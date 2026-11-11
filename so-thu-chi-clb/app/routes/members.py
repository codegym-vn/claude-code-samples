import sqlite3

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.auth import ROLE_TREASURER, User, get_current_user, require_role
from app.dates import today
from app.db import get_db
from app.services.members import (
    MemberError,
    create_member,
    get_member,
    mark_left,
    member_dues_summary,
    search_members,
)
from app.templating import flash, render

router = APIRouter(prefix="/members")


@router.get("")
def member_list(
    request: Request,
    q: str = "",
    user: User = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    members = search_members(conn, q)
    return render(request, "members/list.html", {"members": members, "q": q}, user=user)


@router.get("/new")
def new_member_form(request: Request, user: User = Depends(get_current_user)):
    require_role(user, ROLE_TREASURER)
    form = {"full_name": "", "student_code": "", "joined_on": today().isoformat()}
    return render(request, "members/new.html", {"form": form}, user=user)


@router.post("/new")
def new_member(
    request: Request,
    full_name: str = Form(""),
    student_code: str = Form(""),
    joined_on: str = Form(""),
    user: User = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    require_role(user, ROLE_TREASURER)
    try:
        member = create_member(conn, full_name, student_code, joined_on)
    except MemberError as exc:
        form = {"full_name": full_name, "student_code": student_code, "joined_on": joined_on}
        return render(
            request, "members/new.html", {"form": form, "error": str(exc)}, status_code=400, user=user
        )
    flash(request, f"Đã thêm thành viên {member.full_name}.")
    return RedirectResponse(f"/members/{member.id}", status_code=303)


@router.get("/{member_id}")
def member_detail(
    request: Request,
    member_id: int,
    user: User = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    member = get_member(conn, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy thành viên.")
    summary = member_dues_summary(conn, member_id)
    return render(
        request, "members/detail.html", {"member": member, "summary": summary}, user=user
    )


@router.post("/{member_id}/leave")
def member_leave(
    request: Request,
    member_id: int,
    left_on: str = Form(""),
    user: User = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    require_role(user, ROLE_TREASURER)
    try:
        member = mark_left(conn, member_id, left_on or None)
    except (MemberError, ValueError) as exc:
        flash(request, str(exc), "error")
    else:
        flash(request, f"Đã ghi nhận {member.full_name} rời câu lạc bộ.")
    return RedirectResponse(f"/members/{member_id}", status_code=303)
