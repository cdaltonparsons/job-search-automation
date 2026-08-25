import time
import random
from playwright.sync_api import sync_playwright
from ai.extractor import extract_job_from_html

SEARCH_URL = "https://www.linkedin.com/jobs/search"


def _collect_job_urls(page, keyword: str, location: str) -> list[str]:
    """Navigate to LinkedIn search results and return individual job page URLs."""
    search_url = f"{SEARCH_URL}?keywords={keyword.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
    page.goto(search_url, wait_until="networkidle", timeout=30000)
    time.sleep(3)

    anchors = page.query_selector_all("a.base-card__full-link")
    urls = []
    for a in anchors:
        href = a.get_attribute("href")
        if href:
            urls.append(href.split("?")[0])  # strip tracking params
    return list(dict.fromkeys(urls))  # deduplicate while preserving order


def fetch_linkedin(keyword: str, location: str = "Remote", limit: int = 5) -> list[dict]:
    """Scrape LinkedIn job listings using Playwright + Claude HTML extraction.

    limit defaults to 5 — LinkedIn is more aggressive about blocking than Indeed,
    so keep this low and runs infrequent (once per day at most).
    """
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        try:
            urls = _collect_job_urls(page, keyword, location)
            print(f"LinkedIn: found {len(urls)} job links for '{keyword}'")

            for url in urls[:limit]:
                try:
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    delay = random.uniform(3, 6)  # randomized delay to avoid pattern detection
                    time.sleep(delay)
                    html = page.content()
                    job = extract_job_from_html(html, url=url)
                    jobs.append(job)
                    print(f"  Extracted: {job.get('title', 'unknown')}")
                except Exception as e:
                    print(f"  Error on {url}: {e}")
        finally:
            browser.close()

    return jobs
