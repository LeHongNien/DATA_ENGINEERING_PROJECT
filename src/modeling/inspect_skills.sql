-- Diagnostic check: sample the actual text context around C and R matches
-- to eyeball whether they're genuine tech mentions or false positives
-- (grade/plan/section labels, stray initials, etc.) that case-sensitivity
-- alone can't filter out.

-- c_matches_sample
SELECT
    j.id,
    j.title,
    regexp_extract(j.description, '.{0,40}\bC\b.{0,40}') AS context
FROM jobs j
WHERE regexp_matches(j.description, '\bC\b')
LIMIT 20;

-- r_matches_sample
SELECT
    j.id,
    j.title,
    regexp_extract(j.description, '.{0,40}\bR\b.{0,40}') AS context
FROM jobs j
WHERE regexp_matches(j.description, '\bR\b')
LIMIT 20;