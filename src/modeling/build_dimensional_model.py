import duckdb

DB_PATH = "data/warehouse/jobs.duckdb"
SQL_PATH = "src/modeling/build_dimensional_model.sql"

with open(SQL_PATH, "r", encoding="utf-8") as f:
    content = f.read()

statements = [s.strip() for s in content.split(";") if s.strip()]

con = duckdb.connect(DB_PATH)

for statement in statements:
    lines = statement.splitlines()
    comment_lines = [line[2:].strip() for line in lines if line.strip().startswith("--")]
    label = comment_lines[-1] if comment_lines else "statement"

    sql = "\n".join(line for line in lines if not line.strip().startswith("--"))
    if not sql.strip():
        continue

    con.execute(sql)
    print(f"Built {label}")

print("\n--- Row counts ---")
for table in ["dim_company", "dim_location", "dim_date", "fact_job_postings"]:
    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count} rows")

con.close()