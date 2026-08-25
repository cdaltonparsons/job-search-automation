from unittest.mock import patch, Mock
from ai.extractor import extract_job_from_html

SAMPLE_HTML = """
<html><body>
  <h1 class="job-title">Senior Angular Engineer</h1>
  <div class="company-name">Acme Corp</div>
  <div class="location">Remote</div>
  <div class="salary-range">$120,000 - $160,000</div>
  <div class="description">
    We are looking for a Senior Angular Engineer to join our team.
    You will build scalable frontend features using Angular and TypeScript.
  </div>
</body></html>
"""

EXTRACTED = {
    "title": "Senior Angular Engineer",
    "company": "Acme Corp",
    "location": "Remote",
    "description": "We are looking for a Senior Angular Engineer...",
    "salary": "$120,000 - $160,000",
    "remote": True,
}


def _mock_response(data: dict) -> Mock:
    import json
    block = Mock()
    block.text = json.dumps(data)
    response = Mock()
    response.content = [block]
    return response


def test_extract_returns_expected_fields():
    with patch("ai.extractor.client.messages.create", return_value=_mock_response(EXTRACTED)):
        result = extract_job_from_html(SAMPLE_HTML, url="https://acme.com/jobs/1")

    assert result["title"] == "Senior Angular Engineer"
    assert result["company"] == "Acme Corp"
    assert result["remote"] is True
    assert result["salary"] == "$120,000 - $160,000"


def test_extract_injects_url_and_source():
    with patch("ai.extractor.client.messages.create", return_value=_mock_response(EXTRACTED)):
        result = extract_job_from_html(SAMPLE_HTML, url="https://acme.com/jobs/1")

    assert result["url"] == "https://acme.com/jobs/1"
    assert result["source"] == "playwright"


def test_extract_truncates_large_html():
    large_html = "<html>" + ("x" * 20000) + "</html>"
    with patch("ai.extractor.client.messages.create", return_value=_mock_response(EXTRACTED)) as mock_create:
        extract_job_from_html(large_html)

    sent_content = mock_create.call_args.kwargs["messages"][0]["content"]
    assert len(sent_content) < 12000
