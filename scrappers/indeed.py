import time
from playwright.sync_api import sync_playwright
from ai.extractor import extract_job_from_html

BASE_URL = "https://www.indeed.com/jobs"


def _collect_job_urls(page, keyword: str, location: str) -> list[str]:
    """Navigate to Indeed search results and return individual job page URLs."""
    search_url = f"{BASE_URL}?q={keyword.replace(' ', '+')}&l={location.replace(' ', '+')}"
    page.goto(search_url, wait_until="networkidle", timeout=30000)
    time.sleep(2)

    anchors = page.query_selector_all("h2.jobTitle a")
    urls = []
    for a in anchors:
        href = a.get_attribute("href")
        if href:
            full_url = f"https://www.indeed.com{href}" if href.startswith("/") else href
            urls.append(full_url)
    return urls


def fetch_indeed(keyword: str, location: str = "Remote", limit: int = 10) -> list[dict]:
    """Scrape Indeed job listings using Playwright + Claude HTML extraction."""
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

        try:
            urls = _collect_job_urls(page, keyword, location)
            print(f"Indeed: found {len(urls)} job links for '{keyword}'")

            for url in urls[:limit]:
                try:
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    time.sleep(2)
                    html = page.content()
                    job = extract_job_from_html(html, url=url)
                    jobs.append(job)
                    print(f"  Extracted: {job.get('title', 'unknown')}")
                    time.sleep(2)
                except Exception as e:
                    print(f"  Error on {url}: {e}")
        finally:
            browser.close()

    return jobs
