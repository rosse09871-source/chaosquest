from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from app.database.models import User, Stage, StageAttempt


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def get_or_create_user(db: Session, username: str) -> User:
    """Finds an existing user by username or creates a new one."""
    clean_username = username.strip()
    user = db.query(User).filter(User.username == clean_username).first()
    if not user:
        user = User(username=clean_username)
        db.add(user)
        db.flush()
    else:
        user.last_active_at = utc_now()
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username.strip()).first()


def upsert_stage(
    db: Session,
    stage_id: str,
    title: str,
    category: str,
    difficulty: str = "Easy",
    base_score: int = 500,
    target_time_seconds: int = 600,
    description: str = "",
) -> Stage:
    """Inserts or updates a stage definition in the database."""
    stage = db.query(Stage).filter(Stage.id == stage_id).first()
    if not stage:
        stage = Stage(
            id=stage_id,
            title=title,
            category=category,
            difficulty=difficulty,
            base_score=base_score,
            target_time_seconds=target_time_seconds,
            description=description,
        )
        db.add(stage)
    else:
        stage.title = title
        stage.category = category
        stage.difficulty = difficulty
        stage.base_score = base_score
        stage.target_time_seconds = target_time_seconds
        stage.description = description
    db.flush()
    return stage


def get_stage(db: Session, stage_id: str) -> Optional[Stage]:
    return db.query(Stage).filter(Stage.id == stage_id).first()


def get_all_stages(db: Session) -> List[Stage]:
    return db.query(Stage).order_by(Stage.id.asc()).all()


def start_stage_attempt(
    db: Session,
    user_id: int,
    stage_id: str,
    session_id: str,
    container_id: Optional[str] = None,
) -> StageAttempt:
    """Registers a new attempt when a user begins a challenge."""
    # Mark any previously open attempt for this user & stage as ABANDONED
    open_attempts = (
        db.query(StageAttempt)
        .filter(
            StageAttempt.user_id == user_id,
            StageAttempt.stage_id == stage_id,
            StageAttempt.status == "IN_PROGRESS",
        )
        .all()
    )
    for prev in open_attempts:
        prev.status = "ABANDONED"
        prev.finished_at = utc_now()

    attempt = StageAttempt(
        user_id=user_id,
        stage_id=stage_id,
        session_id=session_id,
        container_id=container_id,
        status="IN_PROGRESS",
        started_at=utc_now(),
    )
    db.add(attempt)
    db.flush()
    return attempt


def record_hint_used(db: Session, attempt_id: int) -> StageAttempt:
    """Increments hint count for an active attempt."""
    attempt = db.query(StageAttempt).filter(StageAttempt.id == attempt_id).first()
    if not attempt:
        raise ValueError(f"Attempt with ID {attempt_id} not found.")
    attempt.hints_used += 1
    db.flush()
    return attempt


def finish_stage_attempt(
    db: Session, attempt_id: int, success: bool = True
) -> StageAttempt:
    """Completes an attempt, calculates score based on time & hints, and updates user profile."""
    attempt = db.query(StageAttempt).filter(StageAttempt.id == attempt_id).first()
    if not attempt:
        raise ValueError(f"Attempt with ID {attempt_id} not found.")

    attempt.finished_at = utc_now()
    started = attempt.started_at
    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)
    
    elapsed = int((attempt.finished_at - started).total_seconds())
    attempt.elapsed_seconds = max(1, elapsed)

    if success:
        attempt.status = "CLEARED"
        stage = db.query(Stage).filter(Stage.id == attempt.stage_id).first()
        base_score = stage.base_score if stage else 500
        target_time = stage.target_time_seconds if stage else 600

        # Calculation rules:
        # 1. Hint penalty: -50 pts per hint
        hint_penalty = attempt.hints_used * 50
        # 2. Time bonus: if solved faster than target time
        time_bonus = 0
        if attempt.elapsed_seconds < target_time:
            time_bonus = int((target_time - attempt.elapsed_seconds) * 0.5)

        earned = base_score - hint_penalty + time_bonus
        attempt.earned_score = max(50, earned)  # Minimum 50 points for clearing
    else:
        attempt.status = "FAILED"
        attempt.earned_score = 0

    db.flush()
    recalculate_user_total_score(db, attempt.user_id)
    return attempt


def recalculate_user_total_score(db: Session, user_id: int) -> int:
    """
    Computes total score as the sum of the best score for each unique cleared stage.
    """
    subquery = (
        db.query(
            StageAttempt.stage_id,
            func.max(StageAttempt.earned_score).label("best_score"),
        )
        .filter(
            StageAttempt.user_id == user_id,
            StageAttempt.status == "CLEARED",
        )
        .group_by(StageAttempt.stage_id)
        .subquery()
    )

    total = (
        db.query(func.coalesce(func.sum(subquery.c.best_score), 0))
        .scalar()
    )

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.total_score = int(total)
        db.flush()
    return int(total)


def get_global_leaderboard(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """Returns top users ordered by cumulative total score."""
    users = (
        db.query(User)
        .filter(User.total_score > 0)
        .order_by(User.total_score.desc(), User.last_active_at.asc())
        .limit(limit)
        .all()
    )
    result = []
    for rank, u in enumerate(users, start=1):
        cleared_count = (
            db.query(func.count(func.distinct(StageAttempt.stage_id)))
            .filter(
                StageAttempt.user_id == u.id,
                StageAttempt.status == "CLEARED",
            )
            .scalar()
        )
        result.append(
            {
                "rank": rank,
                "username": u.username,
                "total_score": u.total_score,
                "cleared_stages": cleared_count,
                "last_active": u.last_active_at.strftime("%Y-%m-%d %H:%M"),
            }
        )
    return result


def get_stage_leaderboard(
    db: Session, stage_id: str, limit: int = 10
) -> List[Dict[str, Any]]:
    """Returns fastest clear times for a specific stage."""
    # Subquery: fastest clear time per user for this stage
    subquery = (
        db.query(
            StageAttempt.user_id,
            func.min(StageAttempt.elapsed_seconds).label("min_elapsed"),
            func.max(StageAttempt.earned_score).label("max_score"),
        )
        .filter(
            StageAttempt.stage_id == stage_id,
            StageAttempt.status == "CLEARED",
        )
        .group_by(StageAttempt.user_id)
        .subquery()
    )

    query = (
        db.query(User.username, subquery.c.min_elapsed, subquery.c.max_score)
        .join(subquery, User.id == subquery.c.user_id)
        .order_by(subquery.c.min_elapsed.asc(), subquery.c.max_score.desc())
        .limit(limit)
        .all()
    )

    result = []
    for rank, (username, elapsed, score) in enumerate(query, start=1):
        mins, secs = divmod(elapsed or 0, 60)
        result.append(
            {
                "rank": rank,
                "username": username,
                "clear_time": f"{mins:02d}m {secs:02d}s",
                "score": score,
            }
        )
    return result


def get_user_progress_summary(db: Session, user_id: int) -> Dict[str, Any]:
    """Summarizes user's cleared challenges and active stats."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {}

    cleared_attempts = (
        db.query(StageAttempt)
        .filter(
            StageAttempt.user_id == user_id,
            StageAttempt.status == "CLEARED",
        )
        .all()
    )

    cleared_stage_ids = set(a.stage_id for a in cleared_attempts)

    return {
        "user_id": user.id,
        "username": user.username,
        "total_score": user.total_score,
        "cleared_count": len(cleared_stage_ids),
        "cleared_stage_ids": list(cleared_stage_ids),
    }
