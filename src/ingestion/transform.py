import json
import glob
import os
import pandas as pd

# Find raw JSON files
files = glob.glob("data/raw/*.json")

if not files:
    raise FileNotFoundError("No raw JSON files found in data/raw/")

# Select the most recently modified file
# (load.py is responsible for accumulation across runs — this script only
# ever processes the single latest ingestion pull)
latest_file = max(files, key=os.path.getmtime)

# Load raw JSON
with open(latest_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Validate expected structure
if "results" not in data:
    raise ValueError("Raw JSON does not contain a 'results' field.")

if not data["results"]:
    raise ValueError("Raw JSON contains no job results.")

# Flatten nested job data
df = pd.json_normalize(data["results"])

# --- Schema stability -------------------------------------------------
# Adzuna doesn't return the same fields for every job (e.g. salary_min/
# salary_max/contract_type are sometimes absent). Explicitly define the
# columns we want downstream so the parquet schema — and therefore the
# DuckDB table load.py builds on top of it — never shifts from run to run.
EXPECTED_COLUMNS = [
    "id",
    "title",
    "description",
    "created",
    "salary_is_predicted",
    "salary_min",
    "salary_max",
    "contract_type",
    "contract_time",
    "redirect_url",
    "category.label",
    "category.tag",
    "location.display_name",
    "location.area",
    "latitude",
    "longitude",
    "company.display_name",
    "queried_title",
]

# Add any missing expected columns as null, then select only the expected
# columns in a fixed order (this also drops noise like `__CLASS__` and `adref`).
for column in EXPECTED_COLUMNS:
    if column not in df.columns:
        df[column] = pd.NA

df = df[EXPECTED_COLUMNS]

# location.area is a nested list per job (e.g. ["Singapore", "Central"]).
# Some jobs lack it entirely, which json_normalize/reindexing leaves as NaN —
# a mix of lists and NaN floats in one column breaks parquet's list type.
# Normalize every missing value to an empty list instead.
df["location.area"] = df["location.area"].apply(lambda x: x if isinstance(x, list) else [])

# latitude/longitude are only present on some postings; make sure they're
# numeric rather than left as generic objects.
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

# Basic schema validation
required_columns = ["title", "company.display_name", "location.display_name"]

missing_columns = [column for column in required_columns if column not in df.columns]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# Basic data-quality checks
# Title is treated as fatal: a job posting with no title at all suggests something
# is genuinely wrong with the response, not just an optional field being absent.
if df["title"].isna().any():
    raise ValueError("Some jobs are missing a title.")

# Company name is a routine, expected gap, not a fatal one: some Adzuna postings
# (often agency/recruiter listings) legitimately omit the hiring company's name to
# stay confidential. Impute a placeholder and log it, rather than crashing the
# entire daily batch over a handful of undisclosed postings.
missing_company = df["company.display_name"].isna().sum()
if missing_company > 0:
    print(f"Warning: {missing_company} job(s) have no disclosed company name — filled with 'Not Disclosed'.")
    df["company.display_name"] = df["company.display_name"].fillna("Not Disclosed")

# --- Type cleanup -------------------------------------------------------
df["created"] = pd.to_datetime(df["created"], errors="coerce", utc=True)
df["salary_is_predicted"] = df["salary_is_predicted"].astype(str) == "1"
df["salary_min"] = pd.to_numeric(df["salary_min"], errors="coerce")
df["salary_max"] = pd.to_numeric(df["salary_max"], errors="coerce")

# Remove duplicate jobs using stable identifiers (within this single pull)
before = len(df)

if "id" in df.columns:
    df = df.drop_duplicates(subset=["id"])
else:
    df = df.drop_duplicates(
        subset=["title", "company.display_name", "location.display_name"]
    )

duplicates_removed = before - len(df)

# Save processed data
# (single overwritten file — this represents "the latest transformed pull";
# load.py is what accumulates history into the warehouse)
output_path = "data/processed/jobs.parquet"
df.to_parquet(output_path, index=False)

print(f"Source file: {latest_file}")
print(f"Saved {len(df)} jobs to {output_path}")
print(f"Columns: {len(df.columns)}")
print(f"Duplicates removed: {duplicates_removed}")
print("Validation passed.")