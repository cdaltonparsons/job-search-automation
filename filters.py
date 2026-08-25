_PROVIDENCE_METRO = {
    "providence", "cranston", "warwick", "pawtucket", "woonsocket",
    "north providence", "east providence", "central falls", "johnston",
    "north smithfield", "smithfield", "lincoln", "Cumberland",
    # MA border towns ~30mi
    "attleboro", "north attleborough", "taunton", "fall river", "new bedford",
    "mansfield", "norton", "seekonk", "rehoboth", "swansea",
    # CT border
    "putnam", "plainfield",
    # state abbreviations that indicate RI/nearby MA/CT
    " ri", ", ri", " r.i.", "rhode island",
}

# Location strings that signal a non-US job we don't want
_NON_US_SIGNALS = {
    "london", "uk", "u.k.", "united kingdom", "england",
    "germany", "deutschland", "berlin", "munich", "münchen", "hamburg", "frankfurt",
    "amsterdam", "netherlands", "france", "paris",
    "spain", "madrid", "barcelona",
    "australia", "sydney", "melbourne",
    "canada", "toronto", "vancouver",
    "india", "bangalore", "bengaluru", "hyderabad",
    "singapore", "hong kong", "japan", "tokyo",
    "ireland", "dublin",
    "poland", "warsaw", "krakow",
    "portugal", "lisbon",
    "sweden", "stockholm",
    "norway", "oslo",
    "denmark", "copenhagen",
    "switzerland", "zurich",
    "austria", "vienna",
    "europe", "apac", "emea",
}


def _is_acceptable_location(job: dict) -> bool:
    """
    Return True if the job passes our location rules:
    - Remote jobs are OK as long as they don't signal a non-US location.
    - Non-remote jobs are OK only if the location is within the Providence metro (~30mi).
    - Jobs with no location info pass through (we can't be sure they're wrong).
    """
    location = (job.get("location") or "").lower().strip()
    is_remote = bool(job.get("remote"))

    # No location info — let it through
    if not location or location in ("", "remote"):
        return True

    # Check for non-US signals regardless of remote flag
    if any(signal in location for signal in _NON_US_SIGNALS):
        return False

    if is_remote:
        # Remote + no non-US signal → keep
        return True

    # On-site or hybrid — must be in Providence metro
    return any(metro in location for metro in _PROVIDENCE_METRO)


def filter_jobs(
    jobs: list[dict],
    min_score: int = 5,
    require_remote: bool = False,
    keywords: list[str] | None = None,
    location_filter: bool = True,
) -> list[dict]:
    """Filter jobs by score, remote flag, keywords, and location rules."""
    results = []
    for job in jobs:
        score = job["relevance_score"]
        if score is not None and score < min_score:
            continue
        if require_remote and not job["remote"]:
            continue
        if keywords:
            text = f"{job['title']} {job['description'] or ''}".lower()
            if not any(kw.lower() in text for kw in keywords):
                continue
        if location_filter and not _is_acceptable_location(job):
            continue
        results.append(job)
    return results
