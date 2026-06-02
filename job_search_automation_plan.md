# Job Search Automation — Project Plan

> Built with Claude (claude.ai). Migrate this file to VS Code and continue the session with Claude Code.

---

## Project Goal

Build a personal job search pipeline that automatically aggregates listings from multiple sources, deduplicates them, filters by relevance, and delivers a daily digest — so you spend time applying, not searching.

---

## Recommended Stack

| Layer | Tool | Why |
|---|---|---|
| Language | Python 3.11+ | Best ecosystem for scraping & automation |
| Static scraping | `requests` + `BeautifulSoup` | Simple, fast, no overhead |
| Dynamic scraping | `Playwright` | Handles JS-heavy sites (LinkedIn, Indeed) |
| Data | `pandas` + `SQLite` | Lightweight, zero setup, easy to query |
| Scheduling | `APScheduler` | Run scrapers on a cron-style timer |
| Alerts | `smtplib` or Mailgun | Email digest of new listings |
| Config | `python-dotenv` | Keep API keys out of code |
| AI | `anthropic` | Claude API for relevance scoring, extraction, and more |
| Testing | `pytest` | Python's standard test framework |

---

## Architecture Overview

```
[Data Sources]
      |
      v
[Scrapers / API Clients]   <-- one module per source
      |
      v
[Normalizer]               <-- standard schema for all listings
      |
      v
[SQLite Database]          <-- deduplication + storage
      |
      v
[Filter Engine]            <-- keyword, location, salary filters
      |
      v
[Digest / Alert]           <-- daily email or CLI report
```

---

## Data Sources (start here, expand later)

### Free / No Auth
- **Arbeitnow** — `https://www.arbeitnow.com/api/job-board-api` — remote/EU roles, no key needed
- **RSS Feeds** — LinkedIn, Indeed, Greenhouse, Lever, and Workday all expose RSS per search query

### Free with Key
- **USAJobs API** — `https://data.usajobs.gov/api/search` — well-documented, free registration required

### Direct Scraping (use Playwright)
- Indeed
- LinkedIn (be aware of ToS / rate limits — go slow)
- Company career pages (Greenhouse, Lever, Workday ATS)

> **Note on Claude API:** Pay-per-use, but at personal-project volume (hundreds of listings/day) the cost is negligible — typically under $1/month. No subscription required, just an API key.

---

## Standard Job Schema

Every source gets normalized to this before hitting the DB:

```python
{
    "id": str,           # hash of (title + company + url)
    "title": str,
    "company": str,
    "location": str,
    "url": str,
    "source": str,       # e.g. "indeed", "usajobs", "rss"
    "posted_date": str,  # ISO 8601
    "description": str,
    "salary": str,       # nullable
    "remote": bool,
    "seen": bool,        # have you viewed this listing?
    "applied": bool,
    "notes": str         # nullable, for your own tracking
}
```

---

## Build Order (Phased)

### Phase 0 — Python Foundations
> **Coming from Angular/TypeScript?** This phase builds the mental bridges before you touch any scraping or AI code.

- [x] Set up `pyproject.toml` + `venv` (think: `package.json` + `node_modules` — same idea, different tool)
- [x] Learn Python type hints and `dataclasses` (direct analogue to TypeScript interfaces)
- [x] Set up `pytest` and write a first passing test

> **You'll learn:** Python's data model, module system, and toolchain — and how to map your existing JS/TS mental models onto them.

---

### Phase 1 — Foundation
- [x] Set up project structure and virtual environment
- [x] Build SQLite schema and DB helper module
- [x] Write normalizer function (raw dict → standard schema)
- [x] Build deduplication logic (hash-based on title + company + url)

> **You'll learn:** SQLite schema design, hash-based deduplication, Python `dataclasses` as typed structs, and writing isolated unit tests with `pytest`.

**Tests to write:**
- Unit test for the normalizer (given raw dict in, assert standard schema out)
- Unit test for deduplication (same job twice → only one row)

---

### Phase 2 — First Data Sources + First Claude Touch
- [ ] RSS feed parser (start here — simplest wins)
- [ ] USAJobs API client
- [ ] **Claude relevance scoring** — send each listing's title + description to Claude, get back a 0–10 relevance score against your target role

> **You'll learn:** HTTP clients in Python, JSON parsing, API authentication, and your first real Claude API call using structured JSON output.

**Tests to write:**
- Mock HTTP responses for both API clients (no real network calls in tests)
- Fixture-based test for Claude scoring (fake API response, assert score is parsed correctly)

---

