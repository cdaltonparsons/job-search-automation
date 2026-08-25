# Job Search Automation Pipeline

A personal job search pipeline that aggregates listings from multiple sources, scores them for relevance using Claude AI, filters them, and delivers a daily digest — so you spend time applying, not searching.

---

## Project Structure

```
newJob/
├── .env                        # API keys — never commit
├── main.py                     # Pipeline entry point (fetch → normalize → score → digest)
├── cli.py                      # Interactive CLI for cover letters, gap analysis, agent search
├── normalizer.py               # Raw dict → standard Job dataclass
├── filters.py                  # Filter jobs by score, remote, keywords
├── resume.txt                  # Your resume in plain text — never commit
│
├── scrappers/
│   ├── rss.py                  # RSS feed parser
│   ├── usajobs.py              # USAJobs REST API client
│   ├── indeed.py               # Playwright scraper for Indeed
│   ├── linkedin.py             # Playwright scraper for LinkedIn (use sparingly)
│   ├── arbeitnow.py            # Arbeitnow public API (no auth)
│   ├── remotive.py             # Remotive public API (no auth, remote-only)
│   ├── remoteok.py             # RemoteOK public API (no auth, remote-only)
│   ├── greenhouse.py           # Greenhouse ATS API (targeted companies)
│   └── lever.py                # Lever ATS API (targeted companies)
│
├── ai/
│   ├── scorer.py               # Claude relevance scoring (single + batch API)
│   ├── extractor.py            # Claude HTML → structured job data
│   ├── cover_letter.py         # Streaming cover letter + gap analysis (prompt caching)
│   └── agent.py                # Tool-use agent: Claude queries the job DB directly
│
├── db/
│   ├── schema.sql              # SQLite schema
│   └── database.py             # DB helpers: init, insert, update score
│
├── digest.py                   # Claude narrative digest + Gmail email delivery
│
├── api/
│   └── app.py                  # FastAPI REST API for the Angular dashboard
│
├── dashboard/                  # Angular 17 frontend
│   └── src/app/
│       ├── models/job.model.ts
│       ├── services/job.service.ts
│       └── components/job-list/
│
└── tests/                      # pytest unit tests (all mock external calls)
    ├── test_normalizer.py
    ├── test_database.py
    ├── test_rss.py
    ├── test_usajobs.py
    ├── test_scorer.py
    ├── test_extractor.py
    ├── test_filters.py
    ├── test_arbeitnow.py
    ├── test_remotive.py
    ├── test_remoteok.py
    ├── test_greenhouse.py
    └── test_lever.py
```

---

## Setup

### 1. Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests playwright python-dotenv anthropic fastapi uvicorn
playwright install chromium
```

### 2. Environment variables

Create a `.env` file in the project root (already in `.gitignore`):

```
ANTHROPIC_API_KEY=sk-ant-...
USAJOBS_API_KEY=your-key
USAJOBS_EMAIL=your@email.com
ALERT_EMAIL_FROM=you@gmail.com
ALERT_EMAIL_TO=you@gmail.com
ALERT_EMAIL_PASSWORD=xxxx xxxx xxxx xxxx   # Gmail App Password
```

**Getting keys:**
- **Anthropic:** [console.anthropic.com](https://console.anthropic.com) — pay-per-use, ~$1/month at personal volume
- **USAJobs:** [usajobs.gov/Help/APIInfo/](https://www.usajobs.gov/Help/APIInfo/) — free, requires registration
- **Gmail App Password:** myaccount.google.com → Security → 2-Step Verification → App passwords

### 3. Resume

Create `resume.txt` in the project root with your resume as plain text. This is in `.gitignore`.

### 4. Angular dashboard

```bash
cd dashboard
npm install
```

---

## Running the Pipeline

### Full pipeline (fetch all sources → score → digest → email)

```bash
python main.py
```

Fetches from all configured sources, scores new jobs with Claude Haiku, filters by score ≥ 6, writes a Claude narrative digest to the terminal, and emails it if email is configured.

### Configure sources

Edit the top of `main.py`:

```python
RSS_FEEDS = ["https://..."]  # Add RSS feed URLs here

USAJOBS_KEYWORDS  = ["angular developer", "frontend engineer", "full stack typescript"]
INDEED_KEYWORDS   = ["angular developer", "frontend engineer typescript"]
LINKEDIN_KEYWORDS = ["angular developer"]   # Keep short — LinkedIn rate-limits aggressively

# ATS company slugs — find these in the URL of a company's job board:
#   Greenhouse: boards.greenhouse.io/{slug}
#   Lever:      jobs.lever.co/{slug}
GREENHOUSE_COMPANIES = ["notion", "figma", "stripe", "discord"]
LEVER_COMPANIES      = ["netflix", "reddit", "robinhood"]
```

Arbeitnow, Remotive, and RemoteOK require no configuration — they pull all open roles automatically on every run.

---

## CLI Commands

```bash
# Ask a natural-language question about your saved jobs (Claude uses tool use to query the DB)
python cli.py ask "find me remote Angular jobs scored above 7"

# Stream a tailored cover letter for a job (uses your resume.txt)
python cli.py cover <job_id>

