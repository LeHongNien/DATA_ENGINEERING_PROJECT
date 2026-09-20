import os
import json
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/sg/search/1"

JOB_TITLES = [
    "Business Analyst",
    "Cloud Engineer",
    "Data Analyst",
    "Data Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "Software Engineer",
]

all_results = []

for title in JOB_TITLES:
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": 50,
        "what_phrase": title,   # exact-phrase match, not word-level OR
        "category": "it-jobs",  # keep results scoped to tech, not e.g. civil/mechanical "engineer"
        "sort_by": "date",      # newest first, so daily runs surface new postings
        "content-type": "application/json",
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    jobs = data.get("results", [])
    for job in jobs:
        job["queried_title"] = title  # track which query surfaced this job

    all_results.extend(jobs)

    print(f"{title}: {len(jobs)} jobs")

    time.sleep(1)  # polite pacing; well within the 25 hits/minute limit regardless

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"data/raw/adzuna_{timestamp}.json"

output = {
    "pulled_at": datetime.now(timezone.utc).isoformat(),
    "queried_titles": JOB_TITLES,
    "results": all_results,
}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"Saved raw data to {output_path}")
print(f"Total jobs returned across all titles (may include overlaps): {len(all_results)}")