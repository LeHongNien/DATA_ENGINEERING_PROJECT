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

RESULTS_PER_PAGE = 50
REQUEST_DELAY_SECONDS = 2.5  # ~24 requests/minute, safely under the 25/minute limit

# The two titles that hit backfill.py's MAX_PAGES_PER_TITLE=20 cap (page 20 =
# 1,000 results) before exhausting Adzuna's reported count. Continuing from
# page 21. max_page is set a bit above what's strictly needed as a buffer, in
# case the live count shifted slightly since the original backfill ran.
TARGETS = {
    "Data Scientist": {"start_page": 20, "max_page": 38},
    "Software Engineer": {"start_page": 20, "max_page": 53},
}

all_results = []
total_requests = 0

for title, bounds in TARGETS.items():
    page = bounds["start_page"]
    max_page = bounds["max_page"]
    title_total_seen = 0

    while page <= max_page:
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
            print(f"{title} page {page}: request failed ({response.status_code}) — "
                  f"likely a practical pagination depth limit. Stopping this title.")
            break

        data = response.json()
        jobs = data.get("results", [])
        total_available = data.get("count", 0)

        if not jobs:
            print(f"{title} page {page}: no results returned — stopping "
                  f"(exhausted, or hit a depth limit before reaching the reported count).")
            break

        for job in jobs:
            job["queried_title"] = title

        all_results.extend(jobs)
        title_total_seen += len(jobs)

        print(f"{title} page {page}: {len(jobs)} jobs "
              f"(this run's running total {title_total_seen}, {total_available} reported available)")

        if len(jobs) < RESULTS_PER_PAGE:
            break  # reached the actual end

        page += 1
        time.sleep(REQUEST_DELAY_SECONDS)

    time.sleep(REQUEST_DELAY_SECONDS)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"data/raw/adzuna_backfill_continue_{timestamp}.json"

output = {
    "pulled_at": datetime.now(timezone.utc).isoformat(),
    "queried_titles": list(TARGETS.keys()),
    "results": all_results,
}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"\nTotal API requests made: {total_requests}")
print(f"Saved raw data to {output_path}")
print(f"Total jobs collected in this continuation run: {len(all_results)}")