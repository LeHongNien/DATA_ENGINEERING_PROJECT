select
    cast(strftime(d, '%Y%m%d') as integer) as date_id,
    d as date,
    extract(year from d) as year,
    extract(month from d) as month,
    extract(day from d) as day,
    extract(dow from d) as day_of_week,
    strftime(d, '%A') as day_name,
    strftime(d, '%B') as month_name
from (
    select distinct cast(created as date) as d
    from {{ ref('stg_jobs') }}
    where created is not null
)