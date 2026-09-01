import pytest
from fastapi.testclient import TestClient
from app.web.server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_dashboard_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "ChaosQuest" in response.text
    assert "대시보드" in response.text or "진척" in response.text


def test_challenges_page(client):
    response = client.get("/challenges")
    assert response.status_code == 200
    assert "7대 인프라 도메인" in response.text
    assert "Domain" in response.text


def test_api_catalog(client):
    response = client.get("/api/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "catalog" in data
    assert len(data["catalog"]) == 7


def test_api_leaderboard(client):
    response = client.get("/api/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert "leaderboard" in data


def test_api_user_login(client):
    response = client.post("/api/user/login", json={"username": "web_test_user"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["username"] == "web_test_user"


def test_api_stage_lifecycle(client):
    # 1. Start stage
    res_start = client.post("/api/stages/101-1/start", json={"session_id": "test_web_sess"})
    assert res_start.status_code == 200
    data_start = res_start.json()
    assert data_start["status"] == "started"

    # 2. Ask AI mentor
    res_mentor = client.post(
        "/api/stages/101-1/ask-mentor",
        json={"session_id": "test_web_sess", "question": "디스크가 왜 100%인가요?"},
    )
    assert res_mentor.status_code == 200
    data_mentor = res_mentor.json()
    assert "advice" in data_mentor

    # 3. Request hint
    res_hint = client.post("/api/stages/101-1/hint", json={"session_id": "test_web_sess"})
    assert res_hint.status_code == 200
    data_hint = res_hint.json()
    assert data_hint["status"] in ["unlocked", "no_more_hints"]

    # 4. Verify stage
    res_verify = client.post("/api/stages/101-1/verify", json={"session_id": "test_web_sess"})
    assert res_verify.status_code == 200
