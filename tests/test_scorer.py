from unittest.mock import patch, Mock
from ai.scorer import score_job


def _mock_response(score: int) -> Mock:
    block = Mock()
    block.text = f'{{"score": {score}}}'
    response = Mock()
    response.content = [block]
    return response


def test_score_job_returns_integer():
    with patch("ai.scorer.client.messages.create", return_value=_mock_response(8)):
        result = score_job("Frontend Engineer", "We need an Angular developer.")
    assert result == 8
    assert isinstance(result, int)


def test_score_job_sends_title_and_description():
    with patch("ai.scorer.client.messages.create", return_value=_mock_response(3)) as mock_create:
        score_job("Data Scientist", "Python ML expertise required.")
    content = mock_create.call_args.kwargs["messages"][0]["content"]
    assert "Data Scientist" in content
    assert "Python ML expertise required." in content


def test_score_job_truncates_long_description():
    long_desc = "x" * 5000
    with patch("ai.scorer.client.messages.create", return_value=_mock_response(5)) as mock_create:
        score_job("Engineer", long_desc)
    content = mock_create.call_args.kwargs["messages"][0]["content"]
    assert len(content) < 3000
