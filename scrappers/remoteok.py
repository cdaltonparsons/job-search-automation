import requests


def fetch_remoteok() -> list[dict]:
    """Fetch jobs from the RemoteOK public API. No auth required."""
    # RemoteOK blocks the default requests User-Agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    response = requests.get("https://remoteok.com/api", headers=headers)
    response.raise_for_status()

    raw = response.json()
    jobs = []
    # First element is API metadata, not a job listing
    for item in raw[1:]:
        salary_min = item.get("salary_min")
        salary_max = item.get("salary_max")
        salary = f"${salary_min} - ${salary_max}" if salary_min and salary_max else None

        jobs.append({
            "title": item.get("position"),
            "company": item.get("company"),
            "location": item.get("location") or "Remote",
            "url": item.get("url"),
            "posted_date": item.get("date"),
            "description": item.get("description"),
            "remote": True,  # RemoteOK listings are remote by definition
            "salary": salary,
            "source": "remoteok",
        })

    return jobs
