import duckdb

DB_PATH = "data/warehouse/jobs.duckdb"
SQL_PATH = "src/analysis/sanity_checks.sql"

with open(SQL_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Split into individual statements; each one is preceded by a "-- label"
# comment in the .sql file, which we pull out to use as a heading.
statements = [s.strip() for s in content.split(";") if s.strip()]

con = duckdb.connect(DB_PATH)

for statement in statements:
    lines = statement.splitlines()
    comment_lines = [line[2:].strip() for line in lines if line.strip().startswith("--")]
    label = comment_lines[-1] if comment_lines else "query"

    sql = "\n".join(line for line in lines if not line.strip().startswith("--"))
    if not sql.strip():
        continue

    result = con.execute(sql).df()
    print(f"\n=== {label} ===")
    print(result.to_string(index=False))

con.close()