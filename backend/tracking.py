import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'jobs.db'
STATUSES = {'Not Applied', 'Applied', 'Interviewing', 'Offer', 'Rejected'}


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_tracking():
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS tracking (
            source TEXT NOT NULL,
            job_id TEXT NOT NULL,
            saved INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Not Applied',
            snapshot TEXT NOT NULL DEFAULT '{}',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(source, job_id)
        )''')


def list_tracking():
    with connect() as db:
        rows = db.execute('SELECT * FROM tracking ORDER BY updated_at DESC').fetchall()
    return [{**dict(row), 'saved': bool(row['saved']), 'job': json.loads(row['snapshot'])} for row in rows]


def update_tracking(source, job_id, saved, status, job):
    if status not in STATUSES:
        raise ValueError('Invalid application status')
    with connect() as db:
        db.execute('''INSERT INTO tracking(source,job_id,saved,status,snapshot,updated_at)
            VALUES(?,?,?,?,?,CURRENT_TIMESTAMP)
            ON CONFLICT(source,job_id) DO UPDATE SET
            saved=excluded.saved, status=excluded.status,
            snapshot=excluded.snapshot, updated_at=CURRENT_TIMESTAMP''',
            (source, job_id, int(saved), status, json.dumps(job)))
    return {'source': source, 'job_id': job_id, 'saved': saved, 'status': status}
