from unittest.mock import patch, Mock
from scrappers.greenhouse import fetch_greenhouse

MOCK_RESPONSE = {
    "jobs": [
        {
            "title": "Senior Frontend Engineer",
            "location": {"name": "Remote"},
            "absolute_url": "https://boards.greenhouse.io/acme/jobs/123",
            "updated_at": "2026-08-01T10:00:00Z",
            "content": "<p>Build Angular apps.</p><ul><li>5+ years experience</li></ul>",
        },
        {
            "title": "Backend Engineer",
            "location": {"name": "New York, NY"},
            "absolute_url": "https://boards.greenhouse.io/acme/jobs/456",
            "updated_at": "2026-08-02T10:00:00Z",
            "content": "<p>Java services.</p>",
        },
    ]
}


def test_fetch_greenhouse_fields():
    mock_resp = Mock()
    mock_resp.json.return_value = MOCK_RESPONSE

    with patch("scrappers.greenhouse.requests.get", return_value=mock_resp):
        result = fetch_greenhouse("acme")

    assert len(result) == 2
    job = result[0]
    assert job["title"] == "Senior Frontend Engineer"
    assert job["company"] == "acme"
    assert job["location"] == "Remote"
    assert job["url"] == "https://boards.greenhouse.io/acme/jobs/123"
    assert job["source"] == "greenhouse"


def test_fetch_greenhouse_strips_html():
    mock_resp = Mock()
    mock_resp.json.return_value = MOCK_RESPONSE

    with patch("scrappers.greenhouse.requests.get", return_value=mock_resp):
        result = fetch_greenhouse("acme")

    assert "<p>" not in result[0]["description"]
    assert "Build Angular apps." in result[0]["description"]


def test_fetch_greenhouse_remote_flag():
    mock_resp = Mock()
    mock_resp.json.return_value = MOCK_RESPONSE

    with patch("scrappers.greenhouse.requests.get", return_value=mock_resp):
        result = fetch_greenhouse("acme")

    assert result[0]["remote"] is True   # "Remote" in location
    assert result[1]["remote"] is False  # "New York, NY"
