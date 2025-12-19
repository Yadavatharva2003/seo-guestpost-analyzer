import sqlite3
from threading import Lock
from datetime import datetime

DB_FILE = "seo.db"

lock = Lock()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        niche TEXT,
        cms TEXT,
        submission_type TEXT,
        guest_post INTEGER,
        spam_risk TEXT,
        authority_score INTEGER,
        quality_tier TEXT,
        structure_group TEXT,
        index_status INTEGER,
        content_length INTEGER,
        load_time REAL,
        run_id TEXT,
        created_at TEXT
    );
    """)

    conn.commit()
    conn.close()


def save_result(data: dict):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    with lock:
        c.execute("""
            INSERT OR REPLACE INTO results (
                url, niche, cms, submission_type, guest_post,
                spam_risk, authority_score, quality_tier,
                structure_group, index_status, content_length,
                load_time, run_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["url"],
            data["niche"],
            data["cms"],
            data["submission_type"],
            1 if data["guest_post"] else 0,
            data["spam_risk"],
            data["authority_score"],
            data["quality_tier"],
            data["structure_group"],
            1 if data["index_status"] else 0,
            data["content_length"],
            data["load_time"],
            data.get("run_id"),
            datetime.utcnow().isoformat()
        ))

        conn.commit()

    conn.close()


def fetch_results(run_id=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    if run_id:
        c.execute("SELECT * FROM results WHERE run_id = ?", (run_id,))
    else:
        c.execute("SELECT * FROM results")

    rows = c.fetchall()
    conn.close()

    return rows
