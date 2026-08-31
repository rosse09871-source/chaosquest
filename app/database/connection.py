from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import DATABASE_URL

# SQLAlchemy Base for ORM models
Base = declarative_base()

# Create Engine
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


def init_db():
    """Initializes the database by creating all declared tables."""
    # Import models here to ensure they are registered with Base.metadata
    from app.database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db_session():
    """Context manager for providing a transactional database session."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
