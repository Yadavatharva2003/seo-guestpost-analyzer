import sqlite3
from datetime import datetime

conn = sqlite3.connect("seo_runs.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS results (
    run_id TEXT,
    domain TEXT,
    score INTEGER,
    tier TEXT,
    created_at TEXT
)
""")
conn.commit()

def save_result(run_id, domain, score, tier):
    c.execute(
        "INSERT INTO results VALUES (?,?,?,?,?)",
        (run_id, domain, score, tier, datetime.utcnow().isoformat())
    )
    conn.commit()
