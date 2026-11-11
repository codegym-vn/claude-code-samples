from app.auth import ROLE_MEMBER, ROLE_TREASURER, authenticate


def test_authenticate_demo_accounts():
    assert authenticate("thuquy", "thuquy123").role == ROLE_TREASURER
    assert authenticate("thanhvien", "thanhvien123").role == ROLE_MEMBER


def test_authenticate_rejects_wrong_password():
    assert authenticate("thuquy", "sai-mat-khau") is None
    assert authenticate("khong-co", "x") is None


def test_pages_require_login(client):
    response = client.get("/members", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_login_page_renders(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert "Đăng nhập" in response.text


def test_login_with_wrong_password_shows_error(client):
    response = client.post("/login", data={"username": "thuquy", "password": "x"})
    assert response.status_code == 400
    assert "không đúng" in response.text


def test_login_then_logout(treasurer_client):
    home = treasurer_client.get("/")
    assert home.status_code == 200
    assert "Trần Thu Hà" in home.text

    treasurer_client.post("/logout")
    response = treasurer_client.get("/", follow_redirects=False)
    assert response.status_code == 303