### Phase 3 — Dynamic Scraping + Claude Extraction
- [ ] Playwright scraper for Indeed
- [ ] Playwright scraper for LinkedIn (slow, respectful rate limits)
- [ ] ATS career page scrapers (Greenhouse, Lever)
- [ ] **Claude HTML extraction** — for pages where schema fields aren't cleanly available, pass raw HTML to Claude and ask it to return the standard schema as JSON

> **You'll learn:** Browser automation with Playwright, async Python, ethical scraping practices, and using AI as a flexible data-extraction layer instead of brittle regex.

**Tests to write:**
- HTML parser test using a saved HTML snapshot (no live browser in CI)

---

### Phase 4 — Filtering, Alerts & Claude Digest
- [ ] Keyword filter (title, description)
- [ ] Location / remote filter
- [ ] Salary filter (where available)
- [ ] Daily email digest (new listings since last run)
- [ ] **Claude narrative digest** — instead of a raw list, ask Claude to write a short editorial summary of the day's best matches

> **You'll learn:** Scheduling with APScheduler, email delivery via SMTP, and how to prompt Claude for a specific tone, length, and structure in generated text.

**Tests to write:**
- Test digest formatting logic (given N jobs, assert email body contains expected fields)

---

### Phase 5 — AI Engineering Deep Dive
- [ ] Resume ↔ job description gap analysis (Claude API)
- [ ] Auto-generate tailored cover letter draft (Claude API)
- [ ] **Tool use** — let Claude call a `search_jobs` tool to drive its own queries against your DB
- [ ] **Streaming** — stream cover letter output token-by-token to the CLI as it's generated
- [ ] **Prompt caching** — cache your resume across all JD comparisons and measure the cost reduction
- [ ] **Batch API** — score 50 listings asynchronously in a single batch request

> **You'll learn:** Each bullet is a distinct Claude API capability. Together they cover the full Anthropic SDK surface: completions, tool use, streaming, caching, and async batch processing.

---

### Phase 6 — Dashboard (Optional)
> Leverage your Angular skills to build a UI on top of the pipeline you've built.

- [ ] FastAPI endpoint serving job data as JSON
- [ ] Angular frontend to browse, filter, and mark jobs as seen / applied / rejected

> **You'll learn:** FastAPI as a Python backend (think Express, but with Python type hints), and how to wire an Angular app to a REST API you built yourself.

---

## Project Structure

```
job-search/
├── .env                   # API keys — never commit this
├── pyproject.toml
├── main.py                # entry point / scheduler
├── db/
│   ├── schema.sql
│   └── database.py        # DB helper functions
├── scrapers/
│   ├── base.py            # abstract base scraper class
│   ├── rss.py
│   ├── usajobs.py
│   ├── indeed.py
│   └── linkedin.py
├── normalizer.py          # raw → standard schema
├── filters.py             # filtering logic
├── digest.py              # email digest builder
├── ai/
│   ├── scorer.py          # Claude relevance scoring
│   ├── extractor.py       # Claude HTML → schema
│   └── cover_letter.py    # Claude cover letter + gap analysis
├── cli.py                 # mark jobs, view stats
└── tests/
    ├── test_normalizer.py
    ├── test_database.py
    ├── test_rss.py
    └── test_scorer.py
```

---

## Environment Variables (.env)

```
USAJOBS_API_KEY=
USAJOBS_EMAIL=
ANTHROPIC_API_KEY=
MAILGUN_API_KEY=        # or use Gmail SMTP
ALERT_EMAIL_TO=
```

---

## Key Libraries to Install

```bash
pip install requests beautifulsoup4 playwright pandas \
            apscheduler python-dotenv anthropic lxml pytest
playwright install chromium
```

---

## Notes & Reminders

- **Deduplication first** — the same job appears on 3-5 platforms. Hash on `(title + company + url)` to avoid noise.
- **Rate limiting** — add `time.sleep(2-5)` between requests, especially on LinkedIn/Indeed.
- **Respect robots.txt** — check before scraping any site directly.
- **Start with RSS + USAJobs** — both are clean, free, and require no browser automation. Get the pipeline working end-to-end before adding complexity.
- **Claude API integration** — use `claude-sonnet-4-6` for relevance scoring, extraction, and cover letter generation. Start simple (basic completions in Phase 2), then layer in streaming, tool use, and caching as you reach Phase 5.
- **Test as you go** — each phase has a "Tests to write" list. Don't skip it; tests catch regressions when you add the next scraper.

---

## Continuing in VS Code

1. Open Claude Code in VS Code (`Ctrl+Shift+P` → "Claude")
2. Drop this file into your project root
3. Tell Claude: *"I have a job search automation plan in job_search_automation_plan.md — let's start with Phase 0"*
4. Claude Code can read the file directly and begin mentoring you through Phase 0

---

*Plan compiled: June 2026*
