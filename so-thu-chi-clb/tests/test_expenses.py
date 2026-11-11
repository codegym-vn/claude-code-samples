import pytest

from app.services.ledger import LedgerError, cancel_expense, get_expense, list_expenses


def test_treasurer_creates_expense(treasurer_client, conn):
    response = treasurer_client.post(
        "/expenses/new",
        data={
            "spent_on": "2026-03-10",
            "amount": "120.000",
            "category": "Nước uống",
            "description": "Nước uống buổi sinh hoạt",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    expenses = list_expenses(conn)
    assert len(expenses) == 1
    assert expenses[0].amount == 120_000
    assert expenses[0].status == "active"


def test_member_cannot_create_expense(member_client, conn):
    response = member_client.post(
        "/expenses/new",
        data={
            "spent_on": "2026-03-10",
            "amount": "120.000",
            "category": "Nước uống",
            "description": "Nước uống buổi sinh hoạt",
        },
        follow_redirects=False,
    )
    assert response.status_code == 403
    assert list_expenses(conn) == []


def test_expense_needs_description(treasurer_client):
    response = treasurer_client.post(
        "/expenses/new",
        data={"spent_on": "2026-03-10", "amount": "120000", "category": "Khác", "description": " "},
    )
    assert response.status_code == 400


def test_treasurer_cancels_expense(treasurer_client, add_expense, conn):
    expense = add_expense("2026-03-10", 120_000)
    response = treasurer_client.post(
        f"/expenses/{expense.id}/cancel", data={"note": "Nhập nhầm"}, follow_redirects=False
    )
    assert response.status_code == 303
    cancelled = get_expense(conn, expense.id)
    assert cancelled.status == "cancelled"
    assert cancelled.cancel_note == "Nhập nhầm"


def test_member_cannot_cancel_expense(member_client, add_expense):
    expense = add_expense("2026-03-10", 120_000)
    response = member_client.post(f"/expenses/{expense.id}/cancel", follow_redirects=False)
    assert response.status_code != 200


def test_cancel_twice_is_rejected(conn, add_expense):
    expense = add_expense("2026-03-10", 120_000)
    cancel_expense(conn, expense.id)
    with pytest.raises(LedgerError):
        cancel_expense(conn, expense.id)


def test_cancel_unknown_expense_returns_404(treasurer_client):
    response = treasurer_client.post("/expenses/999/cancel", follow_redirects=False)
    assert response.status_code == 404


def test_expense_list_total_ignores_cancelled(member_client, add_expense, conn):
    add_expense("2026-03-10", 120_000)
    wrong = add_expense("2026-03-11", 1_500_000, "Đặt cọc xe")
    cancel_expense(conn, wrong.id)
    response = member_client.get("/expenses")
    assert response.status_code == 200
    assert "Đã hủy" in response.text
    assert "120.000 đ</th>" in response.text
