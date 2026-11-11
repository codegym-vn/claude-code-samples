CREATE TABLE IF NOT EXISTS members (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name    TEXT    NOT NULL,
    student_code TEXT    NOT NULL UNIQUE,
    joined_on    TEXT    NOT NULL,
    status       TEXT    NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'left')),
    left_on      TEXT
);

CREATE TABLE IF NOT EXISTS incomes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    received_on TEXT    NOT NULL,
    amount      INTEGER NOT NULL CHECK (amount > 0),
    kind        TEXT    NOT NULL CHECK (kind IN ('dues', 'donation')),
    member_id   INTEGER REFERENCES members (id),
    dues_month  TEXT,
    note        TEXT    NOT NULL DEFAULT '',
    created_by  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS expenses (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    spent_on     TEXT    NOT NULL,
    amount       INTEGER NOT NULL CHECK (amount > 0),
    category     TEXT    NOT NULL,
    description  TEXT    NOT NULL,
    status       TEXT    NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled')),
    created_by   TEXT    NOT NULL,
    cancelled_on TEXT,
    cancel_note  TEXT
);

CREATE INDEX IF NOT EXISTS idx_incomes_received_on ON incomes (received_on);
CREATE INDEX IF NOT EXISTS idx_incomes_dues_month ON incomes (dues_month);
CREATE INDEX IF NOT EXISTS idx_expenses_spent_on ON expenses (spent_on);
