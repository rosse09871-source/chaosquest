import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CHALLENGES_DIR = BASE_DIR / "challenges"
DATA_DIR = BASE_DIR / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/chaosquest.db")

# Container & Sandbox Settings
DEFAULT_SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "1800"))  # 30 minutes
DEFAULT_CONTAINER_MEM_LIMIT = os.getenv("CONTAINER_MEM_LIMIT", "256m")
DEFAULT_CONTAINER_CPU_LIMIT = float(os.getenv("CONTAINER_CPU_LIMIT", "0.5"))
