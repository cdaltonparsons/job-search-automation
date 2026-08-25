import os
import smtplib
import sqlite3
from email.mime.text import MIMEText

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a career coach helping a frontend/full-stack engineer (Angular, TypeScript) with their job search.
Given a list of today's top job matches, write a short editorial digest (3-5 sentences):
- Lead with the most exciting role and why it stands out
- Note any patterns (multiple companies hiring, remote-friendly clusters, common tech stacks, etc.)
- End with one sentence of encouragement or a tactical tip
Keep the tone warm, honest, and brief. No bullet points — flowing prose only."""


def build_narrative(jobs: list[dict]) -> str:
    """Ask Claude to write a short editorial summary of the day's best job matches."""
    if not jobs:
        return "No new matching jobs found today."

    job_summaries = [
        f"- {job['title']} at {job['company']} ({job['location']}) — Score: {job['relevance_score']}/10"
        for job in jobs[:10]
    ]
    prompt = "Today's top job matches:\n" + "\n".join(job_summaries)

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def send_email(jobs: list[dict], narrative: str) -> None:
    """Send the digest as a plain-text email via Gmail SMTP."""
    from_addr = os.getenv("ALERT_EMAIL_FROM")
    to_addr = os.getenv("ALERT_EMAIL_TO")
    password = os.getenv("ALERT_EMAIL_PASSWORD")

    if not all([from_addr, to_addr, password]):
        print(
            "Email skipped — set ALERT_EMAIL_FROM, ALERT_EMAIL_TO, "
            "ALERT_EMAIL_PASSWORD in .env to enable delivery."
        )
        return

    job_lines = "\n".join(
        f"  [{job['relevance_score']:>2}/10] {job['title']} — {job['company']} ({job['location']})\n"
        f"         {job['url']}"
        for job in jobs
    )
    body = f"{narrative}\n\n---\n\nAll {len(jobs)} matches:\n\n{job_lines}"

    msg = MIMEText(body)
    msg["Subject"] = f"Job Digest — {len(jobs)} new matches"
    msg["From"] = from_addr
    msg["To"] = to_addr

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_addr, password)
        smtp.send_message(msg)

    print(f"Digest emailed to {to_addr}")


def run_digest(conn: sqlite3.Connection, jobs: list[dict]) -> None:
    """Build the narrative, print it, send it, and mark all jobs as seen."""
    if not jobs:
        print("No new jobs to digest.")
        return

    narrative = build_narrative(jobs)
    print(f"\n--- Today's Digest ---\n{narrative}\n")

    send_email(jobs, narrative)

    ids = [job["id"] for job in jobs]
    placeholders = ",".join("?" * len(ids))
    conn.execute(f"UPDATE jobs SET seen = 1 WHERE id IN ({placeholders})", ids)
    conn.commit()
    print(f"Marked {len(ids)} jobs as seen.")
