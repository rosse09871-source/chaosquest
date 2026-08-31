import pytest
from app.engine.stage_loader import get_challenge, load_all_challenge_metadata
from app.ui.components import (
    render_banner,
    render_incident_ticket,
    render_post_mortem,
    render_leaderboard_table,
)


def test_ui_render_components():
    # Test banner rendering without crashing
    render_banner("tester", 1000, 2)

    # Test ticket rendering
    challenges = load_all_challenge_metadata()
    assert "101" in challenges
    ch101 = challenges["101"]

    render_incident_ticket(ch101)
    render_post_mortem(ch101, solve_time_str="05m 20s", score=480)

    # Test leaderboard rendering
    mock_lb = [
        {"rank": 1, "username": "alice", "total_score": 500, "cleared_stages": 1, "last_active": "2026-08-31"},
    ]
    render_leaderboard_table(mock_lb)
