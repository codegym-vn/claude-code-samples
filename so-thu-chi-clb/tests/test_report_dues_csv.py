def test_dues_csv_for_treasurer(treasurer_client, make_member, pay_dues):
    an = make_member("Nguyễn Văn An", student_code="SV2026001")
    make_member("Trần Thị Bình", student_code="SV2026002")
    pay_dues(an.id, "2026-03", "2026-03-05")
    pay_dues(an.id, "2026-04", "2026-04-02")

    response = treasurer_client.get("/reports/dues.csv?year=2026")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    lines = response.text.splitlines()
    assert lines[0] == "Họ tên,Mã sinh viên,Trạng thái,Số tháng đã đóng,Tổng đã đóng"
    assert "Nguyễn Văn An,SV2026001,Đang sinh hoạt,2,100000" in lines
    assert "Trần Thị Bình,SV2026002,Đang sinh hoạt,0,0" in lines


def test_dues_csv_needs_login(client):
    response = client.get("/reports/dues.csv", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
