import requests
import xml.etree.ElementTree as ET

def fetch_rss_feed(url: str) -> list[dict]:
    """Fetch and parse an RSS feed, return list of raw job dicts"""
    response = requests.get(url)
    response.raise_for_status() # raise an error if status is 404, 500, etc

    root = ET.fromstring(response.text)

    jobs = []
    for item in root.iter("item"):
        title = item.findtext("title")
        url = item.findtext("link")
        description = item.findtext("description")
        posted_date = item.findtext("pubDate")
        job = {
            "title": title,
            "url": url,
            "description": description,
            "posted_date": posted_date,
            "source": "rss",
        }
        jobs.append(job)

    return jobs