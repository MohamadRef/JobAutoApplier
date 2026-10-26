import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs.db"


def connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT,
                source TEXT,
                title TEXT,
                company TEXT,
                location TEXT,
                url TEXT,
                PRIMARY KEY (id, source)
            )
        """)


def save_jobs(jobs):
    with connect() as conn:
        for job in jobs:
            conn.execute("""
                INSERT OR REPLACE INTO jobs
                (id, source, title, company, location, url)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                job["id"],
                job["source"],
                job["title"],
                job["company"],
                json.dumps(job["location"]),
                job["url"]
            ))


def get_saved_jobs():
    with connect() as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY company, title"
        ).fetchall()

    jobs = []

    for row in rows:
        job = dict(row)
        job["location"] = json.loads(job["location"])
        jobs.append(job)

    return jobs