import requests
from datetime import datetime, timezone


def fetch_lever(company: str) -> list[dict]:
    """
    Fetch all open roles from a company's Lever job board.
    `company` is the slug from jobs.lever.co/{company}
    """
    response = requests.get(
        f"https://api.lever.co/v0/postings/{company}",
        params={"mode": "json"},
    )
    response.raise_for_status()

    jobs = []
    for item in response.json():
        # createdAt is Unix milliseconds
        created_at = item.get("createdAt")
        posted_date = (
            datetime.fromtimestamp(created_at / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            if created_at
            else None
        )

        categories = item.get("categories") or {}
        location = categories.get("location") or "Remote"
        title = item.get("text") or ""

        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "url": item.get("hostedUrl"),
            "posted_date": posted_date,
            "description": item.get("descriptionPlain") or item.get("description") or "",
            "remote": "remote" in location.lower() or "remote" in title.lower(),
            "salary": None,
            "source": "lever",
        })

    return jobs
