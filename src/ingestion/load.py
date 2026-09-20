import duckdb

PARQUET_PATH = "data/processed/jobs.parquet"
DB_PATH = "data/warehouse/jobs.duckdb"

con = duckdb.connect(DB_PATH)

# Create the table on first run only, with the schema taken from the
# parquet file itself — no rows yet.
con.execute(f"""
    CREATE TABLE IF NOT EXISTS jobs AS
    SELECT * FROM read_parquet('{PARQUET_PATH}') WHERE 1 = 0
""")

before = con.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]

# Insert only jobs whose id isn't already in the warehouse. This is what
# turns each overwritten jobs.parquet snapshot into accumulating history —
# every run only adds genuinely new postings.
con.execute(f"""
    INSERT INTO jobs
    SELECT new.*
    FROM read_parquet('{PARQUET_PATH}') AS new
    WHERE new.id NOT IN (SELECT id FROM jobs)
""")

after = con.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]

print(f"Jobs in warehouse before load: {before}")
print(f"New jobs inserted: {after - before}")
print(f"Jobs in warehouse after load: {after}")

con.close()