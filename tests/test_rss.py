from unittest.mock import patch, Mock
from scrappers.rss import fetch_rss_feed

def test_fetch_rss_feed():
    mock_response = Mock()
    mock_response.text = "<?xml version='1.0'?><rss><channel><item><title>Software Engineer</title><link>https://acme.com/jobs/1</link><description>Build cool things.</description><pubDate>2026-06-01</pubDate></item></channel></rss>"

    with patch("scrappers.rss.requests.get", return_value=mock_response):
        result = fetch_rss_feed("http://fake-url.com/rss")
    
    assert result[0]["title"] == "Software Engineer"
    assert result[0]["url"] == "https://acme.com/jobs/1"
    assert result[0]["description"] == "Build cool things."
    assert result[0]["posted_date"] == "2026-06-01"
    assert result[0]["source"] == "rss"