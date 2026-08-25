from unittest.mock import patch, Mock
from scrappers.remotive import fetch_remotive

MOCK_RESPONSE = {
    "jobs": [
        {
            "title": "Frontend Engineer",
            "company_name": "Remote Corp",
            "candidate_required_location": "Worldwide",
            "url": "https://remotive.com/remote-jobs/software-dev/frontend-123",
            "publication_date": "2026-08-01T09:00:00",
            "description": "React and TypeScript role.",
            "salary": "$100k - $130k",
        }
    ]
}


def test_fetch_remotive_fields():
    mock_resp = Mock()
    mock_resp.json.return_value = MOCK_RESPONSE

    with patch("scrappers.remotive.requests.get", return_value=mock_resp):
        result = fetch_remotive()

    assert len(result) == 1
    job = result[0]
    assert job["title"] == "Frontend Engineer"
    assert job["company"] == "Remote Corp"
    assert job["location"] == "Worldwide"
    assert job["remote"] is True
    assert job["salary"] == "$100k - $130k"
    assert job["source"] == "remotive"


def test_fetch_remotive_remote_always_true():
    mock_resp = Mock()
    mock_resp.json.return_value = MOCK_RESPONSE

    with patch("scrappers.remotive.requests.get", return_value=mock_resp):
        result = fetch_remotive()

    assert result[0]["remote"] is True


def test_fetch_remotive_empty_salary_becomes_none():
    mock_resp = Mock()
    mock_resp.json.return_value = {
        "jobs": [{**MOCK_RESPONSE["jobs"][0], "salary": ""}]
    }

    with patch("scrappers.remotive.requests.get", return_value=mock_resp):
        result = fetch_remotive()

    assert result[0]["salary"] is None
