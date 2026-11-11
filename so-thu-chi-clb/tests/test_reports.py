from app.services.ledger import cancel_expense, record_donation
from app.services.reports import fund_balance, monthly_report, unpaid_members


def test_monthly_report_page(treasurer_client):
    response = treasurer_client.get("/reports/monthly", params={"month": "2026-03"})
    assert response is not None


def test_member_cannot_see_monthly_report(member_client):
    response = member_client.get("/reports/monthly", params={"month": "2026-03"})
    assert response.status_code == 403


def test_treasurer_sees_monthly_report(treasurer_client, conn):
    record_donation(conn, received_on="2026-03-14", amount=300_000, note="Ủng hộ", created_by="thuquy")
    response = treasurer_client.get("/reports/monthly", params={"month": "2026-03"})
    assert response.status_code == 200
    assert "Báo cáo tháng 2026-03" in response.text
    assert "300.000 đ" in response.text


def test_monthly_report_totals(conn, make_member, pay_dues, add_expense):
    an = make_member("Nguyễn Văn An")
    binh = make_member("Trần Thị Bình")
    pay_dues(an.id, "2026-03", "2026-03-05")
    pay_dues(binh.id, "2026-03", "2026-03-12")
    record_donation(conn, received_on="2026-03-20", amount=200_000, note="", created_by="thuquy")
    add_expense("2026-03-08", 120_000)
    add_expense("2026-03-15", 80_000, "Bút", "Văn phòng phẩm")
    # Entries in neighbouring months must not count.
    record_donation(conn, received_on="2026-02-15", amount=999_000, note="", created_by="thuquy")
    add_expense("2026-04-02", 555_000)

    report = monthly_report(conn, 2026, 3)

    assert report["total_dues"] == 100_000
    assert report["total_donations"] == 200_000
    assert report["total_income"] == 300_000
    assert report["total_expense"] == 200_000
    assert report["net"] == 100_000
    assert report["by_category"] == [("Nước uống", 120_000), ("Văn phòng phẩm", 80_000)]


def test_monthly_report_skips_cancelled_expenses(conn, add_expense):
    add_expense("2026-03-08", 120_000)
    wrong = add_expense("2026-03-09", 1_000_000, "Đặt cọc")
    cancel_expense(conn, wrong.id)
    report = monthly_report(conn, 2026, 3)
    assert report["total_expense"] == 120_000


def test_fund_balance(conn, make_member, pay_dues, add_expense):
    an = make_member("Nguyễn Văn An")
    pay_dues(an.id, "2026-03", "2026-03-05")
    record_donation(conn, received_on="2026-03-20", amount=200_000, note="", created_by="thuquy")
    add_expense("2026-03-08", 120_000)
    add_expense("2026-03-15", 30_000)
    assert fund_balance(conn) == 100_000


def test_unpaid_members(conn, make_member, pay_dues):
    an = make_member("Nguyễn Văn An")
    binh = make_member("Trần Thị Bình")
    pay_dues(an.id, "2026-03", "2026-03-05")
    assert [m.id for m in unpaid_members(conn, "2026-03")] == [binh.id]
    assert {m.id for m in unpaid_members(conn, "2026-04")} == {an.id, binh.id}


def test_unpaid_page(treasurer_client, make_member):
    make_member("Nguyễn Văn An")
    response = treasurer_client.get("/reports/unpaid", params={"month": "2026-03"})
    assert response.status_code == 200
    assert "Nguyễn Văn An" in response.text


def test_dashboard_shows_balance(member_client, conn):
    record_donation(conn, received_on="2026-03-20", amount=200_000, note="", created_by="thuquy")
    response = member_client.get("/")
    assert response.status_code == 200
    assert "200.000 đ" in response.text
