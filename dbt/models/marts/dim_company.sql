select
    row_number() over (order by company_name) as company_id,
    company_name
from (select distinct company_name from {{ ref('stg_jobs') }})