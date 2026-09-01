import pytest
from app.engine.stage_loader import get_challenge
from app.engine.ai_mentor import AIMentor
from app.ui.components import render_ai_mentor_dialogue


def test_ai_mentor_heuristic_filesystem():
    mentor = AIMentor()
    ch101 = get_challenge("101-1")
    assert ch101 is not None

    # Test with unlinked open file diagnostics
    mock_diag = {
        "processes": "root 142 0.0 0.1 python3 /usr/local/bin/legacy_logger.py",
        "disks": "Filesystem 20G 20G 0 100% /",
        "network": "",
        "open_files": "python3 142 root 3w REG 8,1 15728640 0 /var/log/app_ghost.log (deleted)",
        "logs": "",
    }

    advice = mentor.consult(ch101, mock_diag, user_question="디스크가 왜 안 줄어들죠?")
    assert "김수석" in advice
    assert "유령 파일" in advice or "파일 디스크립터" in advice or "lsof" in advice


def test_ai_mentor_heuristic_ports():
    mentor = AIMentor()
    ch201 = get_challenge("201-1")
    assert ch201 is not None

    mock_diag = {
        "processes": "root 89 0.0 0.1 python3 /usr/local/bin/rogue_occupier.py",
        "disks": "Filesystem 20G 5G 15G 25% /",
        "network": "LISTEN 0 128 0.0.0.0:80 0.0.0.0:* users:(('python3',pid=89,fd=3))",
        "open_files": "",
        "logs": "",
    }

    advice = mentor.consult(ch201, mock_diag, user_question="80번 포트에 서비스가 안 떠요")
    assert "김수석" in advice
    assert "포트" in advice or "좀비" in advice


def test_render_ai_mentor_ui():
    render_ai_mentor_dialogue(
        user_question="포트가 왜 안 열릴까요?",
        mentor_advice="80번 포트를 점유하고 있는 rogue_occupier 프로세스를 kill -9로 사살해보세요!",
    )
