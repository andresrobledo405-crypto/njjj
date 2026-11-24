import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

APP_NAME = os.getenv("KINEPRO_NOMBRE", "KinePro")
DATA_DIR = Path(os.getenv("KINEPRO_DATA_DIR", BASE_DIR / "data"))
UPLOAD_DIR = DATA_DIR / "uploads"
DATABASE_PATH = DATA_DIR / "kinepro.db"
MAX_UPLOAD_BYTES = 8 * 1024 * 1024

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
