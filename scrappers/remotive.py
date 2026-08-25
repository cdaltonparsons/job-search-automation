import requests


def fetch_remotive(category: str = "software-dev") -> list[dict]:
    """Fetch remote jobs from the Remotive public API. No auth required."""
    response = requests.get(
        "https://remotive.com/api/remote-jobs",
        params={"category": category},
    )
    response.raise_for_status()

    jobs = []
    for item in response.json().get("jobs", []):
        jobs.append({
            "title": item.get("title"),
            "company": item.get("company_name"),
            "location": item.get("candidate_required_location") or "Remote",
            "url": item.get("url"),
            "posted_date": item.get("publication_date"),
            "description": item.get("description"),
            "remote": True,  # Remotive lists are remote by definition
            "salary": item.get("salary") or None,
            "source": "remotive",
        })

    return jobs
