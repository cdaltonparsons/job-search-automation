from unittest.mock import patch, Mock
from scrappers.lever import fetch_lever

MOCK_RESPONSE = [
    {
        "text": "Angular Software Engineer",
        "hostedUrl": "https://jobs.lever.co/acme/abc-123",
        "createdAt": 1753920000000,  # Unix ms
        "categories": {"location": "Remote", "team": "Engineering"},
        "descriptionPlain": "Build Angular features for our platform.",
    },
    {
        "text": "Remote Data Engineer",
        "hostedUrl": "https://jobs.lever.co/acme/def-456",
        "createdAt": 1753920000000,
        "categories": {"location": "San Francisco, CA"},
        "descriptionPlain": "Python data pipelines.",
    },
]


def test_fetch_lever_fields():
    mock_resp = Mock()
    mock_resp.json.return_value = MOCK_RESPONSE

    with patch("scrappers.lever.requests.get", return_value=mock_resp):
        result = fetch_lever("acme")

    assert len(result) == 2
    job = result[0]
    assert job["title"] == "Angular Software Engineer"
    assert job["company"] == "acme"
    assert job["location"] == "Remote"
    assert job["url"] == "https://jobs.lever.co/acme/abc-123"
    assert job["source"] == "lever"


def test_fetch_lever_converts_timestamp():
    mock_resp = Mock()
    mock_resp.json.return_value = MOCK_RESPONSE

    with patch("scrappers.lever.requests.get", return_value=mock_resp):
        result = fetch_lever("acme")

    assert isinstance(result[0]["posted_date"], str)
    assert "T" in result[0]["posted_date"]


def test_fetch_lever_remote_from_location():
    mock_resp = Mock()
    mock_resp.json.return_value = MOCK_RESPONSE

    with patch("scrappers.lever.requests.get", return_value=mock_resp):
        result = fetch_lever("acme")

    assert result[0]["remote"] is True   # location is "Remote"


def test_fetch_lever_remote_from_title():
    mock_resp = Mock()
    mock_resp.json.return_value = MOCK_RESPONSE

    with patch("scrappers.lever.requests.get", return_value=mock_resp):
        result = fetch_lever("acme")

    # "Remote Data Engineer" — "remote" in title even though location is SF
    assert result[1]["remote"] is True
