from dataclasses import dataclass, field
from typing import Optional

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
