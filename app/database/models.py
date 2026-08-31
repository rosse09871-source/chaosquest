from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.connection import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    total_score = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    last_active_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    attempts = relationship("StageAttempt", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', score={self.total_score})>"


class Stage(Base):
    __tablename__ = "stages"

    id = Column(String(32), primary_key=True, index=True)  # e.g., '101', '102'
    title = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False)          # Filesystem, Process, Network, Nginx, Performance
    difficulty = Column(String(32), default="Easy", nullable=False) # Easy, Medium, Hard
    base_score = Column(Integer, default=500, nullable=False)
    target_time_seconds = Column(Integer, default=600, nullable=False) # 10 mins
    description = Column(Text, nullable=True)

    attempts = relationship("StageAttempt", back_populates="stage")

    def __repr__(self):
        return f"<Stage(id='{self.id}', title='{self.title}', diff='{self.difficulty}')>"


class StageAttempt(Base):
    __tablename__ = "stage_attempts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    stage_id = Column(String(32), ForeignKey("stages.id"), index=True, nullable=False)
    session_id = Column(String(64), index=True, nullable=False) # Unique per active game session
    container_id = Column(String(128), nullable=True)
    status = Column(String(32), default="IN_PROGRESS", nullable=False) # IN_PROGRESS, CLEARED, FAILED, ABANDONED
    hints_used = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime, default=utc_now, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    elapsed_seconds = Column(Integer, nullable=True)
    earned_score = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="attempts")
    stage = relationship("Stage", back_populates="attempts")

    def __repr__(self):
        return f"<StageAttempt(id={self.id}, user_id={self.user_id}, stage='{self.stage_id}', status='{self.status}')>"
