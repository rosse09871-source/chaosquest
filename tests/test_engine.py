import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base
from app.database import models, crud
from app.engine.stage_loader import (
    load_all_challenge_metadata,
    sync_challenges_to_db,
    get_challenge,
    get_domain_catalog,
)
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
    assert "101-1" in challenges
    assert "201-1" in challenges
    assert "701-1" in challenges
    assert len(challenges) >= 15

    meta101 = challenges["101-1"]
    assert meta101.title == "단일 데몬의 삭제된 로그 파일 디스크립터 회수"
    assert meta101.category == "Filesystem"
    assert len(meta101.hints) == 3
    assert meta101.incident.severity == "P1-CRITICAL"


def test_domain_catalog():
    catalog = get_domain_catalog()
    assert len(catalog) == 7  # All 7 domains present
    assert 1 in catalog  # Domain 1: Filesystem
    assert 7 in catalog  # Domain 7: AWS Cloud & Security
    assert "101" in catalog[1]["tracks"]


def test_sync_challenges_to_db(db_session):
    count = sync_challenges_to_db(db_session)
    assert count >= 15

    stage101 = crud.get_stage(db_session, "101-1")
    assert stage101 is not None
    assert "단일 데몬" in stage101.title
    assert stage101.category == "Filesystem"


def test_orchestrator_sandbox_lifecycle():
    orchestrator = DockerOrchestrator()
    res = orchestrator.create_sandbox(stage_id="101-1", session_id="test_sess_001")
    assert "container_id" in res

    success, msg = orchestrator.verify_sandbox(stage_id="101-1", session_id="test_sess_001")
    assert isinstance(success, bool)

    destroyed = orchestrator.destroy_sandbox(stage_id="101-1", session_id="test_sess_001")
    assert destroyed is True


def test_watchdog_prune_expired_sessions(db_session):
    orchestrator = DockerOrchestrator()
    user = crud.get_or_create_user(db_session, "player_one")
    sync_challenges_to_db(db_session)

    attempt = crud.start_stage_attempt(
        db_session,
        user_id=user.id,
        stage_id="101-1",
        session_id="expired_sess_99",
    )
    attempt.started_at = datetime.now(timezone.utc) - timedelta(minutes=40)
    db_session.flush()

    res = prune_expired_sessions(db_session, orchestrator, max_ttl_seconds=1800)
    assert res["expired_count"] == 1

    updated_attempt = db_session.query(models.StageAttempt).filter(models.StageAttempt.id == attempt.id).first()
    assert updated_attempt.status == "ABANDONED"
