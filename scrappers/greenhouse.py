import re
import requests


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "").strip()


def fetch_greenhouse(company: str) -> list[dict]:
    """
    Fetch all open roles from a company's Greenhouse job board.
    `company` is the slug from boards.greenhouse.io/{company}
    """
    response = requests.get(
        f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs",
        params={"content": "true"},
    )
    response.raise_for_status()

    jobs = []
    for item in response.json().get("jobs", []):
        location_name = (item.get("location") or {}).get("name") or "Remote"
        jobs.append({
            "title": item.get("title"),
            "company": company,
            "location": location_name,
            "url": item.get("absolute_url"),
            "posted_date": item.get("updated_at"),
            "description": _strip_html(item.get("content")),
            "remote": "remote" in location_name.lower(),
            "salary": None,
            "source": "greenhouse",
        })

    return jobs