# Stream a gap analysis between your resume and a job
python cli.py gap <job_id>

# Score all unscored jobs at once using the Batch API (async, 50% cheaper)
python cli.py batch-score
```

To find job IDs:

```bash
sqlite3 jobs.db "SELECT id, title, company, relevance_score FROM jobs ORDER BY relevance_score DESC LIMIT 20"
```

---

## Dashboard

Start the API and Angular dev server in two terminals:

```bash
# Terminal 1 — FastAPI
uvicorn api.app:app --reload

# Terminal 2 — Angular
cd dashboard
npm start
```

Open [http://localhost:4200](http://localhost:4200).

### API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/jobs` | List jobs — supports `keyword`, `min_score`, `remote_only`, `seen`, `applied`, `limit`, `offset` |
| `GET` | `/api/jobs/{id}` | Single job |
| `PATCH` | `/api/jobs/{id}` | Update `seen`, `applied`, `notes` |
| `GET` | `/api/stats` | Summary counts (total, unseen, applied, avg score) |

Interactive API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs) when the server is running.

---

## Running Tests

```bash
python -m pytest tests/ -v
```

All tests mock external calls (no real HTTP requests, no live browser, no Claude API calls in CI).

---

## Claude API Features Used

| Feature | Where | Why |
|---------|-------|-----|
| Basic completions | `ai/scorer.py` | Score each job 0–10 for relevance |
| Structured JSON output | `ai/scorer.py`, `ai/extractor.py` | Force Claude to return `{"score": N}` / job schema |
| HTML extraction | `ai/extractor.py` | Extract job fields from raw Playwright HTML — no brittle CSS selectors |
| Streaming | `ai/cover_letter.py` | Cover letters and gap analysis appear token-by-token |
| Prompt caching | `ai/cover_letter.py` | Resume is cached across cover letter calls — ~10% cost on repeat calls |
| Tool use | `ai/agent.py` | Claude drives SQL queries against the local DB via a `search_jobs` tool |
| Batch API | `ai/scorer.py` | Score 50+ jobs asynchronously in one request at 50% lower cost |
| Narrative generation | `digest.py` | Editorial daily digest instead of a raw job list |

---

## Data Sources

| Source | Auth | Type | Notes |
|--------|------|------|-------|
| RSS feeds | None | Keyword search | LinkedIn/Indeed/Greenhouse all expose RSS per search query |
| USAJobs | Free API key | Keyword search | Well-documented, reliable, US government roles |
| Indeed | None | Playwright scraper | May break if Indeed changes their HTML |
| LinkedIn | None | Playwright scraper | Use sparingly — ToS restricts scraping, rate-limits aggressively |
| Arbeitnow | None | Full catalog | Remote-friendly roles, no auth, simple JSON API |
| Remotive | None | Full catalog | Remote-only roles, no auth, filter by `category` param |
| RemoteOK | None | Full catalog | Remote-only tech roles, no auth |
| Greenhouse | None | ATS feed | Per-company feed — add slug from `boards.greenhouse.io/{slug}` |
| Lever | None | ATS feed | Per-company feed — add slug from `jobs.lever.co/{slug}` |

### Finding Greenhouse and Lever slugs

Go to a company's careers page. If the job listings live at `boards.greenhouse.io/notion` or `job-boards.greenhouse.io/notion`, the slug is `notion`. If they live at `jobs.lever.co/netflix`, the slug is `netflix`. Many mid-size tech companies use one of these two ATS platforms — check the URL when you click "View open roles" on a company's website.

---

## Architecture

```
[Sources: RSS / USAJobs / Indeed / LinkedIn / Arbeitnow / Remotive / RemoteOK / Greenhouse / Lever]
          ↓
     [Scrapers]          one module per source
          ↓
     [Normalizer]        raw dict → Job dataclass (standard schema)
          ↓
  [SQLite Database]      INSERT OR IGNORE deduplication
          ↓
  [Claude Scorer]        0–10 relevance score per job
          ↓
  [Filter Engine]        min_score, remote_only, keyword
          ↓
 [Claude Digest]         narrative summary + Gmail email
          ↓
  [FastAPI + Angular]    browse, filter, mark applied
```

---

## Job Schema

Every source is normalized to this before hitting the database:

| Field | Type | Description |
|-------|------|-------------|
| `id` | TEXT PK | MD5 hash of title + company + url |
| `title` | TEXT | Job title |
| `company` | TEXT | Company name |
| `location` | TEXT | City/state or "Remote" |
| `url` | TEXT | Link to the original listing |
| `source` | TEXT | `rss`, `usajobs`, `playwright`, `arbeitnow`, `remotive`, `remoteok`, `greenhouse`, `lever` |
| `posted_date` | TEXT | ISO 8601 |
| `description` | TEXT | Full job description |
| `salary` | TEXT | Nullable — range if available |
| `remote` | INTEGER | 0 or 1 |
| `seen` | INTEGER | 0 or 1 — have you viewed this? |
| `applied` | INTEGER | 0 or 1 |
| `notes` | TEXT | Nullable — your own tracking notes |
| `relevance_score` | INTEGER | 0–10, scored by Claude |
