import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base
from app.database import models, crud
from app.engine.stage_loader import load_all_challenge_metadata, sync_challenges_to_db, get_challenge
from app.engine.orchestrator import DockerOrchestrator
from app.engine.watchdog import prune_expired_sessions


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_stage_loader_discovery():
    challenges = load_all_challenge_metadata()
    assert "101" in challenges
    assert "201" in challenges

    meta101 = challenges["101"]
    assert meta101.title == "디스크가 꽉 찼는데 지울 파일이 없어요!"
    assert meta101.category == "Filesystem"
    assert len(meta101.hints) == 3
    assert meta101.incident.severity == "P1-CRITICAL"
    assert meta101.sabotage_script_path is not None
    assert meta101.verify_script_path is not None


def test_sync_challenges_to_db(db_session):
    count = sync_challenges_to_db(db_session)
    assert count >= 2

    stage101 = crud.get_stage(db_session, "101")
    assert stage101 is not None
    assert stage101.title == "디스크가 꽉 찼는데 지울 파일이 없어요!"
    assert stage101.category == "Filesystem"


def test_orchestrator_sandbox_lifecycle():
    orchestrator = DockerOrchestrator()
    res = orchestrator.create_sandbox(stage_id="101", session_id="test_sess_001")
    assert "container_id" in res

    success, msg = orchestrator.verify_sandbox(stage_id="101", session_id="test_sess_001")
    assert isinstance(success, bool)

    destroyed = orchestrator.destroy_sandbox(stage_id="101", session_id="test_sess_001")
    assert destroyed is True


def test_watchdog_prune_expired_sessions(db_session):
    orchestrator = DockerOrchestrator()
    user = crud.get_or_create_user(db_session, "player_one")
    sync_challenges_to_db(db_session)

    # Create an attempt started 40 minutes ago (> 1800s TTL)
    attempt = crud.start_stage_attempt(
        db_session,
        user_id=user.id,
        stage_id="101",
        session_id="expired_sess_99",
    )
    attempt.started_at = datetime.now(timezone.utc) - timedelta(minutes=40)
    db_session.flush()

    # Run watchdog
    res = prune_expired_sessions(db_session, orchestrator, max_ttl_seconds=1800)
    assert res["expired_count"] == 1

    # Verify attempt is now ABANDONED
    updated_attempt = db_session.query(models.StageAttempt).filter(models.StageAttempt.id == attempt.id).first()
    assert updated_attempt.status == "ABANDONED"
