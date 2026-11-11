"""SQLite access helpers.

The app uses the standard library sqlite3 module directly. Each request gets
its own connection through the ``get_db`` dependency.
"""

import sqlite3
from collections.abc import Iterator
from pathlib import Path

from fastapi import Request

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def connect(database_path: str) -> sqlite3.Connection:
    """Open a connection with row access by column name and foreign keys on."""
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(database_path: str) -> None:
    """Create tables if they do not exist yet."""
    conn = connect(database_path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()


def get_db(request: Request) -> Iterator[sqlite3.Connection]:
    """FastAPI dependency that yields a connection and closes it afterwards."""
    conn = connect(request.app.state.settings.database_path)
    try:
        yield conn
    finally:
        conn.close()
