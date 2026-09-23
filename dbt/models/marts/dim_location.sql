select
    row_number() over (order by location_name) as location_id,
    location_name,
    any_value(location_area) as location_area,
    any_value(latitude) as latitude,
    any_value(longitude) as longitude
from {{ ref('stg_jobs') }}
group by location_name