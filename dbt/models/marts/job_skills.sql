-- DuckDB requires regexp_matches' options argument to be a literal constant,
-- not a column value — so case-insensitive and case-sensitive skills are
-- matched in two CTEs (each using a literal flag) and combined.
-- Bare "R" and "C" are deliberately not tracked — see dim_skill seed
-- comments / project notes for why (too ambiguous against short truncated
-- description snippets to reliably disambiguate).

with case_insensitive as (
    select j.job_id, s.skill_id
    from {{ ref('stg_jobs') }} j
    cross join {{ ref('dim_skill') }} s
    where s.regex_flags = 'i'
      and regexp_matches(j.description, s.match_pattern, 'i')
),

case_sensitive as (
    select j.job_id, s.skill_id
    from {{ ref('stg_jobs') }} j
    cross join {{ ref('dim_skill') }} s
    where s.regex_flags = 'cs'
      and regexp_matches(j.description, s.match_pattern)
)

select * from case_insensitive
union all
select * from case_sensitive