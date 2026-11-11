"""Application settings loaded from environment variables and the .env file."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Monthly dues every active member is expected to pay, in VND.
MONTHLY_DUES = 50_000

# Expense categories shown in the "new expense" form.
EXPENSE_CATEGORIES = [
    "Văn phòng phẩm",
    "Sự kiện",
    "Nước uống",
    "In ấn",
    "Thuê phòng",
    "Khác",
]

# Spreadsheet tools (Google Sheets IMPORTDATA) cannot log in, so the yearly
# dues sheet also accepts this token in the query string.
DUES_EXPORT_TOKEN = "clb-sotc-2026"


@dataclass(frozen=True)
class Settings:
    secret_key: str
    database_path: str


def get_settings() -> Settings:
    """Read settings from the environment, loading .env first if it exists."""
    load_dotenv(BASE_DIR / ".env")
    database_path = os.getenv("DATABASE_PATH", "data/so_thu_chi.db")
    if not os.path.isabs(database_path):
        database_path = str(BASE_DIR / database_path)
    return Settings(
        secret_key=os.getenv("SECRET_KEY", "change-me"),
        database_path=database_path,
    )
