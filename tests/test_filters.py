from filters import filter_jobs

JOB_A = {"id": "1", "title": "Angular Engineer", "company": "Acme", "location": "Remote",
          "description": "Build Angular components with TypeScript.", "remote": 1, "relevance_score": 9, "url": ""}
JOB_B = {"id": "2", "title": "Java Backend Developer", "company": "Corp", "location": "NYC",
          "description": "Spring Boot microservices.", "remote": 0, "relevance_score": 2, "url": ""}
JOB_C = {"id": "3", "title": "React Engineer", "company": "Startup", "location": "Remote",
          "description": "Build React SPAs.", "remote": 1, "relevance_score": 7, "url": ""}
JOB_D = {"id": "4", "title": "Frontend Engineer", "company": "BigCo", "location": "Chicago",
          "description": "Vue.js and some React.", "remote": 0, "relevance_score": None, "url": ""}

ALL_JOBS = [JOB_A, JOB_B, JOB_C, JOB_D]


def test_min_score_filters_low_scores():
    result = filter_jobs(ALL_JOBS, min_score=6, location_filter=False)
    ids = [j["id"] for j in result]
    assert "1" in ids  # score 9 — passes
    assert "3" in ids  # score 7 — passes
    assert "2" not in ids  # score 2 — filtered out


def test_unscored_jobs_pass_through():
    result = filter_jobs(ALL_JOBS, min_score=6, location_filter=False)
    ids = [j["id"] for j in result]
    assert "4" in ids  # score None — should pass through


def test_require_remote_filters_onsite():
    result = filter_jobs(ALL_JOBS, min_score=0, require_remote=True, location_filter=False)
    ids = [j["id"] for j in result]
    assert "1" in ids   # remote=1
    assert "3" in ids   # remote=1
    assert "2" not in ids  # remote=0
    assert "4" not in ids  # remote=0


def test_keyword_filter():
    result = filter_jobs(ALL_JOBS, min_score=0, keywords=["angular", "typescript"], location_filter=False)
    ids = [j["id"] for j in result]
    assert "1" in ids   # "Angular" in title, "TypeScript" in description
    assert "2" not in ids  # no match
    assert "3" not in ids  # React only


def test_empty_list_returns_empty():
    assert filter_jobs([]) == []


# Location filter tests

def _job(id, location, remote, score=8):
    return {"id": id, "title": "Eng", "company": "X", "location": location,
            "description": "", "remote": remote, "relevance_score": score, "url": ""}


def test_location_remote_us_passes():
    jobs = [_job("1", "Remote, US", 1), _job("2", "United States", 1)]
    result = filter_jobs(jobs, min_score=0)
    assert len(result) == 2


def test_location_remote_london_rejected():
    jobs = [_job("1", "London, UK", 1)]
    result = filter_jobs(jobs, min_score=0)
    assert len(result) == 0


def test_location_remote_germany_rejected():
    jobs = [_job("1", "Berlin, Germany", 1)]
    result = filter_jobs(jobs, min_score=0)
    assert len(result) == 0


def test_location_onsite_providence_passes():
    jobs = [_job("1", "Providence, RI", 0), _job("2", "Warwick, RI", 0)]
    result = filter_jobs(jobs, min_score=0)
    assert len(result) == 2


def test_location_onsite_boston_rejected():
    jobs = [_job("1", "Boston, MA", 0)]
    result = filter_jobs(jobs, min_score=0)
    assert len(result) == 0


def test_location_onsite_attleboro_passes():
    # ~20mi from Providence, inside the metro list
    jobs = [_job("1", "Attleboro, MA", 0)]
    result = filter_jobs(jobs, min_score=0)
    assert len(result) == 1


def test_location_empty_passes_through():
    jobs = [_job("1", "", 0), _job("2", None, 1)]
    result = filter_jobs(jobs, min_score=0)
    assert len(result) == 2


def test_location_filter_disabled():
    jobs = [_job("1", "London, UK", 1), _job("2", "Berlin, Germany", 0)]
    result = filter_jobs(jobs, min_score=0, location_filter=False)
    assert len(result) == 2
