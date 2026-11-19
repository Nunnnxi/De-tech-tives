"""Download the Dallas-Fort Worth unemployment rate from FRED into data/.

What it does:
    1. Calls the FRED API (Federal Reserve Bank of St. Louis) for series
       LAUMT481910000000003A: unemployment rate, Dallas-Fort Worth-Arlington
       metro area, annual, not seasonally adjusted (BLS LAUS), 1990 onward.
    2. Caches the raw JSON response to data/fred_dfw_unemployment.json. If
       that file exists, the API is NOT called again.
    3. Writes data/dfw_unemployment.csv with one row per year:
           year, unemployment      (unemployment is a percent, e.g. 4.1)

FRED sends missing values as the string "." instead of null, so values are
converted with pd.to_numeric(errors="coerce") and missing years are dropped.

Your key goes in .env at the repo root (gitignored, never commit it):
    FRED_API_KEY=paste_your_key_here
Get one free at https://fredaccount.stlouisfed.org/apikeys

How to run (from the repo root):
    .venv/bin/python -m src.get_fred
To force a fresh download, delete data/fred_dfw_unemployment.json first.
"""

import json
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

DATA_DIR = Path("data")
RAW_PATH = DATA_DIR / "fred_dfw_unemployment.json"
CSV_PATH = DATA_DIR / "dfw_unemployment.csv"

URL = "https://api.stlouisfed.org/fred/series/observations"
SERIES_ID = "LAUMT481910000000003A"  # DFW MSA unemployment rate, annual


def fetch():
    """Return FRED's list of observations, from the cache or the API."""
    if RAW_PATH.exists():
        print(f"using cache: {RAW_PATH}")
        return json.loads(RAW_PATH.read_text(encoding="utf-8"))["observations"]

    load_dotenv()  # reads .env into os.environ; must run before we look
    key = os.environ.get("FRED_API_KEY")
    if not key:
        raise SystemExit("FRED_API_KEY not set. Add it to .env at the repo root "
                         "(see the README, Week 12 setup).")

    # The series is already annual, so no frequency conversion is needed.
    response = requests.get(URL, params={
        "series_id": SERIES_ID,
        "api_key": key,
        "file_type": "json",
    }, timeout=60)
    response.raise_for_status()  # stop on a bad key (400) or server error
    payload = response.json()

    DATA_DIR.mkdir(exist_ok=True)
    RAW_PATH.write_text(json.dumps(payload), encoding="utf-8")
    print(f"downloaded {len(payload['observations'])} observations -> {RAW_PATH}")
    return payload["observations"]


def to_yearly(observations):
    """Turn FRED observations into a year, unemployment DataFrame."""
    df = pd.DataFrame(observations)
    df["year"] = df["date"].str[:4].astype(int)                     # "1990-01-01" -> 1990
    df["unemployment"] = pd.to_numeric(df["value"], errors="coerce")  # "." -> NaN
    df = df.dropna(subset=["unemployment"])
    return df[["year", "unemployment"]].sort_values("year").reset_index(drop=True)


def main():
    """Fetch (or load the cache) and write data/dfw_unemployment.csv."""
    yearly = to_yearly(fetch())
    yearly.to_csv(CSV_PATH, index=False)
    print(f"wrote {CSV_PATH}: {len(yearly)} years, "
          f"{yearly['year'].min()}-{yearly['year'].max()}")


if __name__ == "__main__":
    main()
