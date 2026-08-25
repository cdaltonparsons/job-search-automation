import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("USAJOBS_API_KEY")
api_email = os.getenv("USAJOBS_EMAIL")

def fetch_usajobs(keyword: str) -> list[dict]:
    host = "data.usajobs.gov"

    headers = {
        "Host": host,
        "User-Agent": api_email,
        "Authorization-Key": api_key
    }
    
    params = {
        "Keyword": keyword
    }
    response = requests.get("https://data.usajobs.gov/api/search", headers=headers, params=params)
    response.raise_for_status() # raise an error if status is 404, 500, etc

    root = response.json()["SearchResult"]["SearchResultItems"]

    jobs = []
    for item in root:
        title = item["MatchedObjectDescriptor"]["PositionTitle"]
        company = item["MatchedObjectDescriptor"]["OrganizationName"]
        location = item["MatchedObjectDescriptor"]["PositionLocation"][0]["LocationName"]
        url = item["MatchedObjectDescriptor"]["PositionURI"]
        posted_date = item["MatchedObjectDescriptor"]["PublicationStartDate"]
        description = item["MatchedObjectDescriptor"]["UserArea"]["Details"]["JobSummary"]
        remote = item["MatchedObjectDescriptor"]["UserArea"]["Details"]["RemoteIndicator"]
        salary = item["MatchedObjectDescriptor"]["PositionRemuneration"][0]["MinimumRange"]
        job = {
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "posted_date": posted_date,
            "description": description,
            "remote": remote,
            "salary": salary,
            "source": "usajobs",
        }
        jobs.append(job)
    
    return jobs
    