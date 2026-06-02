import sqlite3
from pathlib import Path
from normalizer import Job

def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    schema_path = Path(__file__).parent / "schema.sql"
    sql = schema_path.read_text()
    conn.executescript(sql)


def insert_job(conn: sqlite3.Connection, job: Job) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO jobs (id, title, company, url, location, posted_date, description, source, remote, seen, applied, salary, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (job.id, job.title, job.company, job.url, job.location, job.posted_date, job.description, job.source, job.remote, job.seen, job.applied, job.salary, job.notes)
    )
    conn.commit()

