-- Dimensional model built on top of the jobs staging table.
-- Full-refresh pattern: since jobs already accumulates incrementally via
-- load.py, these derived tables can simply be rebuilt from it each time —
-- no separate incremental logic needed here.

-- dim_company
CREATE OR REPLACE TABLE dim_company AS
SELECT
    ROW_NUMBER() OVER (ORDER BY company_name) AS company_id,
    company_name
FROM (
    SELECT DISTINCT "company.display_name" AS company_name FROM jobs
) t;

-- dim_location
CREATE OR REPLACE TABLE dim_location AS
SELECT
    ROW_NUMBER() OVER (ORDER BY location_name) AS location_id,
    location_name,
    ANY_VALUE(area) AS area,
    ANY_VALUE(latitude) AS latitude,
    ANY_VALUE(longitude) AS longitude
FROM (
    SELECT
        "location.display_name" AS location_name,
        "location.area" AS area,
        latitude,
        longitude
    FROM jobs
) t
GROUP BY location_name;

-- dim_date
CREATE OR REPLACE TABLE dim_date AS
SELECT
    CAST(strftime(d, '%Y%m%d') AS INTEGER) AS date_id,
    d AS date,
    EXTRACT(year FROM d) AS year,
    EXTRACT(month FROM d) AS month,
    EXTRACT(day FROM d) AS day,
    EXTRACT(dow FROM d) AS day_of_week,
    strftime(d, '%A') AS day_name,
    strftime(d, '%B') AS month_name
FROM (
    SELECT DISTINCT CAST(created AS DATE) AS d
    FROM jobs
    WHERE created IS NOT NULL
) t;

-- fact_job_postings
CREATE OR REPLACE TABLE fact_job_postings AS
SELECT
    j.id AS job_id,
    c.company_id,
    l.location_id,
    CAST(strftime(CAST(j.created AS DATE), '%Y%m%d') AS INTEGER) AS date_id,
    j.title,
    j.queried_title,
    j."category.label" AS category_label,
    j."category.tag" AS category_tag,
    j.contract_type,
    j.contract_time,
    j.salary_min,
    j.salary_max,
    j.salary_is_predicted,
    j.redirect_url,
    j.created AS posted_at
FROM jobs j
LEFT JOIN dim_company c ON j."company.display_name" = c.company_name
LEFT JOIN dim_location l ON j."location.display_name" = l.location_name;