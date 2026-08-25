"""
CLI for interactive job search features.

Usage:
    python cli.py ask "find me remote Angular jobs with a score above 7"
    python cli.py cover <job_id>
    python cli.py gap <job_id>
    python cli.py batch-score
"""

import sys
from db.database import get_connection, update_job_score

DB_PATH = "jobs.db"

RESUME_PATH = "resume.txt"


def _load_resume() -> str:
    try:
        with open(RESUME_PATH) as f:
            return f.read()
    except FileNotFoundError:
        print(f"Resume not found. Create {RESUME_PATH} with your resume text.")
        sys.exit(1)


def _get_job(conn, job_id: str) -> dict:
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not row:
        print(f"Job {job_id!r} not found.")
        sys.exit(1)
    return dict(row)


def cmd_ask(query: str) -> None:
    """Agent: ask a natural-language question about your saved jobs."""
    from ai.agent import run_job_search_agent
    conn = get_connection(DB_PATH)
    answer = run_job_search_agent(conn, query)
    print(f"\n{answer}")


def cmd_cover(job_id: str) -> None:
    """Stream a tailored cover letter for a saved job."""
    from ai.cover_letter import generate_cover_letter
    conn = get_connection(DB_PATH)
    job = _get_job(conn, job_id)
    resume = _load_resume()
    generate_cover_letter(resume, job["title"], job["company"], job["description"] or "")


def cmd_gap(job_id: str) -> None:
    """Stream a gap analysis between your resume and a saved job."""
    from ai.cover_letter import analyze_gap
    conn = get_connection(DB_PATH)
    job = _get_job(conn, job_id)
    resume = _load_resume()
    analyze_gap(resume, job["title"], job["description"] or "")


def cmd_batch_score() -> None:
    """Batch-score all unscored jobs using the Anthropic Batch API."""
    from ai.scorer import batch_score_jobs, collect_batch_scores
    conn = get_connection(DB_PATH)
    rows = conn.execute(
        "SELECT id, title, description FROM jobs WHERE relevance_score IS NULL"
    ).fetchall()

    if not rows:
        print("No unscored jobs.")
        return

    jobs = [(row["id"], row["title"], row["description"] or "") for row in rows]
    print(f"Submitting {len(jobs)} jobs to Batch API...")
    batch_id = batch_score_jobs(jobs)

    print("Waiting for batch to complete...")
    scores = collect_batch_scores(batch_id)

    for job_id, score in scores.items():
        update_job_score(conn, job_id, score)
        print(f"  [{score:>2}/10] {job_id}")

    print(f"\nScored {len(scores)} jobs.")


COMMANDS = {
    "ask": (cmd_ask, 1, "\"<question>\""),
    "cover": (cmd_cover, 1, "<job_id>"),
    "gap": (cmd_gap, 1, "<job_id>"),
    "batch-score": (cmd_batch_score, 0, ""),
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Usage:")
        for name, (_, _, args) in COMMANDS.items():
            print(f"  python cli.py {name} {args}")
        sys.exit(1)

    cmd, fn, min_args, _ = sys.argv[1], *COMMANDS[sys.argv[1]]
    extra_args = sys.argv[2:]

    if len(extra_args) < min_args:
        print(f"Usage: python cli.py {cmd} {COMMANDS[cmd][2]}")
        sys.exit(1)

    fn(*extra_args)
