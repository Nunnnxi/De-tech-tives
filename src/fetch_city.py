"""Fetch every murder incident from the Dallas OpenData police feed into data/case.db.

What it does:
    1. Pages through the City of Dallas "Police Incidents" API (resource
       qv6i-rri7, June 2014 to now) for murder rows, using your own app token.
    2. Caches the raw JSON to data/raw_incidents.json. If that file already
       exists, the API is NOT called again (fetch once, don't hammer it).
    3. Flattens the nested location column into lat / lon and turns servyr
       (a string in the API) into a number.
    4. Writes everything to the "incidents" table in data/case.db (SQLite).
    5. Copies rows with an impossible service year (e.g. 1011, 1967) into a
       "quarantine" table so they are documented, not silently deleted.

"Murder" here = offincident contains MURDER or equals HOMICIDE. We do not
filter on nibrs_crime_category, because it is only filled in from 2017 on.

Your token goes in a .env file at the repo root (gitignored, never commit it):
    DALLAS_APP_TOKEN=paste_your_token_here

How to run (from the repo root):
    .venv/bin/python -m src.fetch_city
To force a fresh download, delete data/raw_incidents.json first.
"""

import json
import os
import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

DATA_DIR = Path("data")
RAW_PATH = DATA_DIR / "raw_incidents.json"
DB_PATH = DATA_DIR / "case.db"

URL = "https://www.dallasopendata.com/resource/qv6i-rri7.json"

# SODA (the API's query language) filter for murder rows.
WHERE = "offincident like '%MURDER%' OR offincident = 'HOMICIDE'"

# Rows per request. The full murder set is about 1,200 rows, so this is
# usually one page, but the loop still handles more.
PAGE_SIZE = 5000

# The feed starts June 1, 2014. Any service year outside 2014..this year is
# a data-entry error and goes to quarantine.
FIRST_YEAR = 2014
LAST_YEAR = date.today().year


def get_token():
    """Return the app token from .env, or None (with a warning) if it isn't set.

    Without a token the API still answers, but requests share a throttled
    pool and can fail with HTTP 429. Every detective should use their own.
    """
    load_dotenv()  # reads .env into os.environ; must run before we look
    token = os.environ.get("DALLAS_APP_TOKEN")
    if not token:
        print("WARNING: DALLAS_APP_TOKEN not set in .env; fetching without a token "
              "(may be throttled with HTTP 429).")
    return token


def fetch_all():
    """Return every murder row as a list of dicts, from the cache or the API."""
    if RAW_PATH.exists():
        print(f"using cache: {RAW_PATH}")
        return json.loads(RAW_PATH.read_text(encoding="utf-8"))

    token = get_token()
    rows, offset = [], 0
    while True:
        # Params go in a dict so requests URL-encodes the quotes and % signs.
        # $order is required: without a stable order, paging can repeat rows.
        params = {
            "$where": WHERE,
            "$order": "incidentnum",
            "$limit": PAGE_SIZE,
            "$offset": offset,
        }
        if token:
            params["$$app_token"] = token

        response = requests.get(URL, params=params, timeout=60)
        response.raise_for_status()  # stop on 400/429/500 instead of saving junk
        page = response.json()
        rows.extend(page)
        print(f"offset {offset}: {len(page)} rows")

        # A short page means we've reached the end.
        if len(page) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    DATA_DIR.mkdir(exist_ok=True)
    RAW_PATH.write_text(json.dumps(rows), encoding="utf-8")
    print(f"cached {len(rows)} rows to {RAW_PATH}")
    return rows


def flatten(rows):
    """Turn the raw list of dicts into a flat DataFrame that SQLite can store."""
    df = pd.DataFrame(rows)

    # geocoded_column is a nested dict ({latitude, longitude, human_address}).
    # SQLite can't store a dict, so pull out lat / lon as numbers.
    geo = df.pop("geocoded_column") if "geocoded_column" in df else pd.Series(dtype=object)
    df["lat"] = geo.apply(lambda g: float(g["latitude"]) if isinstance(g, dict) and "latitude" in g else None)
    df["lon"] = geo.apply(lambda g: float(g["longitude"]) if isinstance(g, dict) and "longitude" in g else None)

    # Drop the portal's computed-region columns (names start with ":@").
    df = df[[c for c in df.columns if not c.startswith(":@")]]

    # Any other nested value would also break to_sql, so store it as JSON text.
    for col in df.columns:
        if df[col].apply(lambda v: isinstance(v, (dict, list))).any():
            df[col] = df[col].apply(lambda v: json.dumps(v) if isinstance(v, (dict, list)) else v)

    # servyr comes from the API as a string; make it a number so it groups
    # and compares correctly. Unparseable values become NaN.
    df["servyr"] = pd.to_numeric(df["servyr"], errors="coerce")
    return df


def quarantine(df):
    """Return the rows whose service year is missing or outside 2014..this year."""
    bad = ~df["servyr"].between(FIRST_YEAR, LAST_YEAR)
    return df[bad]


def main():
    """Fetch (or load the cache), flatten, and write incidents + quarantine to case.db."""
    df = flatten(fetch_all())
    bad = quarantine(df)

    DATA_DIR.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        # All rows go into incidents; bad years are flagged in quarantine too.
        df.to_sql("incidents", con, if_exists="replace", index=False)
        bad.to_sql("quarantine", con, if_exists="replace", index=False)
        n = pd.read_sql("SELECT COUNT(*) AS n FROM incidents", con)["n"][0]
        q = pd.read_sql("SELECT COUNT(*) AS n FROM quarantine", con)["n"][0]

    print(f"\n{DB_PATH}: SELECT COUNT(*) FROM incidents -> {n}")
    print(f"{DB_PATH}: SELECT COUNT(*) FROM quarantine -> {q} "
          f"(service year missing or outside {FIRST_YEAR}-{LAST_YEAR})")
    if q:
        print(bad["servyr"].value_counts(dropna=False).sort_index().to_string())


if __name__ == "__main__":
    main()
