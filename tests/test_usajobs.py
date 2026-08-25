from unittest.mock import patch, Mock
from scrappers.usajobs import fetch_usajobs

def test_fetch_usajobs():
    mock_response = Mock()
    mock_response.json.return_value = {
        "SearchResult": {
            "SearchResultItems": [
                {
                    "MatchedObjectDescriptor": {
                        "PositionTitle": "Software Engineer",
                        "OrganizationName": "Acme Agency",
                        "PositionLocation": [{"LocationName": "Remote"}],
                        "PositionURI": "https://usajobs.gov/job/1",
                        "PublicationStartDate": "2026-07-01",
                        "UserArea": {
                            "Details": {
                                "JobSummary": "Build cool things.",
                                "RemoteIndicator": True
                            }
                        },
                        "PositionRemuneration": [{"MinimumRange": "120000"}]
                    }
                }
            ]
        }
    }

    with patch("scrappers.usajobs.requests.get", return_value=mock_response):
        result = fetch_usajobs("software engineer")

    assert len(result) == 1
    assert result[0]["title"] == "Software Engineer"
    assert result[0]["company"] == "Acme Agency"
    assert result[0]["location"] == "Remote"
    assert result[0]["url"] == "https://usajobs.gov/job/1"
    assert result[0]["posted_date"] == "2026-07-01"
    assert result[0]["description"] == "Build cool things."
    assert result[0]["remote"] == True
    assert result[0]["salary"] == "120000"
