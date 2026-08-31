from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box
from app.engine.stage_loader import ChallengeMetadata


console = Console()


def render_banner(username: str = "", score: int = 0, cleared_count: int = 0, docker_active: bool = False):
    """Renders top header banner with user profile and engine status."""
    title_text = Text("🚨 ChaosQuest ", style="bold red")
    title_text.append("| Cloud DevOps Incident Sandbox ", style="bold white")
    if docker_active:
        title_text.append("[🐳 Docker Active]", style="bold green")
    else:
        title_text.append("[⚡ Local Simulation Mode]", style="bold yellow")

    profile_text = Text()
    if username:
        profile_text.append(f"👤 {username} ", style="bold cyan")
        profile_text.append(f"| ⭐ {score} pts ", style="bold yellow")
        profile_text.append(f"| 🏆 Cleared: {cleared_count} ", style="bold green")

    content = Table.grid(expand=True)
    content.add_column(justify="left")
    content.add_column(justify="right")
    content.add_row(title_text, profile_text)

    panel = Panel(
        content,
        box=box.DOUBLE_EDGE,
        border_style="bright_blue",
        padding=(0, 1),
    )
    console.print(panel)


def render_incident_ticket(challenge: ChallengeMetadata, attempt=None):
    """Renders a realistic Incident Response ticket."""
    table = Table(box=box.ROUNDED, border_style="red", expand=True)
    table.add_column("항목", style="bold cyan", width=16)
    table.add_column("상세 내용", style="white")

    severity_color = "bold red" if "CRITICAL" in challenge.incident.severity else "bold yellow"

    table.add_row("인시던트 ID", f"INC-{challenge.id} (Stage {challenge.id})")
    table.add_row("장애 제목", f"[bold white]{challenge.title}[/]")
    table.add_row("카테고리 / 난이도", f"{challenge.category} | {challenge.difficulty}")
    table.add_row("신고 부서", challenge.incident.reporter)
    table.add_row("심각도 (Severity)", f"[{severity_color}]{challenge.incident.severity}[/]")
    table.add_row("증상 (Symptom)", f"[italic bright_white]{challenge.incident.symptom}[/]")
    table.add_row("목표 (Objective)", f"[bold green]{challenge.incident.objective}[/]")

    if attempt and attempt.status == "IN_PROGRESS":
        table.add_row("세션 상태", f"[bold green]🔥 IN PROGRESS[/] (힌트 사용: {attempt.hints_used}개)")

    panel = Panel(
        table,
        title=f"🚨 [bold red]INCIDENT REPORT #{challenge.id}[/]",
        border_style="red",
        padding=(1, 1),
    )
    console.print(panel)


def render_post_mortem(challenge: ChallengeMetadata, solve_time_str: str = "", score: int = 0):
    """Renders an engineer's Post-Mortem retrospective after solving."""
    table = Table(box=box.ROUNDED, border_style="green", expand=True)
    table.add_column("분석 항목", style="bold cyan", width=18)
    table.add_column("기술 분석 및 예방책", style="white")

    table.add_row("🎉 복구 완료", f"[bold green]정상 복구 확인! 소요 시간: {solve_time_str} | 획득 점수: {score} pts[/]")
    table.add_row("📌 근본 원인 (Root Cause)", challenge.post_mortem.root_cause)

    cmd_list = "\n".join([f"  • [bold yellow]{cmd}[/]" for cmd in challenge.post_mortem.key_commands])
    table.add_row("🛠️ 핵심 명령어 & 도구", cmd_list)
    table.add_row("🏢 실무 교훈 & Best Practice", challenge.post_mortem.real_world_lesson)

    panel = Panel(
        table,
        title="📝 [bold green]POST-MORTEM (장애 원인 분석 및 회고 보고서)[/]",
        border_style="green",
        padding=(1, 1),
    )
    console.print(panel)


def render_leaderboard_table(leaderboard_data: list, title: str = "🏆 GLOBAL LEADERBOARD"):
    table = Table(title=f"[bold yellow]{title}[/]", box=box.ROUNDED, border_style="yellow", expand=True)
    table.add_column("순위", justify="center", style="bold cyan", width=8)
    table.add_column("유저 닉네임", style="bold white")
    table.add_column("총 점수", justify="right", style="bold yellow")
    table.add_column("해결한 문제 수", justify="center", style="green")
    table.add_column("최근 활동", justify="center", style="dim")

    if not leaderboard_data:
        table.add_row("-", "아직 등록된 기록이 없습니다. 첫 번째 영웅이 되어보세요!", "-", "-", "-")
    else:
        for item in leaderboard_data:
            rank_str = f"🥇 1위" if item["rank"] == 1 else f"🥈 2위" if item["rank"] == 2 else f"🥉 3위" if item["rank"] == 3 else f"{item['rank']}위"
            table.add_row(
                rank_str,
                item["username"],
                f"{item['total_score']} pts",
                f"{item['cleared_stages']}개",
                item["last_active"],
            )

    console.print(Panel(table, border_style="yellow", padding=(0, 1)))
