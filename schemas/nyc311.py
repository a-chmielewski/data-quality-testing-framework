"""Pandera schema for NYC 311 data validation."""

import pandera as pa
from pandera import Column, DataFrameSchema

nyc311_schema = DataFrameSchema(
    {
        "unique_key": Column(str, nullable=False),
        "created_date": Column(str, nullable=False),
        "closed_date": Column(str, nullable=True),
        "agency": Column(str, nullable=True),
        "complaint_type": Column(str, nullable=True),
        "descriptor": Column(str, nullable=True),
        "city": Column(str, nullable=True),
        "borough": Column(str, nullable=True),
        "latitude": Column(str, nullable=True),
        "longitude": Column(str, nullable=True),
    },
    strict=False,
    coerce=True,
)
