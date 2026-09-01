import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from app.engine.stage_loader import ChallengeMetadata


class AIMentor:
    """
    AI SRE Senior Mentor (김수석)
    Inspects live container state (processes, ports, disks, logs) and provides real-time mentoring.
    """

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def capture_diagnostics(self, container: Any) -> Dict[str, str]:
        """Collects a safe live system diagnostic snapshot from the container."""
        if not container or getattr(container, "status", None) != "running":
            return {
                "processes": "Container not running or in mock mode.",
                "disks": "N/A",
                "network": "N/A",
                "logs": "N/A",
                "open_files": "N/A",
            }

        def run_cmd(cmd_str: str) -> str:
            try:
                res = container.exec_run(["bash", "-c", cmd_str])
                return res.output.decode("utf-8", errors="ignore").strip()
            except Exception as e:
                return f"Error running '{cmd_str}': {e}"

        return {
            "processes": run_cmd("ps -eo pid,user,%cpu,%mem,stat,args --sort=-%cpu | head -n 25"),
            "disks": run_cmd("df -h / && echo '=== INODES ===' && df -i /"),
            "network": run_cmd("ss -tlpn 2>/dev/null || netstat -tlpn 2>/dev/null || true"),
            "logs": run_cmd("tail -n 20 /var/log/nginx/error.log 2>/dev/null || tail -n 20 /var/log/payment_service.log 2>/dev/null || tail -n 15 /var/log/syslog 2>/dev/null || true"),
            "open_files": run_cmd("lsof +L1 2>/dev/null | head -n 15 || true"),
        }

    def consult(
        self,
        challenge: ChallengeMetadata,
        diagnostics: Dict[str, str],
        user_question: Optional[str] = None,
    ) -> str:
        """Generates real-time mentoring guidance via LLM or rule-based fallback."""
        if self.gemini_api_key:
            try:
                return self._call_gemini(challenge, diagnostics, user_question)
            except Exception as e:
                pass

        if self.openai_api_key:
            try:
                return self._call_openai(challenge, diagnostics, user_question)
            except Exception as e:
                pass

        return self._heuristic_mentor(challenge, diagnostics, user_question)

    def _call_gemini(self, challenge: ChallengeMetadata, diagnostics: Dict[str, str], user_question: Optional[str]) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_api_key}"
        prompt = self._build_prompt(challenge, diagnostics, user_question)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 800},
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    def _call_openai(self, challenge: ChallengeMetadata, diagnostics: Dict[str, str], user_question: Optional[str]) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        prompt = self._build_prompt(challenge, diagnostics, user_question)
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are 'Kim Soo-seok' (김수석), a veteran Senior SRE Lead mentor. Speak in friendly, professional Korean."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 800,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.openai_api_key}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()

    def _build_prompt(self, challenge: ChallengeMetadata, diagnostics: Dict[str, str], user_question: Optional[str]) -> str:
        q_text = user_question.strip() if user_question else "현재 시스템 상태를 진단하고 다음 트러블슈팅 방향을 짚어주세요."
        return f"""
당신은 15년 차 시니어 SRE 리드 '김수석'입니다. 주니어 엔지니어(플레이어)가 현재 장애를 해결하는 것을 1:1로 지도하고 있습니다.
정답 명령어(예: kill -9 <PID>)를 그대로 떠먹여 주지 말고, 사수답게 관찰된 시스템 지표를 근거로 논리적 조사 단계를 안내하세요.

[인시던트 정보]
- ID: {challenge.id} ({challenge.title})
- 카테고리: {challenge.category} (난이도: {challenge.difficulty})
- 고장 증상: {challenge.incident.symptom}
- 복구 목표: {challenge.incident.objective}

[실시간 컨테이너 상태 스냅샷]
1. 프로세스 목록 (ps aux):
{diagnostics.get('processes', 'N/A')}

2. 디스크 및 Inode 상태 (df -h / df -i):
{diagnostics.get('disks', 'N/A')}

3. 네트워크 리슨 포트 (ss/netstat):
{diagnostics.get('network', 'N/A')}

4. 열려있는 삭제 파일 (lsof +L1):
{diagnostics.get('open_files', 'N/A')}

5. 최근 에러 로그:
{diagnostics.get('logs', 'N/A')}

[후배 엔지니어의 질문/요청]
"{q_text}"

위 시스템 상태를 기반으로 사수로서 따뜻하고 날카로운 실무 조언을 3~4문단으로 작성하세요. (존댓말 사용)
"""

    def _heuristic_mentor(self, challenge: ChallengeMetadata, diagnostics: Dict[str, str], user_question: Optional[str]) -> str:
        """Rule-based expert SRE diagnostic response when no external API key is configured."""
        cid = challenge.id
        q = (user_question or "").lower()

        # Domain 1: Filesystem (101, 102, 103)
        if cid.startswith("101"):
            open_f = diagnostics.get("open_files", "")
            if "deleted" in open_f or "app_ghost" in open_f or "dump" in open_f:
                return (
                    "👨‍🏫 [김수석의 실시간 진단]\n\n"
                    "음, 지금 컨테이너의 파일 디스크립터 상태를 봤는데 `(deleted)` 표시가 붙은 유령 파일이 아직 프로세스에 물려있네!\n\n"
                    "1. 리눅스는 `rm`으로 파일을 지워도 실행 중인 프로세스가 해당 파일을 열고 있으면 디스크 공간을 절대 반환하지 않아.\n"
                    "2. `lsof +L1` 결과에서 해당 파일을 열고 있는 PID를 확인해봐.\n"
                    "3. 그 프로세스를 `kill -9 <PID>`(또는 `pkill`)로 안전하게 종료시키면 커널이 디스크 공간을 즉시 회수할 거야. 한번 해볼래?"
                )
            else:
                return (
                    "👨‍🏫 [김수석의 실시간 진단]\n\n"
                    "좋아! 열려있던 유령 파일 디스크립터는 깔끔하게 정리된 것 같아.\n\n"
                    "이제 `ps aux`로 데몬이 완전히 내려갔는지 확인하고, 메뉴에서 **`[3] 복구 검증 및 제출`**을 눌러서 결과를 확인해보자!"
                )

        # Domain 2: Process & Ports (201, 202, 203)
        elif cid.startswith("201"):
            net = diagnostics.get("network", "")
            if "80" in net or "8080" in net or "rogue" in net or "immortal" in diagnostics.get("processes", ""):
                return (
                    "👨‍🏫 [김수석의 실시간 진단]\n\n"
                    "포트 충돌 상황이네! 지금 포트 점유 상태(`ss -tlpn`)를 보니까 비인가 좀비 프로세스가 포트를 쥐고 있어.\n\n"
                    "1. `ss -tlpn` 또는 `netstat -tlpn`으로 80번(또는 8080) 포트를 선점하고 있는 프로세스의 PID를 확인해봐.\n"
                    "2. 해당 프로세스를 `kill -9`로 종료한 다음, 정상 서비스 기동 스크립트(`/usr/local/bin/start_*.sh`)를 실행해서 포트를 다시 열어줘야 해!"
                )
            else:
                return (
                    "👨‍🏫 [김수석의 실시간 진단]\n\n"
                    "좀비 프로세스는 잘 사살된 것 같네! 이제 정상 서비스가 200 OK 응답을 주는지 `curl http://127.0.0.1/`로 테스트해보고 제출을 눌러봐."
                )

        # Domain 3: Network (301, 302, 303)
        elif cid.startswith("301"):
            return (
                "👨‍🏫 [김수석의 실시간 진단]\n\n"
                "DNS 해석에 문제가 생겼을 때는 두 곳을 먼저 확인해야 해: `/etc/hosts`와 `/etc/resolv.conf`!\n\n"
                "1. `cat /etc/resolv.conf`를 열어서 유효한 네임서버(예: `8.8.8.8` 또는 `1.1.1.1`)가 제대로 등록되어 있는지 확인해봐.\n"
                "2. 만약 가짜 IP가 적혀있다면 `echo 'nameserver 8.8.8.8' > /etc/resolv.conf`로 공용 DNS를 등록해주면 바로 해결될 거야."
            )

        # Domain 4: Nginx (401, 402, 403)
        elif cid.startswith("401"):
            return (
                "👨‍🏫 [김수석의 실시간 진단]\n\n"
                "Nginx 502 Bad Gateway는 앞단 프록시(Nginx)와 뒷단 백엔드 앱 간의 통신이 끊겼을 때 발생해.\n\n"
                "1. 먼저 `cat /var/log/nginx/error.log`를 열어서 upstream 연결 실패 포트나 소켓 경로를 확인해봐.\n"
                "2. 백엔드가 실제로 몇 번 포트에서 돌고 있는지 `ss -tlpn`으로 확인하고, `/etc/nginx/sites-available/default`의 `proxy_pass` 포트를 일치시킨 뒤 `nginx -s reload`를 실행해봐!"
            )

        # General Fallback
        return (
            f"👨‍🏫 [김수석의 실시간 진단]\n\n"
            f"현재 다루고 있는 인시던트는 **'{challenge.title}'**이네.\n\n"
            f"증상: {challenge.incident.symptom}\n\n"
            "💡 **사수의 3단계 조언**:\n"
            "1. 먼저 샌드박스 쉘에 들어가서 관련 로그나 설정 파일(`/etc/`, `/var/log/`)을 직접 열어봐.\n"
            "2. 에러 메시지에 나오는 핵심 키워드(권한, 포트, 파일명)를 기반으로 명령어를 실행해봐.\n"
            "3. 작업이 끝나면 `exit`로 나와서 [3]번 메뉴로 채점을 요청해봐!"
        )


ai_mentor = AIMentor()
