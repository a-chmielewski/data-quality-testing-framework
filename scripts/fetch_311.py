import os
import json
import datetime as dt
from pathlib import Path

import pandas as pd
import requests
import duckdb

try:
    from schemas.nyc311 import nyc311_schema
except Exception:
    nyc311_schema = None

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR = Path("duckdb")
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "nyc.duckdb"

BASE = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
FIELDS = [
    "unique_key",
    "created_date",
    "closed_date",
    "agency",
    "complaint_type",
    "descriptor",
    "city",
    "borough",
    "latitude",
    "longitude",
]


# helpers
def fmt_date(d: dt.date) -> str:
    return d.strftime("%Y-%m-%d")


def fetch_slice(start_date: dt.date, end_date: dt.date, limit=3000) -> pd.DataFrame:
    where = f"created_date between '{fmt_date(start_date)}T00:00:00' and '{fmt_date(end_date)}T23:59:59'"
    params = {
        "$select": ",".join(FIELDS),
        "$where": where,
        "$order": "created_date DESC",
        "$limit": limit,
    }
    r = requests.get(BASE, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data)
    # ensure all fields exist even if empty
    for c in FIELDS:
        if c not in df.columns:
            df[c] = None
    return df[FIELDS]


def main():
    today = dt.date.today()
    recent_end = today - dt.timedelta(days=1)
    recent_start = recent_end - dt.timedelta(days=6)  # last 7 days

    hist_year = 2019  # good contrast; adjust if preferred
    hist_start = recent_start.replace(year=hist_year)
    hist_end = recent_end.replace(year=hist_year)

    print(f"Fetching RECENT {recent_start}..{recent_end}")
    df_recent = fetch_slice(recent_start, recent_end, limit=3000)
    print(f"Rows recent: {len(df_recent)}")

    print(f"Fetching HISTORICAL {hist_start}..{hist_end}")
    df_hist = fetch_slice(hist_start, hist_end, limit=3000)
    print(f"Rows hist: {len(df_hist)}")

    # Optional Pandera validation
    if nyc311_schema is not None:
        try:
            nyc311_schema.validate(df_recent, lazy=True)
            nyc311_schema.validate(df_hist, lazy=True)
            print("Pandera schema checks passed.")
        except Exception as e:
            print("Pandera schema checks failed:", e)

    # Save CSVs
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    df_recent.to_csv(DATA_DIR / "311_recent.csv", index=False)
    df_hist.to_csv(DATA_DIR / "311_hist.csv", index=False)

    # Load into DuckDB
    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    con.execute("DROP TABLE IF EXISTS raw.nyc311_recent;")
    con.execute("DROP TABLE IF EXISTS raw.nyc311_hist;")
    con.execute("CREATE TABLE raw.nyc311_recent AS SELECT * FROM df_recent;")
    con.execute("CREATE TABLE raw.nyc311_hist AS SELECT * FROM df_hist;")
    con.close()
    print(f"Wrote DuckDB at {DB_PATH}")


if __name__ == "__main__":
    main()
