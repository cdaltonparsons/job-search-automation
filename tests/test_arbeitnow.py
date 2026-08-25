from unittest.mock import patch, Mock
from scrappers.arbeitnow import fetch_arbeitnow

MOCK_RESPONSE = {
    "data": [
        {
            "title": "Senior Angular Engineer",
            "company_name": "Acme GmbH",
            "location": "Berlin, Germany",
            "url": "https://www.arbeitnow.com/jobs/acme/angular-engineer",
            "description": "Build Angular applications.",
            "remote": True,
            "created_at": 1750000000,
            "salary_min": 90000,
            "salary_max": 120000,
        }
    ]
}


def test_fetch_arbeitnow_fields():
    mock_resp = Mock()
    mock_resp.json.return_value = MOCK_RESPONSE

    with patch("scrappers.arbeitnow.requests.get", return_value=mock_resp):
        result = fetch_arbeitnow()

    assert len(result) == 1
    job = result[0]
    assert job["title"] == "Senior Angular Engineer"
    assert job["company"] == "Acme GmbH"
    assert job["location"] == "Berlin, Germany"
    assert job["remote"] is True
    assert job["source"] == "arbeitnow"
    assert job["salary"] == "$90000 - $120000"


def test_fetch_arbeitnow_converts_timestamp():
    mock_resp = Mock()
    mock_resp.json.return_value = MOCK_RESPONSE

    with patch("scrappers.arbeitnow.requests.get", return_value=mock_resp):
        result = fetch_arbeitnow()

    # Should be an ISO 8601 string, not a raw integer
    assert isinstance(result[0]["posted_date"], str)
    assert "T" in result[0]["posted_date"]


def test_fetch_arbeitnow_no_salary():
    mock_resp = Mock()
    mock_resp.json.return_value = {
        "data": [{**MOCK_RESPONSE["data"][0], "salary_min": None, "salary_max": None}]
    }

    with patch("scrappers.arbeitnow.requests.get", return_value=mock_resp):
        result = fetch_arbeitnow()

    assert result[0]["salary"] is None
