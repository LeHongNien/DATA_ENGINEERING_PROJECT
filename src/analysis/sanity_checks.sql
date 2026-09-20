-- Warehouse sanity checks for the jobs table.
-- Each query is separated by a comment header — query_jobs.py runs them in
-- order and prints the results. Keep this file as the source of truth for
-- what these checks actually do — query_jobs.py is just a runner.

-- total_row_count
SELECT COUNT(*) AS total_jobs FROM jobs;

-- jobs_per_queried_title
SELECT queried_title, COUNT(*) AS job_count
FROM jobs
GROUP BY queried_title
ORDER BY job_count DESC;

-- distinct_companies
SELECT COUNT(DISTINCT "company.display_name") AS distinct_companies FROM jobs;

-- created_date_range
SELECT MIN(created) AS earliest_posting, MAX(created) AS latest_posting FROM jobs;

-- undisclosed_company_count
SELECT COUNT(*) AS undisclosed_company_jobs
FROM jobs
WHERE "company.display_name" = 'Not Disclosed';