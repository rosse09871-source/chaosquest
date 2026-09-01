import pytest
from fastapi.testclient import TestClient
from app.web.server import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_dashboard_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "CHAOSQUEST" in response.text.upper()
    assert "DASHBOARD" in response.text.upper() or "INCIDENT" in response.text.upper()


def test_challenges_page(client):
    response = client.get("/challenges")
    assert response.status_code == 200
    assert "CHAOSQUEST" in response.text.upper()
    assert "DOM-0" in response.text or "CHALLENGES" in response.text.upper()


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


def test_community_flow(client):
    # 1. Access community page
    res_comm = client.get("/community")
    assert res_comm.status_code == 200
    assert "커뮤니티" in res_comm.text

    # 2. Create a new post
    res_post = client.post(
        "/api/community/posts",
        json={
            "title": "테스트 게시글입니다",
            "content": "이것은 커뮤니티 테스트 본문입니다.",
            "category": "qna",
            "stage_id": "101-1",
        },
    )
    assert res_post.status_code == 200
    data_post = res_post.json()
    assert data_post["status"] == "success"
    post_id = data_post["post_id"]

    # 3. View post detail page
    res_detail = client.get(f"/community/{post_id}")
    assert res_detail.status_code == 200
    assert "테스트 게시글입니다" in res_detail.text

    # 4. Add a comment
    res_comment = client.post(
        f"/api/community/posts/{post_id}/comments",
        json={"content": "테스트 댓글 내용입니다."},
    )
    assert res_comment.status_code == 200
    data_comment = res_comment.json()
    assert data_comment["status"] == "success"

    # 5. Toggle like
    res_like = client.post(f"/api/community/posts/{post_id}/like")
    assert res_like.status_code == 200
    data_like = res_like.json()
    assert data_like["status"] == "success"
    assert data_like["like_count"] == 1
