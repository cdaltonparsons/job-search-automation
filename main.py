from db.database import get_connection, init_db, insert_job, update_job_score
from normalizer import normalize
from scrappers.rss import fetch_rss_feed
from scrappers.usajobs import fetch_usajobs
from scrappers.indeed import fetch_indeed
from scrappers.linkedin import fetch_linkedin
from scrappers.arbeitnow import fetch_arbeitnow
from scrappers.remotive import fetch_remotive
from scrappers.remoteok import fetch_remoteok
from scrappers.greenhouse import fetch_greenhouse
from scrappers.lever import fetch_lever
from ai.scorer import score_job
from filters import filter_jobs
from digest import run_digest

RSS_FEEDS = [
    # Add RSS feed URLs here, e.g. LinkedIn/Indeed search results
]

USAJOBS_KEYWORDS = [
    "angular developer",
    "frontend engineer",
    "full stack typescript",
]

INDEED_KEYWORDS = [
    "angular developer",
    "frontend engineer typescript",
]

LINKEDIN_KEYWORDS = [
    "angular developer",
]

# ATS company slugs — find these in the URL of a company's job board:
#   Greenhouse: boards.greenhouse.io/{slug}
#   Lever:      jobs.lever.co/{slug}
GREENHOUSE_COMPANIES: list[str] = [
    # e.g. "notion", "figma", "stripe", "discord", "airbnb"
]

LEVER_COMPANIES: list[str] = [
    # e.g. "netflix", "reddit", "robinhood", "coinbase"
]

DB_PATH = "jobs.db"


def run_pipeline():
    conn = get_connection(DB_PATH)
    init_db(conn)

    raw_jobs = []

    for url in RSS_FEEDS:
        try:
            jobs = fetch_rss_feed(url)
            raw_jobs.extend(jobs)
            print(f"RSS: {len(jobs)} jobs from {url}")
        except Exception as e:
            print(f"RSS error ({url}): {e}")

    for keyword in USAJOBS_KEYWORDS:
        try:
            jobs = fetch_usajobs(keyword)
            raw_jobs.extend(jobs)
            print(f"USAJobs '{keyword}': {len(jobs)} jobs")
        except Exception as e:
            print(f"USAJobs error ({keyword}): {e}")

    for keyword in INDEED_KEYWORDS:
        try:
            jobs = fetch_indeed(keyword)
            raw_jobs.extend(jobs)
        except Exception as e:
            print(f"Indeed error ({keyword}): {e}")

    for keyword in LINKEDIN_KEYWORDS:
        try:
            jobs = fetch_linkedin(keyword)
            raw_jobs.extend(jobs)
        except Exception as e:
            print(f"LinkedIn error ({keyword}): {e}")

    for company in GREENHOUSE_COMPANIES:
        try:
            jobs = fetch_greenhouse(company)
            raw_jobs.extend(jobs)
            print(f"Greenhouse '{company}': {len(jobs)} jobs")
        except Exception as e:
            print(f"Greenhouse error ({company}): {e}")

    for company in LEVER_COMPANIES:
        try:
            jobs = fetch_lever(company)
            raw_jobs.extend(jobs)
            print(f"Lever '{company}': {len(jobs)} jobs")
        except Exception as e:
            print(f"Lever error ({company}): {e}")

    try:
        jobs = fetch_arbeitnow()
        raw_jobs.extend(jobs)
        print(f"Arbeitnow: {len(jobs)} jobs")
    except Exception as e:
        print(f"Arbeitnow error: {e}")

    try:
        jobs = fetch_remotive()
        raw_jobs.extend(jobs)
        print(f"Remotive: {len(jobs)} jobs")
    except Exception as e:
        print(f"Remotive error: {e}")

    try:
        jobs = fetch_remoteok()
        raw_jobs.extend(jobs)
        print(f"RemoteOK: {len(jobs)} jobs")
    except Exception as e:
        print(f"RemoteOK error: {e}")

    for raw in raw_jobs:
        job = normalize(raw)
        insert_job(conn, job)

    print(f"\nFetched {len(raw_jobs)} jobs total (duplicates ignored)")

    unscored = conn.execute(
        "SELECT id, title, description FROM jobs WHERE relevance_score IS NULL"
    ).fetchall()

    print(f"Scoring {len(unscored)} new jobs...\n")
    for row in unscored:
        try:
            score = score_job(row["title"], row["description"] or "")
            update_job_score(conn, row["id"], score)
            print(f"  [{score:>2}/10] {row['title']}")
        except Exception as e:
            print(f"  Error scoring '{row['title']}': {e}")

    # Fetch all unseen, scored jobs and run the digest
    new_jobs = conn.execute(
        "SELECT * FROM jobs WHERE seen = 0 AND relevance_score IS NOT NULL ORDER BY relevance_score DESC"
    ).fetchall()

    filtered = filter_jobs(new_jobs, min_score=6, require_remote=False)
    print(f"{len(filtered)} jobs passed filters (of {len(new_jobs)} unseen).")

    run_digest(conn, filtered)

    print("\nDone.")


if __name__ == "__main__":
    run_pipeline()
