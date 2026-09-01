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
    assert len(data["catalog"]) >= 7


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

    # 3. View post detail page and my posts
    res_detail = client.get(f"/community/{post_id}")
    assert res_detail.status_code == 200
    assert "테스트 게시글입니다" in res_detail.text

    res_mine = client.get("/community?mine=true")
    assert res_mine.status_code == 200
    assert "테스트 게시글입니다" in res_mine.text

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

    # 6. Delete comment
    comment_id = data_comment["comment_id"]
    res_del_comment = client.delete(f"/api/community/comments/{comment_id}")
    assert res_del_comment.status_code == 200

    # 7. Delete post
    res_del_post = client.delete(f"/api/community/posts/{post_id}")
    assert res_del_post.status_code == 200


def test_admin_user_management(client):
    # 1. Register regular user
    res_reg = client.post("/api/user/login", json={"username": "regular_engineer"})
    assert res_reg.status_code == 200
    res_unauth = client.get("/api/admin/users")
    assert res_unauth.status_code == 403

    # 2. Try to claim 'daisy' with wrong/no password -> 400 Bad Request
    res_fail = client.post("/api/user/login", json={"username": "daisy", "password": "wrong_password"})
    assert res_fail.status_code == 400
    assert res_fail.json()["detail"] == "비밀번호가 올바르지 않습니다."

    # 3. Login as admin 'daisy' with correct password -> 200 OK
    res_login = client.post("/api/user/login", json={"username": "daisy", "password": "daisy2026!"})
    assert res_login.status_code == 200
    assert res_login.json()["is_admin"] is True

    # 4. Fetch admin user list
    res_users = client.get("/api/admin/users")
    assert res_users.status_code == 200
    data = res_users.json()
    assert "users" in data
    assert any(u["username"] == "regular_engineer" for u in data["users"])

    # Find regular_engineer ID
    target = next(u for u in data["users"] if u["username"] == "regular_engineer")
    target_id = target["id"]

    # 5. Admin cannot delete daisy herself -> 400 Bad Request
    daisy_user = next(u for u in data["users"] if u["username"] == "daisy")
    res_del_daisy = client.delete(f"/api/admin/users/{daisy_user['id']}")
    assert res_del_daisy.status_code == 400

    # 6. Admin deletes regular_engineer -> 200 OK
    res_del = client.delete(f"/api/admin/users/{target_id}")
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "deleted"

    # Verify user is gone
    res_users_after = client.get("/api/admin/users")
    assert not any(u["id"] == target_id for u in res_users_after.json()["users"])
