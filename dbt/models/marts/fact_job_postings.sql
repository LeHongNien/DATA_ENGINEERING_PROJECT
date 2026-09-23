select
    j.job_id,
    c.company_id,
    l.location_id,
    cast(strftime(cast(j.created as date), '%Y%m%d') as integer) as date_id,
    j.title,
    j.queried_title,
    j.category_label,
    j.category_tag,
    j.contract_type,
    j.contract_time,
    j.salary_min,
    j.salary_max,
    j.salary_is_predicted,
    j.redirect_url,
    j.created as posted_at
from {{ ref('stg_jobs') }} j
left join {{ ref('dim_company') }} c on j.company_name = c.company_name
left join {{ ref('dim_location') }} l on j.location_name = l.location_name