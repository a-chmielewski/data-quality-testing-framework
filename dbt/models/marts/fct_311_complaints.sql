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
  longitude,
  case when closed_ts is null then 1 else 0 end as is_open
from {{ ref('stg_311') }}
