-- Staging: light renaming only, no business logic. The dotted column names
-- ("company.display_name") are an artifact of pd.json_normalize flattening
-- nested JSON — this model is where that gets cleaned up into names the
-- rest of the project (and anyone reading it) can actually work with.

select
    id as job_id,
    title,
    description,
    created,
    salary_is_predicted,
    salary_min,
    salary_max,
    contract_type,
    contract_time,
    redirect_url,
    "category.label" as category_label,
    "category.tag" as category_tag,
    "location.display_name" as location_name,
    "location.area" as location_area,
    latitude,
    longitude,
    "company.display_name" as company_name,
    queried_title
from {{ source('raw', 'jobs') }}