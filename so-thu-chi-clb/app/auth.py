"""Very small login system for the demo.

There are two fixed demo accounts. The logged-in username is kept in the
signed session cookie. Every route that changes money data must call
``require_role`` explicitly.
"""

from dataclasses import dataclass

from fastapi import HTTPException, Request

ROLE_TREASURER = "thu_quy"
ROLE_MEMBER = "thanh_vien"

ROLE_LABELS = {
    ROLE_TREASURER: "Thủ quỹ",
    ROLE_MEMBER: "Thành viên",
}


@dataclass(frozen=True)
class User:
    username: str
    display_name: str
    role: str

    @property
    def role_label(self) -> str:
        return ROLE_LABELS[self.role]

    @property
    def is_treasurer(self) -> bool:
        return self.role == ROLE_TREASURER


# Demo accounts only. Passwords are intentionally simple; this app is a
# teaching sample and must never hold real data.
DEMO_ACCOUNTS = {
    "thuquy": ("Trần Thu Hà", ROLE_TREASURER, "thuquy123"),
    "thanhvien": ("Lê Minh Khang", ROLE_MEMBER, "thanhvien123"),
}


class NotAuthenticated(Exception):
    """Raised when a page needs a logged-in user and there is none."""


def authenticate(username: str, password: str) -> User | None:
    account = DEMO_ACCOUNTS.get(username.strip())
    if account is None:
        return None
    display_name, role, expected_password = account
    if password != expected_password:
        return None
    return User(username=username.strip(), display_name=display_name, role=role)


def user_from_session(request: Request) -> User | None:
    username = request.session.get("username")
    if not username or username not in DEMO_ACCOUNTS:
        return None
    display_name, role, _ = DEMO_ACCOUNTS[username]
    return User(username=username, display_name=display_name, role=role)


def get_current_user(request: Request) -> User:
    """FastAPI dependency: the logged-in user, or a redirect to the login page."""
    user = user_from_session(request)
    if user is None:
        raise NotAuthenticated()
    return user


def require_role(user: User, *roles: str) -> None:
    """Stop the request with 403 unless the user has one of the given roles."""
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="Bạn không có quyền thực hiện thao tác này.")
