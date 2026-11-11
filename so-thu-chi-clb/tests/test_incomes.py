import pytest

from app.services.ledger import LedgerError, create_income, list_incomes, record_donation


def test_record_dues(conn, make_member, pay_dues):
    member = make_member("Nguyễn Văn An")
    income = pay_dues(member.id, "2026-03", "2026-03-05")
    assert income.amount == 50_000
    assert income.kind == "dues"
    assert income.dues_month == "2026-03"
    assert income.member_name == "Nguyễn Văn An"


def test_dues_cannot_be_paid_twice_for_same_month(conn, make_member, pay_dues):
    member = make_member("Nguyễn Văn An")
    pay_dues(member.id, "2026-03", "2026-03-05")
    with pytest.raises(LedgerError):
        pay_dues(member.id, "2026-03", "2026-03-20")


def test_dues_need_a_member(conn):
    with pytest.raises(LedgerError):
        create_income(
            conn,
            received_on="2026-03-05",
            amount=50_000,
            kind="dues",
            dues_month="2026-03",
            created_by="thuquy",
        )


def test_amount_must_be_positive_integer(conn):
    with pytest.raises(LedgerError):
        record_donation(conn, received_on="2026-03-05", amount=0, note="", created_by="thuquy")


def test_future_date_is_rejected(conn):
    with pytest.raises(LedgerError):
        record_donation(conn, received_on="2999-01-01", amount=100_000, note="", created_by="thuquy")


def test_donation_has_no_member_or_month(conn):
    income = record_donation(
        conn, received_on="2026-03-05", amount=200_000, note="Cựu thành viên", created_by="thuquy"
    )
    assert income.member_id is None
    assert income.dues_month is None
    assert income.kind_label == "Ủng hộ"


def test_list_incomes_filtered_by_month(conn):
    record_donation(conn, received_on="2026-02-27", amount=100_000, note="tháng 2", created_by="thuquy")
    record_donation(conn, received_on="2026-03-05", amount=200_000, note="tháng 3", created_by="thuquy")
    march = list_incomes(conn, "2026-03")
    assert [i.note for i in march] == ["tháng 3"]
    assert len(list_incomes(conn)) == 2


def test_treasurer_records_dues_through_form(treasurer_client, make_member, conn):
    member = make_member("Nguyễn Văn An")
    response = treasurer_client.post(
        "/incomes/new",
        data={
            "kind": "dues",
            "received_on": "2026-03-05",
            "amount": "50.000",
            "member_id": str(member.id),
            "dues_month": "2026-03",
            "note": "",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    incomes = list_incomes(conn)
    assert len(incomes) == 1
    assert incomes[0].amount == 50_000


def test_income_form_shows_validation_error(treasurer_client):
    response = treasurer_client.post(
        "/incomes/new",
        data={"kind": "donation", "received_on": "2026-03-05", "amount": "50,5"},
    )
    assert response.status_code == 400
    assert "số nguyên đồng" in response.text


def test_income_list_page(member_client, conn):
    record_donation(conn, received_on="2026-03-05", amount=200_000, note="Cựu thành viên", created_by="thuquy")
    response = member_client.get("/incomes")
    assert response.status_code == 200
    assert "200.000 đ" in response.text
