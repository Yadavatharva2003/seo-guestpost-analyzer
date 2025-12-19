import sqlite3
import os

DB_PATH = "database.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            url TEXT,
            niche TEXT,
            cms TEXT,
            submission TEXT,
            authority REAL,
            spam REAL,
            category TEXT,
            structure TEXT,
            tier TEXT
        );
    """)
    conn.commit()
    conn.close()


def save_result(run_id: str, result: dict):
    init_db()  # ensure table exists

    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO results (
            run_id, url, niche, cms, submission,
            authority, spam, category, structure, tier
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_id,
        result.get("url"),
        result.get("niche"),
        result.get("cms"),
        result.get("submission"),
        result.get("authority"),
        result.get("spam"),
        result.get("category"),
        result.get("structure"),
        result.get("tier"),
    ))
    conn.commit()
    conn.close()


def fetch_results(run_id):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT * FROM results WHERE run_id = ?", (run_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
