import os
import subprocess
import time
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
import shutil
import docker
from docker.errors import DockerException, NotFound, APIError
from app.config import DEFAULT_CONTAINER_MEM_LIMIT, DEFAULT_CONTAINER_CPU_LIMIT
from app.engine.stage_loader import get_challenge


class SandboxError(Exception):
    pass


def find_docker_executable() -> Optional[str]:
    """Finds the docker executable path across standard system and macOS Docker Desktop locations."""
    found = shutil.which("docker")
    if found:
        return found

    candidate_paths = [
        os.path.expanduser("~/.docker/bin/docker"),
        "/usr/local/bin/docker",
        "/opt/homebrew/bin/docker",
        "/Applications/Docker.app/Contents/Resources/bin/docker",
    ]
    for p in candidate_paths:
        if os.path.exists(p) and os.access(p, os.X_OK):
            parent_dir = str(Path(p).parent)
            if parent_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = f"{parent_dir}:{os.environ.get('PATH', '')}"
            return p

    return None


class DockerOrchestrator:
    def __init__(self, base_image: str = "chaosquest:base"):
        self.base_image = base_image
        self._client: Optional[docker.DockerClient] = None
        self._docker_available = False
        self.docker_bin = find_docker_executable()
        self._init_client()

    def _init_client(self):
        try:
            self._client = docker.from_env()
            self._client.ping()
            self._docker_available = True
        except Exception:
            self._client = None
            self._docker_available = False

    @property
    def is_docker_available(self) -> bool:
        return self._docker_available

    def _get_effective_image(self) -> str:
        """Returns chaosquest:base if present locally, otherwise falls back to ubuntu:22.04."""
        if not self._client or not self._docker_available:
            return self.base_image
        try:
            self._client.images.get(self.base_image)
            return self.base_image
        except Exception:
            return "ubuntu:22.04"

    def _get_container_name(self, stage_id: str, session_id: str) -> str:
        return f"chaos_{stage_id}_{session_id}"

    def create_sandbox(self, stage_id: str, session_id: str) -> Dict[str, Any]:
        """
        Creates and starts an isolated Docker sandbox container for the given stage and session,
        then injects the sabotage failure into the container.
        """
        challenge = get_challenge(stage_id)
        if not challenge:
            raise SandboxError(f"Stage '{stage_id}' metadata not found.")

        container_name = self._get_container_name(stage_id, session_id)

        if not self._docker_available or not self._client:
            # Fallback/Dry-run simulation mode when Docker daemon is not active
            return {
                "container_id": f"mock_{container_name}",
                "container_name": container_name,
                "status": "running_mock",
                "mock": True,
            }

        # 1. Clean up existing container with the same name if any
        self.destroy_sandbox(stage_id=stage_id, session_id=session_id)

        # 2. Spawn container
        nano_cpus = int(DEFAULT_CONTAINER_CPU_LIMIT * 1_000_000_000)
        labels = {
            "chaosquest": "true",
            "stage_id": stage_id,
            "session_id": session_id,
            "created_at": str(time.time()),
        }

        target_image = self._get_effective_image()

        try:
            container = self._client.containers.run(
                image=target_image,
                name=container_name,
                hostname=f"chaos-{stage_id}",
                detach=True,
                tty=True,
                stdin_open=True,
                mem_limit=DEFAULT_CONTAINER_MEM_LIMIT,
                nano_cpus=nano_cpus,
                labels=labels,
                command="/bin/bash",
            )
        except DockerException as e:
            raise SandboxError(f"Failed to launch Docker container: {e}")

        # 3. Inject sabotage script inside container
        if challenge.sabotage_script_path and os.path.exists(challenge.sabotage_script_path):
            with open(challenge.sabotage_script_path, "r", encoding="utf-8") as f:
                sabotage_content = f.read()

            exec_cmd = ["bash", "-c", sabotage_content]
            exec_res = container.exec_run(exec_cmd)
            if exec_res.exit_code != 0:
                print(f"Warning: Sabotage script warning/non-zero: {exec_res.output.decode('utf-8', errors='ignore')}")

        return {
            "container_id": container.id,
            "container_name": container_name,
            "status": container.status,
            "mock": False,
        }

    def verify_sandbox(self, stage_id: str, session_id: str) -> Tuple[bool, str]:
        """
        Executes verify.sh inside the sandbox container and returns (success, message).
        """
        challenge = get_challenge(stage_id)
        if not challenge:
            return False, f"Stage '{stage_id}' not found."

        if not self._docker_available or not self._client:
            return True, "[Mock Mode] Verification passed simulated."

        container_name = self._get_container_name(stage_id, session_id)
        try:
            container = self._client.containers.get(container_name)
        except NotFound:
            return False, f"Container '{container_name}' is not running."
        except DockerException as e:
            return False, f"Docker error: {e}"

        if not challenge.verify_script_path or not os.path.exists(challenge.verify_script_path):
            return False, "Verification script missing."

        with open(challenge.verify_script_path, "r", encoding="utf-8") as f:
            verify_content = f.read()

        exec_res = container.exec_run(["bash", "-c", verify_content])
        output = exec_res.output.decode("utf-8", errors="ignore").strip()
        is_success = (exec_res.exit_code == 0)

        return is_success, output

    def is_container_running(self, stage_id: str, session_id: str) -> bool:
        """Checks if the container exists and is running."""
        if not self._docker_available or not self._client:
            return False
        container_name = self._get_container_name(stage_id, session_id)
        try:
            container = self._client.containers.get(container_name)
            return container.status == "running"
        except (NotFound, DockerException):
            return False

    def ensure_sandbox_running(self, stage_id: str, session_id: str) -> Dict[str, Any]:
        """Ensures that the sandbox container is up and running. If missing, spawns it."""
        if self.is_container_running(stage_id, session_id):
            container_name = self._get_container_name(stage_id, session_id)
            container = self._client.containers.get(container_name)
            return {
                "container_id": container.id,
                "container_name": container_name,
                "status": container.status,
                "mock": False,
            }
        return self.create_sandbox(stage_id, session_id)

    def destroy_sandbox(self, stage_id: str, session_id: str) -> bool:
        """Stops and removes the container."""
        container_name = self._get_container_name(stage_id, session_id)
        if not self._docker_available or not self._client:
            return True

        try:
            container = self._client.containers.get(container_name)
            container.stop(timeout=2)
            container.remove(force=True)
            return True
        except NotFound:
            return False
        except DockerException:
            return False

    def get_shell_exec_command(self, stage_id: str, session_id: str) -> list:
        docker_bin = find_docker_executable()
        if not self._docker_available or not self._client or not docker_bin:
            sandbox_dir = Path("data/sandboxes") / f"chaos_{stage_id}_{session_id}"
            sandbox_dir.mkdir(parents=True, exist_ok=True)
            return [
                "bash",
                "-c",
                f"echo -e '\\033[1;33m[⚠️ 로컬 시뮬레이션 모드]\\033[0m Docker CLI를 찾을 수 없어 로컬 시뮬레이션 쉘로 진입합니다.\\n👉 샌드박스 경로: {sandbox_dir}\\n👉 조사를 마치고 메인 화면으로 돌아가려면 exit 를 입력하세요.\\n'; cd {sandbox_dir} && PS1='(chaos-{stage_id}) \\w \\$ ' bash --norc",
            ]
        container_name = self._get_container_name(stage_id, session_id)
        return [docker_bin, "exec", "-it", container_name, "bash"]
