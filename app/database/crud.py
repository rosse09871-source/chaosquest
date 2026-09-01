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
    is_admin_user = clean_username.lower() in ["daisy", "admin", "sre_senior_kim"]
    if not user:
        user = User(username=clean_username, is_admin=is_admin_user)
        db.add(user)
        db.flush()
    else:
        if is_admin_user and not user.is_admin:
            user.is_admin = True
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
        # 1. Hint penalty: Levels 1-3 free (0 pts), Level 4 (-50 pts), Level 5 (-100 pts)
        hint_penalty = 0
        if attempt.hints_used == 4:
            hint_penalty = 50
        elif attempt.hints_used >= 5:
            hint_penalty = 150

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


# -------------------------------------------------------------
# Community Forum CRUD
# -------------------------------------------------------------
from app.database.models import Post, Comment, PostLike


def create_post(
    db: Session,
    user_id: int,
    title: str,
    content: str,
    category: str = "general",
    stage_id: Optional[str] = None,
) -> Post:
    """Creates a new community post."""
    post = Post(
        user_id=user_id,
        title=title.strip(),
        content=content.strip(),
        category=category.strip(),
        stage_id=stage_id.strip() if stage_id else None,
    )
    db.add(post)
    db.flush()
    return post


from sqlalchemy.orm import joinedload


def get_posts(
    db: Session,
    category: Optional[str] = None,
    stage_id: Optional[str] = None,
    user_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = "latest",
    limit: int = 50,
) -> List[Post]:
    """Fetches community posts with filtering and sorting."""
    query = db.query(Post).options(joinedload(Post.user), joinedload(Post.comments))
    if category and category != "all":
        query = query.filter(Post.category == category)
    if stage_id:
        query = query.filter(Post.stage_id == stage_id)
    if user_id is not None:
        query = query.filter(Post.user_id == user_id)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (Post.title.ilike(search_pattern)) | (Post.content.ilike(search_pattern))
        )

    if sort_by == "popular":
        query = query.order_by(Post.like_count.desc(), Post.created_at.desc())
    else:
        query = query.order_by(Post.created_at.desc())

    return query.limit(limit).all()


def get_post_by_id(db: Session, post_id: int, increment_views: bool = True) -> Optional[Post]:
    """Fetches a single post by ID, optionally incrementing view count."""
    post = (
        db.query(Post)
        .options(
            joinedload(Post.user),
            joinedload(Post.comments).joinedload(Comment.user),
            joinedload(Post.likes),
        )
        .filter(Post.id == post_id)
        .first()
    )
    if post and increment_views:
        post.views += 1
        db.flush()
    return post


def add_comment(db: Session, post_id: int, user_id: int, content: str) -> Comment:
    """Adds a new comment to a post."""
    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=content.strip(),
    )
    db.add(comment)
    db.flush()
    return comment


def toggle_post_like(db: Session, post_id: int, user_id: int) -> Dict[str, Any]:
    """Toggles like on a post for a user."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return {"status": "not_found", "liked": False, "like_count": 0}

    existing_like = (
        db.query(PostLike)
        .filter(PostLike.post_id == post_id, PostLike.user_id == user_id)
        .first()
    )

    if existing_like:
        db.delete(existing_like)
        post.like_count = max(0, post.like_count - 1)
        liked = False
    else:
        new_like = PostLike(post_id=post_id, user_id=user_id)
        db.add(new_like)
        post.like_count += 1
        liked = True

    db.flush()
    return {"status": "success", "liked": liked, "like_count": post.like_count}


def delete_post(db: Session, post_id: int, user_id: int, is_admin: bool = False) -> bool:
    """Deletes a post if the requesting user is the author or an admin."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return False
    if post.user_id != user_id and not is_admin:
        return False
    db.delete(post)
    db.flush()
    return True


def delete_comment(db: Session, comment_id: int, user_id: int, is_admin: bool = False) -> bool:
    """Deletes a comment if the requesting user is the author or an admin."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return False
    if comment.user_id != user_id and not is_admin:
        return False
    db.delete(comment)
    db.flush()
    return True


def seed_initial_community_posts(db: Session):
    """Seeds rich initial posts so the community is engaging from the start."""
    if db.query(Post).count() > 0:
        return

    admin = get_or_create_user(db, "SRE_Senior_Kim")
    admin.total_score = 5400
    user2 = get_or_create_user(db, "cloud_ninja")
    user2.total_score = 3850
    user3 = get_or_create_user(db, "devops_pro")
    user3.total_score = 2900

    p1 = create_post(
        db=db,
        user_id=admin.id,
        category="writeup",
        stage_id="101-1",
        title="[Write-up] INC-101 유령 파일 누수 1초 만에 잡는 awk + kill 원라이너",
        content=(
            "안녕하세요! SRE 김수석입니다.\n\n"
            "INC-101 문제에서 `rm`으로 로그 파일을 지웠는데도 디스크 사용량이 100%로 남아있는 이유는, "
            "실행 중인 데몬 프로세스가 파일 디스크립터(FD)를 여전히 잡고 있기 때문입니다.\n\n"
            "### 핵심 원라이너:\n"
            "```bash\n"
            "lsof +L1 | awk '/deleted/ {print $2}' | xargs -r kill -9\n"
            "```\n\n"
            "위 명령어를 실행하면 `(deleted)` 상태의 unlinked 파일을 물고 있는 모든 PID를 즉시 안전하게 사살하여 디스크 공간을 커널에 반환합니다!"
        ),
    )
    p1.views = 128
    p1.like_count = 19

    p2 = create_post(
        db=db,
        user_id=user2.id,
        category="war_story",
        title="새벽 3시에 배포하다 Redis OOM 터졌던 실제 프로덕션 장애 회고",
        content=(
            "현업에서 캐시 키에 TTL(만료 시간)을 안 걸어두고 대규모 프로모션을 진행했다가 "
            "새벽에 메모리가 99.8%까지 차면서 전체 결제 서버가 셧다운되었던 뼈아픈 경험입니다...\n\n"
            "`maxmemory-policy noeviction` 상태에서는 새 쓰기 요청이 전부 에러를 뱉게 되니, "
            "반드시 `volatile-lru` 또는 `allkeys-lru` 설정을 기본으로 점검해야 합니다. "
            "ChaosQuest 602번 트랙 풀면서 그 악몽이 다시 떠올랐네요 ㅎㅎ"
        ),
    )
    p2.views = 254
    p2.like_count = 32

    p3 = create_post(
        db=db,
        user_id=user3.id,
        category="qna",
        stage_id="401-1",
        title="INC-401 Nginx 502 에러 해결할 때 unix domain socket 권한 질문입니다",
        content=(
            "Nginx upstream을 127.0.0.1:8000 포트 대신 `/var/run/app.sock` 유닉스 도메인 소켓으로 연결할 때 "
            "502 Bad Gateway가 계속 뜹니다. `www-data` 사용자의 소켓 파일 읽기/쓰기 권한 문제일까요? "
            "다른 분들은 어떻게 디버깅하셨는지 궁금합니다!"
        ),
    )
    p3.views = 89
    p3.like_count = 7

    add_comment(
        db=db,
        post_id=p3.id,
        user_id=admin.id,
        content="맞습니다! `ls -la /var/run/app.sock`로 소유자와 권한(0660 또는 0666)을 확인하고, `chmod 666 /var/run/app.sock` 또는 `chown www-data:www-data`로 Nginx 워커 프로세스가 소켓에 접근할 수 있도록 열어주면 즉시 해결됩니다.",
    )
    db.commit()
