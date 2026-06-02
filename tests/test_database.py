from normalizer import normalize
from db.database import get_connection, init_db, insert_job

def test_insert_job():
    conn = get_connection(":memory:")
    init_db(conn)

    raw = {"title": "Software Engineer", "company": "Acme", "url": "https://acme.com/jobs/1"}
    job = normalize(raw)
    insert_job(conn, job)

    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job.id,)).fetchone()
    assert row is not None
    assert row["title"] == "Software Engineer"

def test_insert_job_deduplication():
    conn = get_connection(":memory:")
    init_db(conn)

    raw = {"title": "Software Engineer", "company": "Acme", "url": "https://acme.com/jobs/1"}
    job = normalize(raw)
    insert_job(conn, job)
    insert_job(conn, job)  # second insert — should be ignored

    count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    assert count == 1
