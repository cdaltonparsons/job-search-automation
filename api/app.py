"""
FastAPI backend for the job search dashboard.

Run with:
    uvicorn api.app:app --reload
"""

import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB_PATH = Path(__file__).parent.parent / "jobs.db"

app = FastAPI(title="Job Search API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_methods=["*"],
    allow_headers=["*"],
)


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Models ────────────────────────────────────────────────────────────────────


class JobUpdate(BaseModel):
    seen: Optional[bool] = None
    applied: Optional[bool] = None
    notes: Optional[str] = None


# ── Routes ────────────────────────────────────────────────────────────────────


@app.get("/api/jobs")
def list_jobs(
    keyword: Optional[str] = None,
    min_score: int = 0,
    remote_only: bool = False,
    seen: Optional[bool] = None,
    applied: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Return jobs matching the given filters, ordered by relevance score descending."""
    conn = _conn()
    query = "SELECT * FROM jobs WHERE (relevance_score IS NULL OR relevance_score >= ?)"
    params: list = [min_score]

    if remote_only:
        query += " AND remote = 1"
    if seen is not None:
        query += " AND seen = ?"
        params.append(1 if seen else 0)
    if applied is not None:
        query += " AND applied = ?"
        params.append(1 if applied else 0)
    if keyword:
        query += " AND (title LIKE ? OR company LIKE ? OR description LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

    query += " ORDER BY relevance_score DESC NULLS LAST LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    return [dict(row) for row in conn.execute(query, params).fetchall()]


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    """Return a single job by ID."""
    conn = _conn()
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return dict(row)


@app.patch("/api/jobs/{job_id}")
def update_job(job_id: str, update: JobUpdate) -> dict:
    """Update seen, applied, or notes on a job."""
    conn = _conn()

    fields, values = [], []
    if update.seen is not None:
        fields.append("seen = ?")
        values.append(1 if update.seen else 0)
    if update.applied is not None:
        fields.append("applied = ?")
        values.append(1 if update.applied else 0)
    if update.notes is not None:
        fields.append("notes = ?")
        values.append(update.notes)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(job_id)
    conn.execute(f"UPDATE jobs SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()

    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return dict(row)


@app.get("/api/stats")
def get_stats() -> dict:
    """Quick summary counts for the dashboard header."""
    conn = _conn()
    total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    unseen = conn.execute("SELECT COUNT(*) FROM jobs WHERE seen = 0").fetchone()[0]
    applied = conn.execute("SELECT COUNT(*) FROM jobs WHERE applied = 1").fetchone()[0]
    scored = conn.execute(
        "SELECT AVG(relevance_score) FROM jobs WHERE relevance_score IS NOT NULL"
    ).fetchone()[0]
    return {
        "total": total,
        "unseen": unseen,
        "applied": applied,
        "avg_score": round(scored, 1) if scored else None,
    }
