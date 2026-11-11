import pytest

from app.services.members import (
    MemberError,
    create_member,
    list_members,
    mark_left,
    member_dues_summary,
    search_members,
)


def test_create_member_normalises_input(conn):
    member = create_member(conn, "  Nguyễn   Văn  An ", "sv2026001", "2026-01-05")
    assert member.full_name == "Nguyễn Văn An"
    assert member.student_code == "SV2026001"
    assert member.is_active


@pytest.mark.parametrize(
    "full_name, code, joined_on",
    [
        ("A", "SV2026001", "2026-01-05"),
        ("Nguyễn Văn An", "123", "2026-01-05"),
        ("Nguyễn Văn An", "SV2026001", "05/01/2026"),
        ("Nguyễn Văn An", "SV2026001", "2999-01-01"),
    ],
)
def test_create_member_rejects_invalid_data(conn, full_name, code, joined_on):
    with pytest.raises(MemberError):
        create_member(conn, full_name, code, joined_on)


def test_student_code_must_be_unique(conn, make_member):
    make_member("Nguyễn Văn An", student_code="SV2026001")
    with pytest.raises(MemberError):
        make_member("Trần Văn Bình", student_code="SV2026001")


def test_search_by_name(conn, make_member):
    make_member("Nguyễn Văn An")
    make_member("Trần Thị Bình")
    found = search_members(conn, "Nguyễn")
    assert [m.full_name for m in found] == ["Nguyễn Văn An"]


def test_search_by_student_code(conn, make_member):
    make_member("Nguyễn Văn An", student_code="SV2026111")
    make_member("Trần Thị Bình", student_code="SV2026222")
    found = search_members(conn, "SV2026222")
    assert [m.full_name for m in found] == ["Trần Thị Bình"]


def test_empty_search_returns_everyone(conn, make_member):
    make_member("Nguyễn Văn An")
    make_member("Trần Thị Bình")
    assert len(search_members(conn, "  ")) == 2


def test_mark_left_keeps_member_in_full_list(conn, make_member):
    member = make_member("Lê Văn Cường")
    updated = mark_left(conn, member.id, "2026-03-01")
    assert updated.status == "left"
    assert updated.left_on == "2026-03-01"
    assert [m.id for m in list_members(conn)] == [member.id]
    assert list_members(conn, include_left=False) == []


def test_mark_left_twice_is_rejected(conn, make_member):
    member = make_member("Lê Văn Cường")
    mark_left(conn, member.id, "2026-03-01")
    with pytest.raises(MemberError):
        mark_left(conn, member.id, "2026-03-02")


def test_member_dues_summary(conn, make_member, pay_dues):
    member = make_member("Phạm Thu Trang")
    pay_dues(member.id, "2026-02", "2026-02-03")
    pay_dues(member.id, "2026-03", "2026-03-04")
    summary = member_dues_summary(conn, member.id)
    assert "total_paid" in summary


def test_member_list_page(member_client, make_member):
    make_member("Nguyễn Văn An")
    response = member_client.get("/members")
    assert response.status_code == 200
    assert "Nguyễn Văn An" in response.text


def test_member_search_page(member_client, make_member):
    make_member("Nguyễn Văn An")
    make_member("Trần Thị Bình")
    response = member_client.get("/members", params={"q": "Bình"})
    assert response.status_code == 200
    assert "Trần Thị Bình" in response.text
    assert "Nguyễn Văn An" not in response.text


def test_member_detail_404(member_client):
    response = member_client.get("/members/999")
    assert response.status_code == 404


def test_treasurer_can_add_member(treasurer_client, conn):
    response = treasurer_client.post(
        "/members/new",
        data={"full_name": "Đỗ Gia Huy", "student_code": "SV2026050", "joined_on": "2026-02-01"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert [m.full_name for m in list_members(conn)] == ["Đỗ Gia Huy"]


def test_member_cannot_add_member(member_client, conn):
    response = member_client.post(
        "/members/new",
        data={"full_name": "Đỗ Gia Huy", "student_code": "SV2026050", "joined_on": "2026-02-01"},
        follow_redirects=False,
    )
    assert response.status_code == 403
    assert list_members(conn) == []
