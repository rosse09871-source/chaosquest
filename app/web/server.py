import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException, Depends, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.config import BASE_DIR
from app.database.connection import init_db, get_db_session
from app.database import crud, models
from app.engine.stage_loader import (
    load_all_challenge_metadata,
    sync_challenges_to_db,
    get_challenge,
    get_domain_catalog,
)
from app.engine.orchestrator import DockerOrchestrator
from app.engine.ai_mentor import ai_mentor
from app.engine.watchdog import prune_expired_sessions

# Initialize App & Services
app = FastAPI(title="ChaosQuest Modern Web Arena", version="2.0.0")
orchestrator = DockerOrchestrator()

WEB_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def on_startup():
    init_db()
    with get_db_session() as db:
        sync_challenges_to_db(db)
        try:
            crud.seed_initial_community_posts(db)
        except Exception:
            pass
        try:
            prune_expired_sessions(db, orchestrator)
        except Exception:
            pass


# -------------------------------------------------------------
# Dependency: Current User Resolution from Cookie
# -------------------------------------------------------------
def get_current_user_name(request: Request) -> str:
    return request.cookies.get("chaos_username", "Guest_Engineer")


def get_current_user_obj(username: str = Depends(get_current_user_name)):
    with get_db_session() as db:
        user = crud.get_or_create_user(db, username)
        return {"id": user.id, "username": user.username, "total_score": user.total_score}


DOMAIN_ICONS = {
    1: "fa-solid fa-hard-drive",
    2: "fa-solid fa-microchip",
    3: "fa-solid fa-network-wired",
    4: "fa-solid fa-globe",
    5: "fa-brands fa-docker",
    6: "fa-solid fa-database",
    7: "fa-solid fa-shield-halved",
}
DOMAIN_EN_NAMES = {
    1: "Storage & Filesystem",
    2: "Process & OS Resources",
    3: "Networking & DNS",
    4: "Web Servers & Reverse Proxy",
    5: "Docker & Container Runtime",
    6: "Database & Cache Engine",
    7: "Cloud & Infrastructure Security",
}


# -------------------------------------------------------------
# HTML Page Routes
# -------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request, user: dict = Depends(get_current_user_obj)):
    """Main Executive SRE Dashboard Page."""
    catalog = get_domain_catalog()
    with get_db_session() as db:
        stats = crud.get_user_progress_summary(db, user["id"])
        stats["clear_rate_percent"] = int((stats.get("cleared_count", 0) / 54) * 100) if stats else 0
        leaderboard = crud.get_global_leaderboard(db, limit=10)

    cleared_ids = set(stats.get("cleared_stage_ids", []))

    # Calculate domain-by-domain summaries
    domain_summaries = []
    for d_id, domain in sorted(catalog.items()):
        total_stages = sum(len(t["stages"]) for t in domain["tracks"].values())
        cleared_in_dom = sum(
            1 for t in domain["tracks"].values() for s in t["stages"] if s.id in cleared_ids
        )
        pct = int((cleared_in_dom / total_stages) * 100) if total_stages > 0 else 0
        clean_name = domain["name"]
        for emo in ["💾", "⚙️", "🌐", "🚀", "🐳", "🗄️", "☁️"]:
            clean_name = clean_name.replace(emo, "").strip()

        domain_summaries.append(
            {
                "id": d_id,
                "code": f"DOM-0{d_id}",
                "name": clean_name,
                "en_name": DOMAIN_EN_NAMES.get(d_id, "Infrastructure"),
                "icon": DOMAIN_ICONS.get(d_id, "fa-solid fa-server"),
                "track_count": len(domain["tracks"]),
                "total_stages": total_stages,
                "cleared_count": cleared_in_dom,
                "percent": pct,
            }
        )

    # Find user rank in leaderboard
    user_rank = None
    for r in leaderboard:
        if r["username"] == user["username"]:
            user_rank = r["rank"]
            break

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "stats": stats,
            "domain_summaries": domain_summaries,
            "leaderboard": leaderboard,
            "user_rank": user_rank,
            "docker_available": orchestrator.is_docker_available,
        },
    )


