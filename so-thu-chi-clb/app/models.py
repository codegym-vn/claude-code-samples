"""Plain data classes for the rows the app works with."""

import sqlite3
from dataclasses import dataclass

MEMBER_ACTIVE = "active"
MEMBER_LEFT = "left"

EXPENSE_ACTIVE = "active"
EXPENSE_CANCELLED = "cancelled"

INCOME_DUES = "dues"
INCOME_DONATION = "donation"

INCOME_KIND_LABELS = {
    INCOME_DUES: "Quỹ tháng",
    INCOME_DONATION: "Ủng hộ",
}


@dataclass
class Member:
    id: int
    full_name: str
    student_code: str
    joined_on: str
    status: str
    left_on: str | None

    @property
    def is_active(self) -> bool:
        return self.status == MEMBER_ACTIVE

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Member":
        return cls(
            id=row["id"],
            full_name=row["full_name"],
            student_code=row["student_code"],
            joined_on=row["joined_on"],
            status=row["status"],
            left_on=row["left_on"],
        )


@dataclass
class Income:
    id: int
    received_on: str
    amount: int
    kind: str
    member_id: int | None
    dues_month: str | None
    note: str
    created_by: str
    member_name: str | None = None

    @property
    def kind_label(self) -> str:
        return INCOME_KIND_LABELS.get(self.kind, self.kind)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Income":
        keys = row.keys()
        return cls(
            id=row["id"],
            received_on=row["received_on"],
            amount=row["amount"],
            kind=row["kind"],
            member_id=row["member_id"],
            dues_month=row["dues_month"],
            note=row["note"],
            created_by=row["created_by"],
            member_name=row["member_name"] if "member_name" in keys else None,
        )


@dataclass
class Expense:
    id: int
    spent_on: str
    amount: int
    category: str
    description: str
    status: str
    created_by: str
    cancelled_on: str | None
    cancel_note: str | None

    @property
    def is_cancelled(self) -> bool:
        return self.status == EXPENSE_CANCELLED

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Expense":
        return cls(
            id=row["id"],
            spent_on=row["spent_on"],
            amount=row["amount"],
            category=row["category"],
            description=row["description"],
            status=row["status"],
            created_by=row["created_by"],
            cancelled_on=row["cancelled_on"],
            cancel_note=row["cancel_note"],
        )
