from pathlib import Path
from typing import List, Dict, Optional, Any
import yaml
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.config import CHALLENGES_DIR
from app.database import crud


class IncidentInfo(BaseModel):
    reporter: str = "Monitoring Bot"
    severity: str = "P1-CRITICAL"
    symptom: str
    objective: str


class Hint(BaseModel):
    level: int
    title: str = ""
    cost: int = 0
    text: str


class PostMortem(BaseModel):
    root_cause: str
    key_commands: List[str] = Field(default_factory=list)
    real_world_lesson: str


class ChallengeMetadata(BaseModel):
    id: str
    domain_id: int = 1
    domain: str = "💾 파일시스템 & 스토리지"
    track_id: str = "101"
    track: str = "Track 101: 유령 파일 & 파일 디스크립터 누수"
    title: str
    category: str
    difficulty: str = "Easy"
    base_score: int = 500
    target_time_seconds: int = 600
    incident: IncidentInfo
    hints: List[Hint] = Field(default_factory=list)
    post_mortem: PostMortem
    sabotage_script_path: Optional[str] = None
    verify_script_path: Optional[str] = None


def generate_5_level_hints(raw_data: dict) -> List[Hint]:
    """Generates structured 5-level progressive hints with 1-3 free, 4-5 penalized."""
    raw_hints = raw_data.get("hints", [])
    raw_texts = [h.get("text", "") if isinstance(h, dict) else getattr(h, "text", "") for h in raw_hints]
    
    incident = raw_data.get("incident", {})
    symptom = incident.get("symptom", "시스템 이상 동작")
    objective = incident.get("objective", "정상 서비스 복구")
    
    post_mortem = raw_data.get("post_mortem", {})
    root_cause = post_mortem.get("root_cause", "설정 또는 프로세스 오작동")
    key_cmds = post_mortem.get("key_commands", [])
    lesson = post_mortem.get("real_world_lesson", "주기적인 상태 점검 및 리소스 모니터링이 필요합니다.")
    
    h1_text = raw_texts[0] if len(raw_texts) > 0 else f"관련 서비스 상태 및 로그 디렉터리(/var/log, /etc)를 먼저 확인하세요. 목표: {objective}"
    h2_text = raw_texts[1] if len(raw_texts) > 1 else f"증상을 구체적으로 관찰하세요. 발생 증상: {symptom}"
    h3_text = f"근본 원인 분석: {root_cause}"
    h4_text = raw_texts[2] if len(raw_texts) > 2 else f"해결 전략: {lesson}"
    
    if key_cmds:
        cmd_list_str = "\n".join([f"  - `{c}`" for c in key_cmds])
        h5_text = f"핵심 복구 명령어:\n{cmd_list_str}\n\n위 명령어를 상황에 맞게 조합하여 실행한 후 정상 상태를 검증하세요."
    else:
        h5_text = f"완전 복구 가이드: 원인({root_cause})을 조치하고 서비스를 재시작(reload/restart)하여 상태를 200 OK로 만드세요."

    return [
        Hint(level=1, title="1단계: 기초 점검 (Orientation)", cost=0, text=h1_text),
        Hint(level=2, title="2단계: 증상 진단 (Symptom Triage)", cost=0, text=h2_text),
        Hint(level=3, title="3단계: 원인 분석 (Root Cause)", cost=0, text=h3_text),
        Hint(level=4, title="4단계: 해결 전략 (Solution Strategy)", cost=50, text=h4_text),
        Hint(level=5, title="5단계: 완전 복구 (Detailed Fix & Commands)", cost=100, text=h5_text),
    ]


def load_all_challenge_metadata() -> Dict[str, ChallengeMetadata]:
    """Scans CHALLENGES_DIR and loads all challenge metadata."""
    challenges: Dict[str, ChallengeMetadata] = {}

    if not CHALLENGES_DIR.exists():
        return challenges

    for stage_folder in sorted(CHALLENGES_DIR.iterdir()):
        if not stage_folder.is_dir():
            continue

        meta_file = stage_folder / "metadata.yaml"
        sabotage_file = stage_folder / "sabotage.sh"
        verify_file = stage_folder / "verify.sh"

        if meta_file.exists():
            with open(meta_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Ensure 5-level progressive hints
            data["hints"] = generate_5_level_hints(data)

            meta = ChallengeMetadata(**data)
            meta.sabotage_script_path = str(sabotage_file.resolve()) if sabotage_file.exists() else None
            meta.verify_script_path = str(verify_file.resolve()) if verify_file.exists() else None
            challenges[meta.id] = meta

    return challenges


def get_challenge(stage_id: str) -> Optional[ChallengeMetadata]:
    """Retrieves metadata for a specific stage ID."""
    all_stages = load_all_challenge_metadata()
    return all_stages.get(stage_id)


def get_domain_catalog() -> Dict[int, Dict[str, Any]]:
    """Groups all loaded challenges into Domains -> Tracks -> Stages."""
    all_challenges = load_all_challenge_metadata()
    catalog: Dict[int, Dict[str, Any]] = {}

    for meta in all_challenges.values():
        d_id = meta.domain_id
        if d_id not in catalog:
            catalog[d_id] = {
                "domain_id": d_id,
                "name": meta.domain,
                "tracks": {},
            }

        t_id = meta.track_id
        if t_id not in catalog[d_id]["tracks"]:
            catalog[d_id]["tracks"][t_id] = {
                "track_id": t_id,
                "title": meta.track,
                "stages": [],
            }

        catalog[d_id]["tracks"][t_id]["stages"].append(meta)

    # Sort stages within each track by id
    for d in catalog.values():
        for t in d["tracks"].values():
            t["stages"].sort(key=lambda s: s.id)

    return catalog


def sync_challenges_to_db(db: Session) -> int:
    """Synchronizes all filesystem challenge definitions into the database."""
    challenges = load_all_challenge_metadata()
    count = 0
    for meta in challenges.values():
        crud.upsert_stage(
            db=db,
            stage_id=meta.id,
            title=f"[{meta.difficulty}] {meta.title}",
            category=meta.category,
            difficulty=meta.difficulty,
            base_score=meta.base_score,
            target_time_seconds=meta.target_time_seconds,
            description=meta.incident.symptom,
        )
        count += 1
    return count
