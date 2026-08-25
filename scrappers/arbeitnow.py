import requests
from datetime import datetime, timezone


def fetch_arbeitnow() -> list[dict]:
    """Fetch jobs from the Arbeitnow public API. No auth required."""
    response = requests.get("https://www.arbeitnow.com/api/job-board-api")
    response.raise_for_status()

    jobs = []
    for item in response.json().get("data", []):
        salary_min = item.get("salary_min")
        salary_max = item.get("salary_max")
        salary = f"${salary_min} - ${salary_max}" if salary_min and salary_max else None

        # created_at is a Unix timestamp integer
        created_at = item.get("created_at")
        posted_date = (
            datetime.fromtimestamp(created_at, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            if created_at
            else None
        )

        jobs.append({
            "title": item.get("title"),
            "company": item.get("company_name"),
            "location": item.get("location") or "Remote",
            "url": item.get("url"),
            "posted_date": posted_date,
            "description": item.get("description"),
            "remote": bool(item.get("remote", False)),
            "salary": salary,
            "source": "arbeitnow",
        })

    return jobs
