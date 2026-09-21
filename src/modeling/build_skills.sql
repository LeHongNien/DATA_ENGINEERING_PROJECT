-- Skill vocabulary and extraction from job descriptions.
-- Keyword/regex based — a hand-maintained list for now, deliberately simple.
-- The match pattern and case-sensitivity live in dim_skill as data, so
-- adding or adjusting a skill later doesn't require touching query logic.
--
-- Go, Excel, Express, React, C++, and C# are matched case-sensitively
-- (regex_flags = '') since they collide with ordinary English words/verbs
-- in lowercase or mid-sentence use everything else matches
-- case-insensitively ('i').
--
-- Deliberately NOT tracking bare "R" or "C" as skills: both collide with
-- too many things in ordinary business/job-posting text (R&D, requisition
-- codes, institute abbreviations, C-suite, C-level, company names like
-- SS&C) to reliably exclude via regex, and Adzuna's descriptions are only
-- truncated snippets to begin with, so there isn't enough context to do
-- better. C++ and C# don't have this problem — they're unambiguous on
-- their own — so they're kept as their own distinct skills.

-- dim_skill
CREATE OR REPLACE TABLE dim_skill AS
SELECT
    ROW_NUMBER() OVER (ORDER BY skill_name) AS skill_id,
    skill_name,
    match_pattern,
    regex_flags
FROM (VALUES
    ('Python', '\bPython\b', 'i'),
    ('SQL', '\bSQL\b', 'i'),
    ('AWS', '\bAWS\b', 'i'),
    ('Spark', '\bSpark\b', 'i'),
    ('Power BI', '\bPower\s*BI\b', 'i'),
    ('Tableau', '\bTableau\b', 'i'),
    ('Azure', '\bAzure\b', 'i'),
    ('Excel', '\bExcel\b', ''),
    ('GCP', '\bGCP\b', 'i'),
    ('Java', '\bJava\b', 'i'),
    ('Databricks', '\bDatabricks\b', 'i'),
    ('Hadoop', '\bHadoop\b', 'i'),
    ('Go', '\bGo\b', ''),
    ('PyTorch', '\bPyTorch\b', 'i'),
    ('C++', '\bC\+\+', ''),
    ('C#', '\bC#', ''),
    ('Snowflake', '\bSnowflake\b', 'i'),
    ('TensorFlow', '\bTensor\s*Flow\b', 'i'),
    ('Kubernetes', '\bKubernetes\b', 'i'),
    ('Docker', '\bDocker\b', 'i'),
    ('Kafka', '\bKafka\b', 'i'),
    ('Airflow', '\bAirflow\b', 'i'),
    ('Scala', '\bScala\b', 'i'),
    ('Git', '\bGit\b', 'i'),
    ('Hive', '\bHive\b', 'i'),
    ('Scikit-learn', '\bScikit-learn\b', 'i'),
    ('Linux', '\bLinux\b', 'i'),
    ('Oracle', '\bOracle\b', 'i'),
    ('Flink', '\bFlink\b', 'i'),
    ('pandas', '\bpandas\b', 'i'),
    ('Terraform', '\bTerraform\b', 'i'),
    ('SAP', '\bSAP\b', 'i'),
    ('Bash', '\bBash\b', 'i'),
    ('Redshift', '\bRedshift\b', 'i'),
    ('NoSQL', '\bNoSQL\b', 'i'),
    ('PowerPoint', '\bPowerPoint\b', 'i'),
    ('PostgreSQL', '\bPostgreSQL\b', 'i'),
    ('Express', '\bExpress\b', ''),
    ('dbt', '\bdbt\b', 'i'),
    ('BigQuery', '\bBigQuery\b', 'i'),
    ('SQL Server', '\bSQL\s*Server\b', 'i'),
    ('GitHub', '\bGitHub\b', 'i'),
    ('Langchain', '\bLangchain\b', 'i'),
    ('Informatica', '\bInformatica\b', 'i'),
    ('MySQL', '\bMySQL\b', 'i'),
    ('React', '\bReact\b', ''),
    ('NumPy', '\bNumPy\b', 'i'),
    ('Delta Lake', '\bDelta\s*Lakes?\b', 'i'),
    ('Azure Data Factory', '\bData\s*Factory\b', 'i'),
    ('Jira', '\bJira\b', 'i')
) AS t(skill_name, match_pattern, regex_flags);

-- job_skills
-- DuckDB requires regexp_matches' options argument to be a literal constant,
-- not a column value — so case-insensitive and case-sensitive skills are
-- matched in two separate queries (each using a literal flag) and combined.
CREATE OR REPLACE TABLE job_skills AS
SELECT j.id AS job_id, s.skill_id
FROM jobs j
CROSS JOIN dim_skill s
WHERE s.regex_flags = 'i'
  AND regexp_matches(j.description, s.match_pattern, 'i')

UNION ALL

SELECT j.id AS job_id, s.skill_id
FROM jobs j
CROSS JOIN dim_skill s
WHERE s.regex_flags = ''
  AND regexp_matches(j.description, s.match_pattern);