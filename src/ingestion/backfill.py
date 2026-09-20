import os
import json
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL_TEMPLATE = "https://api.adzuna.com/v1/api/jobs/sg/search/{page}"

# Same title list as the daily adzuna.py — kept in sync manually since this
# is a one-off script, not something scheduled alongside the daily job.
JOB_TITLES = [
    "Business Analyst",
    "Cloud Engineer",
    "Data Analyst",
    "Data Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "Software Engineer",
]

RESULTS_PER_PAGE = 50
MAX_PAGES_PER_TITLE = 20        # safety cap: up to 1,000 postings per title
REQUEST_DELAY_SECONDS = 2.5     # ~24 requests/minute, safely under the 25/minute limit

# NOTE: Adzuna only indexes currently *live* postings — this pulls deeper into
# what's currently available (older creation dates included), not truly
# expired/removed historical listings. "Historical" here means "as much of the
# live market depth as Adzuna will give us", not a full archive.

all_results = []
total_requests = 0

for title in JOB_TITLES:
    page = 1
    title_total_seen = 0

    while page <= MAX_PAGES_PER_TITLE:
        url = BASE_URL_TEMPLATE.format(page=page)
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": RESULTS_PER_PAGE,
            "what_phrase": title,
            "category": "it-jobs",
            "sort_by": "date",
            "content-type": "application/json",
        }

        response = requests.get(url, params=params)
        total_requests += 1

        if response.status_code != 200:
            print(f"{title} page {page}: request failed ({response.status_code}), stopping this title.")
            break

        data = response.json()
        jobs = data.get("results", [])
        total_available = data.get("count", 0)

        if not jobs:
            break  # no more results for this title

        for job in jobs:
            job["queried_title"] = title

        all_results.extend(jobs)
        title_total_seen += len(jobs)

        print(f"{title} page {page}: {len(jobs)} jobs (running total {title_total_seen} of {total_available} reported available)")

        # Stop once we've hit the end of what's actually available, or a
        # short page (fewer than a full page means there's nothing left).
        if len(jobs) < RESULTS_PER_PAGE or title_total_seen >= total_available:
            break

        page += 1
        time.sleep(REQUEST_DELAY_SECONDS)

    time.sleep(REQUEST_DELAY_SECONDS)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"data/raw/adzuna_backfill_{timestamp}.json"

output = {
    "pulled_at": datetime.now(timezone.utc).isoformat(),
    "queried_titles": JOB_TITLES,
    "results": all_results,
}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"\nTotal API requests made: {total_requests}")
print(f"Saved raw data to {output_path}")
print(f"Total jobs collected across all titles (may include overlaps): {len(all_results)}")