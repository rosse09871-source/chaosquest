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
    cost: int = 50
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
