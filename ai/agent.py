import json
import sqlite3

import anthropic

client = anthropic.Anthropic()

SEARCH_JOBS_TOOL = {
    "name": "search_jobs",
    "description": "Search the local job database for listings matching a keyword.",
    "input_schema": {
        "type": "object",
        "properties": {
            "keyword": {
                "type": "string",
                "description": "Search term matched against job title and description",
            },
            "min_score": {
                "type": "integer",
                "description": "Minimum relevance score 0-10 (default 5)",
            },
            "remote_only": {
                "type": "boolean",
                "description": "If true, only return remote jobs",
            },
            "limit": {
                "type": "integer",
                "description": "Max number of results to return (default 10)",
            },
        },
        "required": ["keyword"],
    },
}


def _search_jobs(
    conn: sqlite3.Connection,
    keyword: str,
    min_score: int = 5,
    remote_only: bool = False,
    limit: int = 10,
) -> list[dict]:
    query = """
        SELECT title, company, location, url, relevance_score, remote
        FROM jobs
        WHERE (title LIKE ? OR description LIKE ?)
        AND (relevance_score IS NULL OR relevance_score >= ?)
    """
    params: list = [f"%{keyword}%", f"%{keyword}%", min_score]

    if remote_only:
        query += " AND remote = 1"

    query += f" ORDER BY relevance_score DESC LIMIT {limit}"

    return [dict(row) for row in conn.execute(query, params).fetchall()]


def run_job_search_agent(conn: sqlite3.Connection, user_query: str) -> str:
    """
    Agentic job search: Claude drives queries against the local DB via tool use,
    then synthesizes the results into a natural-language answer.
    """
    messages = [{"role": "user", "content": user_query}]

    while True:
        response = client.messages.create(
            model="claude-opus-5",
            max_tokens=1024,
            system=(
                "You are a job search assistant with access to a local database of job listings. "
                "Use search_jobs to find roles, calling it multiple times with different keywords if needed. "
                "Summarize your findings clearly when done."
            ),
            tools=[SEARCH_JOBS_TOOL],
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    return block.text
            return ""

        # stop_reason == "tool_use": execute each tool call and loop
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                args = block.input
                results = _search_jobs(
                    conn,
                    keyword=args["keyword"],
                    min_score=args.get("min_score", 5),
                    remote_only=args.get("remote_only", False),
                    limit=args.get("limit", 10),
                )
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(results),
                    }
                )

        messages.append({"role": "user", "content": tool_results})
