import json
import re
import time
import anthropic

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a job relevance scorer for a frontend/full-stack software engineer
with expertise in Angular and TypeScript. Score the job listing 0-10:

10: Perfect - Angular, TypeScript, or modern frontend/full-stack
7-9: Strong - general frontend, React/Vue, full-stack JS/TS
4-6: Partial - general web dev, adjacent tech, some frontend component
1-3: Weak - primarily backend, unrelated stack, or tangential role
0: Irrelevant - non-engineering, data science, QA-only

Respond with ONLY valid JSON: {"score": <integer 0-10>}"""


def score_job(title: str, description: str) -> int:
    """Score a single job listing's relevance on a 0-10 scale using Claude."""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Title: {title}\n\nDescription: {description[:2000]}"
        }]
    )
    raw = response.content[0].text if response.content else ""
    match = re.search(r'\{[^}]+\}', raw)
    if not match:
        raise ValueError(f"No JSON object in response: {raw!r}")
    result = json.loads(match.group())
    return result["score"]


def batch_score_jobs(jobs: list[tuple[str, str, str]]) -> str:
    """
    Submit many jobs to the Batch API in one request.
    jobs: list of (job_id, title, description)
    Returns batch_id — pass to collect_batch_scores() once processing is complete.
    """
    requests = [
        {
            "custom_id": job_id,
            "params": {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 64,
                "system": SYSTEM_PROMPT,
                "messages": [{
                    "role": "user",
                    "content": f"Title: {title}\n\nDescription: {description[:2000]}"
                }],
            },
        }
        for job_id, title, description in jobs
    ]
    batch = client.messages.batches.create(requests=requests)
    print(f"Batch submitted: {batch.id} ({len(jobs)} jobs)")
    return batch.id


def collect_batch_scores(batch_id: str, poll_interval: int = 10) -> dict[str, int]:
    """
    Poll until the batch is complete, then return {job_id: score} for all succeeded results.
    Blocks until done — run this in a background process or scheduled job for large batches.
    """
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status == "ended":
            break
        counts = batch.request_counts
        print(f"  Batch {batch_id}: {counts.processing} processing, {counts.succeeded} done...")
        time.sleep(poll_interval)

    scores: dict[str, int] = {}
    for result in client.messages.batches.results(batch_id):
        if result.result.type == "succeeded":
            try:
                parsed = json.loads(result.result.message.content[0].text)
                scores[result.custom_id] = parsed["score"]
            except (json.JSONDecodeError, KeyError):
                pass
    return scores
