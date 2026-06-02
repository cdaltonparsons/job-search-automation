from dataclasses import dataclass, field
from typing import Optional
import hashlib

@dataclass
class Job:
    id: str
    title: str
    company: str
    location: str
    url: str
    source: str
    posted_date: str
    description: str
    remote: bool = False
    seen: bool = False
    applied: bool = False
    notes: Optional[str] = None
    salary: Optional[str] = None

def normalize(raw: dict) -> Job:
    title = raw.get("title", "")
    company = raw.get("company", "")
    url = raw.get("url", "")
    location = raw.get("location", "")
    source = raw.get("source", "")
    posted_date = raw.get("posted_date", "")
    description = raw.get("description", "")
    remote = raw.get("remote", False)
    salary = raw.get("salary")
    notes = raw.get("notes")

    job_id = hashlib.md5(f"{title}{company}{url}".encode()).hexdigest()

    return Job(
        id=job_id,
        title=title,
        company=company,
        url=url,
        location=location,
        source=source,
        posted_date=posted_date,
        description=description,
        remote=remote,
        notes=notes,
        salary=salary
    )
