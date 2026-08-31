import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.config import DEFAULT_SESSION_TTL_SECONDS
from app.database import models, crud
from app.engine.orchestrator import DockerOrchestrator


def prune_expired_sessions(db: Session, orchestrator: DockerOrchestrator, max_ttl_seconds: int = DEFAULT_SESSION_TTL_SECONDS) -> Dict[str, Any]:
    """
    Finds active stage attempts that have been running longer than max_ttl_seconds,
    cleans up their Docker containers, and marks them as ABANDONED in DB.
    """
    cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=max_ttl_seconds)

    expired_attempts: List[models.StageAttempt] = (
        db.query(models.StageAttempt)
        .filter(
            models.StageAttempt.status == "IN_PROGRESS",
            models.StageAttempt.started_at < cutoff_time,
        )
        .all()
    )

    cleaned_count = 0
    for att in expired_attempts:
        att.status = "ABANDONED"
        att.finished_at = datetime.now(timezone.utc)
        orchestrator.destroy_sandbox(stage_id=att.stage_id, session_id=att.session_id)
        cleaned_count += 1

    db.flush()

    return {
        "expired_count": cleaned_count,
        "pruned_at": datetime.now(timezone.utc).isoformat(),
    }
