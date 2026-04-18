import sqlite3
from datetime import datetime

def init_database(db_path: str = "assistant.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS user_profile (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        key         TEXT NOT NULL UNIQUE,
        value       TEXT NOT NULL,
        category    TEXT DEFAULT 'lainnya',
        updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS routines (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        activity     TEXT NOT NULL,
        category     TEXT DEFAULT 'hobi',
        logged_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
        duration_min INTEGER,
        notes        TEXT,
        mood_score   INTEGER CHECK(mood_score BETWEEN 1 AND 5)
    );

    CREATE TABLE IF NOT EXISTS agendas (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        title        TEXT NOT NULL,
        scheduled_at DATETIME NOT NULL,
        importance   TEXT DEFAULT 'sedang',
        notified     BOOLEAN DEFAULT 0,
        notes        TEXT
    );

    CREATE TABLE IF NOT EXISTS conversations (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        role       TEXT NOT NULL CHECK(role IN ('user','assistant')),
        content    TEXT NOT NULL,
        timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP,
        session_id TEXT
    );

    CREATE TABLE IF NOT EXISTS checkpoints (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        topic       TEXT NOT NULL,
        context     TEXT,
        followup_at DATETIME,
        resolved    BOOLEAN DEFAULT 0
    );
    """)

    conn.commit()
    conn.close()
    print("✅ Database berhasil diinisialisasi.")
