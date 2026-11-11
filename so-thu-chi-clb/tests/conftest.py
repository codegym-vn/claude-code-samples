import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# app.main builds a module-level app on import; keep it away from the real database.
os.environ["DATABASE_PATH"] = str(Path(tempfile.mkdtemp()) / "import.db")
os.environ["SECRET_KEY"] = "test-secret"

from app.auth import DEMO_ACCOUNTS  # noqa: E402
from app.config import Settings  # noqa: E402
from app.db import connect  # noqa: E402
from app.main import create_app  # noqa: E402
from app.services import ledger, members  # noqa: E402


@pytest.fixture
def settings(tmp_path):
    return Settings(secret_key="test-secret", database_path=str(tmp_path / "test.db"))


@pytest.fixture
def app(settings):
    return create_app(settings)


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def conn(app, settings):
    connection = connect(settings.database_path)
    yield connection
    connection.close()


def login(client: TestClient, username: str) -> None:
    password = DEMO_ACCOUNTS[username][2]
    response = client.post(
        "/login", data={"username": username, "password": password}, follow_redirects=False
    )
    assert response.status_code == 303


@pytest.fixture
def treasurer_client(client):
    login(client, "thuquy")
    return client


@pytest.fixture
def member_client(client):
    login(client, "thanhvien")
    return client


@pytest.fixture
def make_member(conn):
    counter = {"n": 0}

    def _make(full_name: str, joined_on: str = "2026-01-05", student_code: str | None = None):
        counter["n"] += 1
        code = student_code or f"SV2026{counter['n']:03d}"
        return members.create_member(conn, full_name, code, joined_on)

    return _make


@pytest.fixture
def pay_dues(conn):
    def _pay(member_id: int, dues_month: str, received_on: str, amount: int = 50_000):
        return ledger.create_income(
            conn,
            received_on=received_on,
            amount=amount,
            kind="dues",
            member_id=member_id,
            dues_month=dues_month,
            created_by="thuquy",
        )

    return _pay


@pytest.fixture
def add_expense(conn):
    def _add(spent_on: str, amount: int, description: str = "Mua nước", category: str = "Nước uống"):
        return ledger.create_expense(
            conn,
            spent_on=spent_on,
            amount=amount,
            category=category,
            description=description,
            created_by="thuquy",
        )

    return _add
