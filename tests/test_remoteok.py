from unittest.mock import patch, Mock
from scrappers.remoteok import fetch_remoteok

# First element is API metadata (skipped), second is a real job
MOCK_RESPONSE = [
    {"legal": "RemoteOK API"},
    {
        "position": "TypeScript Developer",
        "company": "StartupCo",
        "location": "Remote",
        "url": "https://remoteok.com/jobs/12345",
        "date": "2026-08-10T12:00:00Z",
        "description": "Build TypeScript microservices.",
        "salary_min": 110000,
        "salary_max": 150000,
    },
]


def test_fetch_remoteok_skips_metadata():
    mock_resp = Mock()
    mock_resp.json.return_value = MOCK_RESPONSE

    with patch("scrappers.remoteok.requests.get", return_value=mock_resp):
        result = fetch_remoteok()

    # Should return 1 job, not 2 (metadata element is skipped)
    assert len(result) == 1


def test_fetch_remoteok_fields():
    mock_resp = Mock()
    mock_resp.json.return_value = MOCK_RESPONSE

    with patch("scrappers.remoteok.requests.get", return_value=mock_resp):
        result = fetch_remoteok()

    job = result[0]
    assert job["title"] == "TypeScript Developer"
    assert job["company"] == "StartupCo"
    assert job["remote"] is True
    assert job["salary"] == "$110000 - $150000"
    assert job["source"] == "remoteok"


def test_fetch_remoteok_no_salary():
    mock_resp = Mock()
    mock_resp.json.return_value = [
        {"legal": "meta"},
        {**MOCK_RESPONSE[1], "salary_min": None, "salary_max": None},
    ]

    with patch("scrappers.remoteok.requests.get", return_value=mock_resp):
        result = fetch_remoteok()

    assert result[0]["salary"] is None