@app.get("/challenges", response_class=HTMLResponse)
def challenges_page(request: Request, user: dict = Depends(get_current_user_obj)):
    """Dedicated 7 Domains 18 Tracks 54 Problems Matrix Explorer."""
    catalog = get_domain_catalog()
    with get_db_session() as db:
        stats = crud.get_user_progress_summary(db, user["id"])

    cleared_ids = set(stats.get("cleared_stage_ids", []))

    return templates.TemplateResponse(
        request=request,
        name="challenges.html",
        context={
            "user": user,
            "stats": stats,
            "catalog": catalog,
            "cleared_ids": cleared_ids,
            "domain_icons": DOMAIN_ICONS,
            "domain_en_names": DOMAIN_EN_NAMES,
            "docker_available": orchestrator.is_docker_available,
        },
    )


@app.get("/play/{stage_id}", response_class=HTMLResponse)
def workspace_page(stage_id: str, request: Request, user: dict = Depends(get_current_user_obj)):
    """Dual-Pane Incident Workspace Page."""
    challenge = get_challenge(stage_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge stage not found.")

    with get_db_session() as db:
        # Fetch or get attempt
        attempt = (
            db.query(models.StageAttempt)
            .filter(
                models.StageAttempt.user_id == user["id"],
                models.StageAttempt.stage_id == stage_id,
                models.StageAttempt.status == "IN_PROGRESS",
            )
            .first()
        )
        stats = crud.get_user_progress_summary(db, user["id"])

    session_id = attempt.session_id if attempt else f"sess_{os.urandom(4).hex()}"

    return templates.TemplateResponse(
        request=request,
        name="workspace.html",
        context={
            "user": user,
            "stats": stats,
            "challenge": challenge,
            "attempt": attempt,
            "session_id": session_id,
            "docker_available": orchestrator.is_docker_available,
        },
    )


@app.get("/community", response_class=HTMLResponse)
def community_page(
    request: Request,
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "latest",
    user: dict = Depends(get_current_user_obj),
):
    """Community Forum Home Page."""
    with get_db_session() as db:
        posts = crud.get_posts(db, category=category, search=search, sort_by=sort)
        stats = crud.get_user_progress_summary(db, user["id"])
    return templates.TemplateResponse(
        request=request,
        name="community.html",
        context={
            "user": user,
            "stats": stats,
            "posts": posts,
            "selected_category": category or "all",
            "selected_sort": sort,
            "search_query": search or "",
            "docker_available": orchestrator.is_docker_available,
        },
    )


@app.get("/community/{post_id}", response_class=HTMLResponse)
def post_detail_page(
    post_id: int,
    request: Request,
    user: dict = Depends(get_current_user_obj),
):
    """Community Post Detail & Discussion Page."""
    with get_db_session() as db:
        post = crud.get_post_by_id(db, post_id, increment_views=True)
        if not post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        stats = crud.get_user_progress_summary(db, user["id"])
        user_liked = (
            db.query(models.PostLike)
            .filter(models.PostLike.post_id == post_id, models.PostLike.user_id == user["id"])
            .first()
            is not None
        )
    return templates.TemplateResponse(
        request=request,
        name="post_detail.html",
        context={
            "user": user,
            "stats": stats,
            "post": post,
            "user_liked": user_liked,
            "docker_available": orchestrator.is_docker_available,
        },
    )


# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------
class LoginRequest(BaseModel):
    username: str


class CreatePostRequest(BaseModel):
    title: str
    content: str
    category: str = "general"
    stage_id: Optional[str] = None


class CreateCommentRequest(BaseModel):
    content: str


@app.post("/api/community/posts")
def api_create_post(data: CreatePostRequest, user: dict = Depends(get_current_user_obj)):
    if not data.title.strip() or not data.content.strip():
        raise HTTPException(status_code=400, detail="제목과 내용을 모두 입력해주세요.")
    with get_db_session() as db:
        post = crud.create_post(
            db=db,
            user_id=user["id"],
            title=data.title,
            content=data.content,
            category=data.category,
            stage_id=data.stage_id,
        )
        post_id = post.id
    return {"status": "success", "post_id": post_id}


@app.post("/api/community/posts/{post_id}/comments")
def api_create_comment(
    post_id: int, data: CreateCommentRequest, user: dict = Depends(get_current_user_obj)
):
    if not data.content.strip():
        raise HTTPException(status_code=400, detail="댓글 내용을 입력해주세요.")
    with get_db_session() as db:
        comment = crud.add_comment(
            db=db,
            post_id=post_id,
            user_id=user["id"],
            content=data.content,
        )
    return {"status": "success", "comment_id": comment.id}


@app.post("/api/community/posts/{post_id}/like")
def api_toggle_like(post_id: int, user: dict = Depends(get_current_user_obj)):
    with get_db_session() as db:
        res = crud.toggle_post_like(db=db, post_id=post_id, user_id=user["id"])
    return res


@app.post("/api/user/login")
def api_login(data: LoginRequest):
    uname = data.username.strip()
    if not uname:
        raise HTTPException(status_code=400, detail="Username cannot be empty.")

    with get_db_session() as db:
        user = crud.get_or_create_user(db, uname)
        resp = JSONResponse({"status": "success", "username": user.username, "total_score": user.total_score})
        resp.set_cookie(key="chaos_username", value=user.username, max_age=30 * 86400)
        return resp


@app.get("/api/catalog")
def api_get_catalog(user: dict = Depends(get_current_user_obj)):
    catalog = get_domain_catalog()
    with get_db_session() as db:
        stats = crud.get_user_progress_summary(db, user["id"])
    return {
        "catalog": catalog,
        "cleared_stage_ids": stats.get("cleared_stage_ids", []),
        "total_score": user["total_score"],
    }


@app.get("/api/leaderboard")
def api_get_leaderboard():
    with get_db_session() as db:
        return {"leaderboard": crud.get_global_leaderboard(db, limit=20)}


class StageActionRequest(BaseModel):
    session_id: str


@app.post("/api/stages/{stage_id}/start")
def api_start_stage(stage_id: str, data: StageActionRequest, user: dict = Depends(get_current_user_obj)):
    challenge = get_challenge(stage_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found.")

    sandbox_info = orchestrator.create_sandbox(stage_id, data.session_id)

    with get_db_session() as db:
        attempt = crud.start_stage_attempt(
            db=db,
            user_id=user["id"],
            stage_id=stage_id,
            session_id=data.session_id,
            container_id=sandbox_info.get("container_id", ""),
        )
        return {
            "status": "started",
            "attempt_id": attempt.id,
            "session_id": data.session_id,
            "container_name": sandbox_info.get("container_name", ""),
        }


@app.post("/api/stages/{stage_id}/verify")
def api_verify_stage(stage_id: str, data: StageActionRequest, user: dict = Depends(get_current_user_obj)):
    challenge = get_challenge(stage_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found.")

    is_success, msg = orchestrator.verify_sandbox(stage_id, data.session_id)

    if is_success:
        with get_db_session() as db:
            attempt = (
                db.query(models.StageAttempt)
                .filter(
                    models.StageAttempt.user_id == user["id"],
                    models.StageAttempt.stage_id == stage_id,
                    models.StageAttempt.session_id == data.session_id,
                    models.StageAttempt.status == "IN_PROGRESS",
                )
                .first()
            )
            earned_score = 0
            solve_time = 0
            if attempt:
                completed = crud.finish_stage_attempt(
                    db=db,
                    attempt_id=attempt.id,
                    success=True,
                )
                earned_score = completed.earned_score if completed else challenge.base_score
                solve_time = completed.elapsed_seconds if completed else 0

            pm_data = challenge.post_mortem.model_dump() if hasattr(challenge.post_mortem, "model_dump") else challenge.post_mortem.dict()
            return {
                "status": "cleared",
                "message": msg,
                "earned_score": earned_score,
                "solve_time_seconds": solve_time,
                "post_mortem": pm_data,
            }
    else:
        return {
            "status": "failed",
            "message": msg,
        }


@app.post("/api/stages/{stage_id}/hint")
def api_get_hint(stage_id: str, data: StageActionRequest, user: dict = Depends(get_current_user_obj)):
    challenge = get_challenge(stage_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found.")

    with get_db_session() as db:
        attempt = (
            db.query(models.StageAttempt)
            .filter(
                models.StageAttempt.user_id == user["id"],
                models.StageAttempt.stage_id == stage_id,
                models.StageAttempt.session_id == data.session_id,
            )
            .first()
        )
        current_hints_used = attempt.hints_used if attempt else 0
        next_hint_idx = current_hints_used

        if next_hint_idx >= len(challenge.hints):
            return {
                "status": "no_more_hints",
                "message": "모든 힌트를 이미 확인하셨습니다.",
                "hints": [h.model_dump() if hasattr(h, "model_dump") else h.dict() for h in challenge.hints],
            }

        if attempt:
            crud.record_hint_used(db, attempt.id)

        unlocked_hints = [challenge.hints[i].model_dump() if hasattr(challenge.hints[i], "model_dump") else challenge.hints[i].dict() for i in range(next_hint_idx + 1)]
        return {
            "status": "unlocked",
            "unlocked_count": next_hint_idx + 1,
            "hints": unlocked_hints,
        }


class MentorQuestionRequest(BaseModel):
    session_id: str
    question: Optional[str] = ""


@app.post("/api/stages/{stage_id}/ask-mentor")
def api_ask_mentor(stage_id: str, data: MentorQuestionRequest):
    challenge = get_challenge(stage_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found.")

    container = None
    if orchestrator.is_docker_available and orchestrator._client:
        try:
            container_name = orchestrator._get_container_name(stage_id, data.session_id)
            container = orchestrator._client.containers.get(container_name)
        except Exception:
            container = None

    diagnostics = ai_mentor.capture_diagnostics(container)
    advice = ai_mentor.consult(challenge, diagnostics, user_question=data.question)

    return {
        "status": "success",
        "question": data.question,
        "advice": advice,
    }


# -------------------------------------------------------------
# WebSocket: Real-time Xterm.js Interactive PTY Terminal Bridge
# -------------------------------------------------------------
@app.websocket("/ws/terminal/{stage_id}/{session_id}")
async def websocket_terminal_bridge(websocket: WebSocket, stage_id: str, session_id: str):
    await websocket.accept()

    if not orchestrator.is_docker_available or not orchestrator._client:
        await websocket.send_text(
            "\r\n\x1b[33m[Mock Mode] Docker daemon is not active on this host.\r\n"
            "ChaosQuest Web GUI is running in preview/dry-run mode.\x1b[0m\r\n# "
        )
        try:
            while True:
                data = await websocket.receive_text()
                await websocket.send_text(data)
        except WebSocketDisconnect:
            return

    # Ensure container is alive
    orchestrator.ensure_sandbox_running(stage_id, session_id)
    container_name = orchestrator._get_container_name(stage_id, session_id)

    try:
        container = orchestrator._client.containers.get(container_name)
    except Exception as e:
        await websocket.send_text(f"\r\n\x1b[31mFailed to attach container: {e}\x1b[0m\r\n")
        await websocket.close()
        return

    # Create Docker Exec PTY session
    client_api = orchestrator._client.api
    exec_inst = client_api.exec_create(
        container=container.id,
        cmd="/bin/bash",
        stdin=True,
        stdout=True,
        stderr=True,
        tty=True,
        environment={"TERM": "xterm-256color", "COLORTERM": "truecolor"},
    )
    exec_id = exec_inst["Id"]
    sock = client_api.exec_start(exec_id, detach=False, tty=True, stream=True, socket=True)

    loop = asyncio.get_event_loop()

    # Reading from Docker socket -> sending to WebSocket
    async def read_from_docker():
        try:
            while True:
                # Docker raw socket read
                data = await loop.run_in_executor(None, sock._sock.recv, 4096)
                if not data:
                    break
                await websocket.send_bytes(data)
        except Exception:
            pass

    # Reading from WebSocket -> writing to Docker socket
    async def write_to_docker():
        try:
            while True:
                msg = await websocket.receive()
                if "text" in msg:
                    txt = msg["text"]
                    if txt.startswith("{") and "resize" in txt:
                        try:
                            meta = json.loads(txt)
                            if meta.get("type") == "resize":
                                client_api.exec_resize(exec_id, height=meta["rows"], width=meta["cols"])
                        except Exception:
                            pass
                    else:
                        await loop.run_in_executor(None, sock._sock.sendall, txt.encode("utf-8"))
                elif "bytes" in msg:
                    await loop.run_in_executor(None, sock._sock.sendall, msg["bytes"])
        except Exception:
            pass

    task_read = asyncio.create_task(read_from_docker())
    task_write = asyncio.create_task(write_to_docker())

    try:
        done, pending = await asyncio.wait([task_read, task_write], return_when=asyncio.FIRST_COMPLETED)
        for t in pending:
            t.cancel()
    except Exception:
        pass
    finally:
        try:
            sock.close()
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass
