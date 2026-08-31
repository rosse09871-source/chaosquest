import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base
from app.database import crud, models


@pytest.fixture
def db_session():
    """Creates an in-memory SQLite database session for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_user_creation(db_session):
    user = crud.get_or_create_user(db_session, "simon_dev")
    assert user.id is not None
    assert user.username == "simon_dev"
    assert user.total_score == 0

    # Getting same user again should return the existing record
    user2 = crud.get_or_create_user(db_session, "simon_dev")
    assert user2.id == user.id


def test_stage_upsert(db_session):
    stage = crud.upsert_stage(
        db_session,
        stage_id="101",
        title="디스크 유령 파일 사건",
        category="Filesystem",
        difficulty="Easy",
        base_score=500,
        target_time_seconds=600,
        description="삭제된 파일이 프로세스에 열려 있어 디스크가 100% 가득 찬 장애",
    )
    assert stage.id == "101"
    assert stage.title == "디스크 유령 파일 사건"

    stages = crud.get_all_stages(db_session)
    assert len(stages) == 1
    assert stages[0].category == "Filesystem"


def test_stage_attempt_lifecycle(db_session):
    user = crud.get_or_create_user(db_session, "cloud_hacker")
    stage = crud.upsert_stage(
        db_session,
        stage_id="101",
        title="디스크 유령 파일 사건",
        category="Filesystem",
        base_score=500,
        target_time_seconds=600,
    )

    # 1. Start attempt
    attempt = crud.start_stage_attempt(
        db_session,
        user_id=user.id,
        stage_id=stage.id,
        session_id="sess_1234",
        container_id="cont_abcd",
    )
    assert attempt.status == "IN_PROGRESS"
    assert attempt.hints_used == 0

    # 2. Use 1 hint
    crud.record_hint_used(db_session, attempt.id)
    assert attempt.hints_used == 1

    # 3. Simulate completion (simulate started 200 seconds ago)
    attempt.started_at = datetime.now(timezone.utc) - timedelta(seconds=200)
    db_session.flush()

    finished_attempt = crud.finish_stage_attempt(db_session, attempt.id, success=True)
    assert finished_attempt.status == "CLEARED"
    assert finished_attempt.elapsed_seconds >= 200
    assert finished_attempt.earned_score > 0
    assert user.total_score == finished_attempt.earned_score


def test_leaderboard_and_user_progress(db_session):
    # Setup 2 users
    user1 = crud.get_or_create_user(db_session, "alice")
    user2 = crud.get_or_create_user(db_session, "bob")

    stage1 = crud.upsert_stage(db_session, "101", "Stage 101", "Filesystem", base_score=500)
    stage2 = crud.upsert_stage(db_session, "201", "Stage 201", "Network", base_score=600)

    # Alice clears 101 fast (100s)
    att1 = crud.start_stage_attempt(db_session, user1.id, "101", "sess_a1")
    att1.started_at = datetime.now(timezone.utc) - timedelta(seconds=100)
    crud.finish_stage_attempt(db_session, att1.id, success=True)

    # Bob clears 101 slower (300s)
    att2 = crud.start_stage_attempt(db_session, user2.id, "101", "sess_b1")
    att2.started_at = datetime.now(timezone.utc) - timedelta(seconds=300)
    crud.finish_stage_attempt(db_session, att2.id, success=True)

    # Stage leaderboard for 101
    stage_lb = crud.get_stage_leaderboard(db_session, "101")
    assert len(stage_lb) == 2
    assert stage_lb[0]["username"] == "alice"
    assert stage_lb[1]["username"] == "bob"

    # Global leaderboard
    global_lb = crud.get_global_leaderboard(db_session)
    assert len(global_lb) == 2
    assert global_lb[0]["username"] == "alice"

    # User progress summary
    summary = crud.get_user_progress_summary(db_session, user1.id)
    assert summary["cleared_count"] == 1
    assert "101" in summary["cleared_stage_ids"]
