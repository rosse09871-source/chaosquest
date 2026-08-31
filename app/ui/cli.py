import os
import sys
import time
import uuid
import subprocess
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich import box

from app.database.connection import init_db, get_db_session
from app.database import crud, models
from app.engine.stage_loader import load_all_challenge_metadata, sync_challenges_to_db, get_challenge
from app.engine.orchestrator import DockerOrchestrator
from app.ui.components import (
    render_banner,
    render_incident_ticket,
    render_post_mortem,
    render_leaderboard_table,
)

console = Console()
orchestrator = DockerOrchestrator()


class ChaosQuestApp:
    def __init__(self):
        init_db()
        self.session_id = f"sess_{uuid.uuid4().hex[:8]}"
        self.current_user: models.User = None
        self.active_attempts = {}  # stage_id -> StageAttempt ID

    def start(self):
        """Main application entry point."""
        console.clear()
        with get_db_session() as db:
            sync_challenges_to_db(db)

        self._login_prompt()
        self._main_loop()

    def _login_prompt(self):
        render_banner()
        console.print("[bold cyan]👋 환영합니다! ChaosQuest 트러블슈팅 아레나에 오신 것을 환영합니다.[/]\n")
        
        while True:
            username = Prompt.ask("[bold yellow]👉 엔지니어 닉네임을 입력하세요[/]").strip()
            if username:
                break

        with get_db_session() as db:
            self.current_user = crud.get_or_create_user(db, username)

    def _get_user_stats(self):
        with get_db_session() as db:
            return crud.get_user_progress_summary(db, self.current_user.id)

    def _main_loop(self):
        while True:
            console.clear()
            stats = self._get_user_stats()
            render_banner(
                username=stats.get("username", self.current_user.username),
                score=stats.get("total_score", 0),
                cleared_count=stats.get("cleared_count", 0),
            )

            table = Table(box=box.SIMPLE_HEAVY, border_style="bright_blue", expand=True)
            table.add_column("메뉴 번호", justify="center", style="bold cyan", width=12)
            table.add_column("기능", style="bold white")
            table.add_column("설명", style="dim")

            table.add_row("[1]", "📂 스테이지 선택 & 인시던트 해결", "리눅스/네트워크/웹서버 고장 환경에 진입하여 문제 해결")
            table.add_row("[2]", "🏆 명예의 전당 (글로벌 랭킹)", "전체 유저 누적 점수 및 클리어 순위표")
            table.add_row("[3]", "📊 내 전적 및 취약점 분석", "내가 클리어한 문제 및 역량 분석")
            table.add_row("[0]", "🚪 게임 종료", "안전하게 세션 정리 후 종료")

            console.print(Panel(table, title="[bold white]MAIN CONTROL PANEL[/]", border_style="bright_blue"))

            choice = Prompt.ask("\n[bold yellow]선택할 메뉴 번호를 입력하세요[/]", default="1")

            if choice == "1":
                self._stage_selection_menu()
            elif choice == "2":
                self._show_leaderboard()
            elif choice == "3":
                self._show_my_stats()
            elif choice == "0":
                console.print("\n[bold green]👋 수고하셨습니다! 다음에 또 도전하세요.[/]")
                sys.exit(0)

    def _stage_selection_menu(self):
        while True:
            console.clear()
            stats = self._get_user_stats()
            render_banner(username=self.current_user.username, score=stats.get("total_score", 0), cleared_count=stats.get("cleared_count", 0))

            challenges = load_all_challenge_metadata()
            cleared_ids = set(stats.get("cleared_stage_ids", []))

            table = Table(title="[bold white]AVAILABLE INCIDENT STAGES[/]", box=box.ROUNDED, expand=True)
            table.add_column("ID", justify="center", style="bold cyan", width=6)
            table.add_column("상태", justify="center", width=12)
            table.add_column("장애명", style="bold white")
            table.add_column("분야", style="cyan", width=14)
            table.add_column("난이도", style="yellow", width=10)
            table.add_column("기본점수", justify="right", style="green", width=10)

            for sid, ch in challenges.items():
                is_cleared = sid in cleared_ids
                status_badge = "[bold green]✅ CLEARED[/]" if is_cleared else "[bold red]🔥 UNSOLVED[/]"
                table.add_row(
                    ch.id,
                    status_badge,
                    ch.title,
                    ch.category,
                    ch.difficulty,
                    f"{ch.base_score} pts",
                )

            console.print(table)
            console.print("\n[dim]도전할 스테이지 ID (예: 101)를 입력하세요. 메인으로 돌아가려면 0을 입력하세요.[/]")
            choice = Prompt.ask("[bold yellow]스테이지 ID 선택[/]", default="101")

            if choice == "0":
                break
            elif choice in challenges:
                self._play_stage(choice)

    def _play_stage(self, stage_id: str):
        challenge = get_challenge(stage_id)
        if not challenge:
            return

        while True:
            console.clear()
            stats = self._get_user_stats()
            render_banner(username=self.current_user.username, score=stats.get("total_score", 0), cleared_count=stats.get("cleared_count", 0))

            # Fetch active attempt from DB
            attempt = None
            with get_db_session() as db:
                attempt = (
                    db.query(models.StageAttempt)
                    .filter(
                        models.StageAttempt.user_id == self.current_user.id,
                        models.StageAttempt.stage_id == stage_id,
                        models.StageAttempt.status == "IN_PROGRESS",
                    )
                    .first()
                )

            render_incident_ticket(challenge, attempt=attempt)

            menu_table = Table.grid(padding=(0, 2))
            menu_table.add_column(style="bold yellow")
            menu_table.add_column(style="white")

            if not attempt:
                menu_table.add_row("[1]", "🔥 인시던트 시작 (컨테이너 생성 및 고장 주입)")
                menu_table.add_row("[5]", "📝 포스트모템 (장애 분석 보고서 보기)")
                menu_table.add_row("[0]", "🔙 뒤로 가기")
            else:
                menu_table.add_row("[1]", "💻 샌드박스 터미널 내부 접속 (Shell Enter)")
                menu_table.add_row("[2]", f"💡 힌트 보기 ({attempt.hints_used}/{len(challenge.hints)}개 확인됨)")
                menu_table.add_row("[3]", "🔍 복구 검증 및 제출 (Check & Submit)")
                menu_table.add_row("[4]", "⚠️ 인시던트 리셋 / 포기 (Reset Sandbox)")
                menu_table.add_row("[0]", "🔙 뒤로 가기")

            console.print(Panel(menu_table, title="[bold white]ACTION MENU[/]", border_style="yellow"))
            action = Prompt.ask("[bold yellow]실행할 동작을 선택하세요[/]", default="1")

            if action == "0":
                break

            if not attempt:
                if action == "1":
                    self._start_stage_action(stage_id)
                elif action == "5":
                    console.clear()
                    render_post_mortem(challenge)
                    Prompt.ask("\n[bold cyan]엔터를 누르면 돌아갑니다[/]")
            else:
                if action == "1":
                    self._enter_sandbox_action(stage_id, attempt)
                elif action == "2":
                    self._show_hint_action(challenge, attempt)
                elif action == "3":
                    cleared = self._verify_stage_action(challenge, attempt)
                    if cleared:
                        break
                elif action == "4":
                    self._reset_stage_action(stage_id, attempt)

    def _start_stage_action(self, stage_id: str):
        console.print("\n[bold cyan]⚙️ 격리된 샌드박스 컨테이너를 생성하고 고장을 주입하는 중...[/]")
        try:
            sandbox_info = orchestrator.create_sandbox(stage_id, self.session_id)
            with get_db_session() as db:
                attempt = crud.start_stage_attempt(
                    db=db,
                    user_id=self.current_user.id,
                    stage_id=stage_id,
                    session_id=self.session_id,
                    container_id=sandbox_info["container_id"],
                )
            console.print(f"[bold green]✅ 인시던트 환경이 준비되었습니다! (Container: {sandbox_info['container_name']})[/]")
            time.sleep(1.2)
        except Exception as e:
            console.print(f"[bold red]❌ 샌드박스 생성 실패: {e}[/]")
            time.sleep(2)

    def _enter_sandbox_action(self, stage_id: str, attempt):
        cmd = orchestrator.get_shell_exec_command(stage_id, self.session_id)
        console.print(f"\n[bold yellow]👉 샌드박스 쉘에 접속합니다. 조사를 마치고 나오려면 'exit'를 입력하세요.[/]")
        time.sleep(1)
        try:
            subprocess.run(cmd)
        except Exception as e:
            console.print(f"[bold red]접속 오류: {e}[/]")
            Prompt.ask("[dim]엔터를 누르세요...[/]")

    def _show_hint_action(self, challenge, attempt):
        next_hint_idx = attempt.hints_used
        if next_hint_idx >= len(challenge.hints):
            console.print("\n[bold yellow]ℹ️ 이미 모든 힌트를 확인하셨습니다.[/]")
            for h in challenge.hints:
                console.print(f"  • [cyan]힌트 {h.level}[/]: {h.text}")
            Prompt.ask("\n[dim]엔터를 누르면 돌아갑니다...[/]")
            return

        hint_to_unlock = challenge.hints[next_hint_idx]
        confirm = Confirm.ask(f"\n[bold yellow]💡 힌트 {hint_to_unlock.level}번을 확인하시겠습니까? (최종 점수에서 -{hint_to_unlock.cost}점 감점)[/]")
        if confirm:
            with get_db_session() as db:
                crud.record_hint_used(db, attempt.id)
            console.print(f"\n[bold green]💡 힌트 {hint_to_unlock.level}[/]: [bright_white]{hint_to_unlock.text}[/]")
            Prompt.ask("\n[dim]엔터를 누르면 돌아갑니다...[/]")

    def _verify_stage_action(self, challenge, attempt) -> bool:
        console.print("\n[bold cyan]🔍 복구 상태를 자동 채점 및 검증하는 중...[/]")
        time.sleep(1)
        success, msg = orchestrator.verify_sandbox(challenge.id, self.session_id)
        
        console.print(f"\n{msg}\n")
        
        if success:
            with get_db_session() as db:
                finished = crud.finish_stage_attempt(db, attempt.id, success=True)
                mins, secs = divmod(finished.elapsed_seconds, 60)
                solve_time_str = f"{mins:02d}분 {secs:02d}초"

            orchestrator.destroy_sandbox(challenge.id, self.session_id)

            console.clear()
            render_post_mortem(challenge, solve_time_str=solve_time_str, score=finished.earned_score)
            Prompt.ask("\n[bold cyan]축하합니다! 엔터를 누르면 스테이지 목록으로 이동합니다.[/]")
            return True
        else:
            Prompt.ask("[dim]원인을 더 분석한 뒤 다시 채점해보세요. 엔터를 누르세요...[/]")
            return False

    def _reset_stage_action(self, stage_id: str, attempt):
        if Confirm.ask("[bold red]⚠️ 현재 진행 중인 인시던트를 초기화하시겠습니까?[/]"):
            orchestrator.destroy_sandbox(stage_id, self.session_id)
            with get_db_session() as db:
                att = db.query(models.StageAttempt).filter(models.StageAttempt.id == attempt.id).first()
                if att:
                    att.status = "ABANDONED"
            console.print("[bold green]✅ 인시던트 환경이 초기화되었습니다.[/]")
            time.sleep(1)

    def _show_leaderboard(self):
        console.clear()
        with get_db_session() as db:
            data = crud.get_global_leaderboard(db, limit=10)
        render_leaderboard_table(data)
        Prompt.ask("\n[dim]엔터를 누르면 메인 메뉴로 돌아갑니다...[/]")

    def _show_my_stats(self):
        console.clear()
        stats = self._get_user_stats()
        
        table = Table(title="[bold cyan]📊 MY PROGRESS & STATS[/]", box=box.ROUNDED, expand=True)
        table.add_column("지표", style="bold white", width=20)
        table.add_column("기록", style="bold yellow")

        table.add_row("👤 닉네임", stats.get("username", "-"))
        table.add_row("⭐ 누적 총 점수", f"{stats.get('total_score', 0)} pts")
        table.add_row("🏆 해결한 인시던트 수", f"{stats.get('cleared_count', 0)}개")
        table.add_row("클리어한 스테이지 목록", ", ".join(stats.get("cleared_stage_ids", [])) or "없음")

        console.print(Panel(table, border_style="cyan"))
        Prompt.ask("\n[dim]엔터를 누르면 메인 메뉴로 돌아갑니다...[/]")
