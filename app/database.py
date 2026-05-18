import sqlite3
from pathlib import Path

DB_PATH = Path("/app/data/timeline.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS clients (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                goal        TEXT,
                start_date  TEXT,
                goal_date   TEXT,
                start_weight REAL,
                date_of_birth TEXT,
                contact_email TEXT,
                contact_phone TEXT,
                notes       TEXT,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS entries (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id           INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
                week_number         INTEGER NOT NULL,
                date                TEXT,
                phase               TEXT,
                calories            INTEGER,
                cardio              TEXT,
                steps               INTEGER,
                training_specifics  TEXT,
                goals_expectations  TEXT,
                notes               TEXT,
                created_at          TEXT    NOT NULL DEFAULT (datetime('now'))
            );
        """)
        # Migration: add start_date and goal_date columns
        cols = [row[1] for row in conn.execute("PRAGMA table_info(clients)").fetchall()]
        if "start_date" not in cols:
            conn.execute("ALTER TABLE clients ADD COLUMN start_date TEXT")
        if "goal_date" not in cols:
            conn.execute("ALTER TABLE clients ADD COLUMN goal_date TEXT")
    conn.close()
