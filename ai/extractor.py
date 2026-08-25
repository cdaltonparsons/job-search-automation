import json
import anthropic

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a job listing data extractor. Given raw HTML from a job listing page,
extract the structured data and return it as JSON matching this exact schema:

{
    "title": "string - the job title",
    "company": "string - the company name",
    "location": "string - city/state or 'Remote'",
    "description": "string - the full job description",
    "salary": "string or null - salary range if listed, otherwise null",
    "remote": true or false
}

Return ONLY the JSON object, no other text. If a field cannot be determined, use an empty
string for strings and false for booleans (except salary, which should be null)."""


def extract_job_from_html(html: str, url: str = "") -> dict:
    """Extract job fields from raw HTML using Claude. Returns a raw job dict."""
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"URL: {url}\n\nHTML:\n{html[:10000]}"
        }]
    )
    result = json.loads(response.content[0].text)
    result["url"] = url
    result["source"] = "playwright"
    return result
