with src as (
  select *
  from raw.nyc311_recent
),
typed as (
  select
    cast(unique_key as varchar) as unique_key,
    try_cast(created_date as timestamp) as created_ts,
    try_cast(closed_date as timestamp) as closed_ts,
    agency,
    complaint_type,
    descriptor,
    city,
    borough,
    try_cast(latitude as double) as latitude,
    try_cast(longitude as double) as longitude
  from src
),
dedup as (
  select *
  from (
    select *,
      row_number() over (partition by unique_key order by created_ts desc) as rn
    from typed
  ) t
  where rn = 1
)
select
  unique_key,
  created_ts,
  closed_ts,
  agency,
  complaint_type,
  descriptor,
  city,
  borough,
  latitude,
  longitude
from dedup
