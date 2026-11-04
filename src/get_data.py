"""Download the two raw homicide datasets into data/ so anyone can rebuild it.

What it does:
    1. Downloads the Murder Accountability Project (MAP) / FBI UCR homicide
       and clearance archive (UCR65_25.csv) and saves it UNCHANGED as
       data/map_ucr.csv.
    2. Downloads The Washington Post homicide database and saves it
       UNCHANGED as data/wapo_all.csv.
    3. Makes a Dallas-only extract of the Post file (data/wapo_dallas.csv)
       with the victim name columns removed, and checks it has 1,567 rows.

Raw files stay in data/, which is gitignored: we never commit them.
Files that already exist are not downloaded again (they are "cached").

How to run (from the repo root):
    .venv/bin/python -m src.get_data
"""

from pathlib import Path

import pandas as pd
import requests

# All raw inputs live here. Path is relative to the repo root, which is where
# `python -m src.get_data` is run from.
DATA_DIR = Path("data")

# MAP / FBI UCR clearance archive, 1965-2025. Dropbox links can rotate; if
# this one stops working, copy the current link for UCR65_25.csv from
# https://www.murderdata.org/p/data-docs.html (under "UCR clearance data").
MAP_URL = (
    "https://www.dropbox.com/scl/fi/4y2a6yy0pv4lxffm7sa4v/UCR65_25.csv"
    "?rlkey=jhs7ktqhb9h3dnml1wety4nhb&st=7rxppnar&dl=1"
)

# The Washington Post's homicide database (50 large US cities, 2007-2017).
WAPO_URL = (
    "https://raw.githubusercontent.com/washingtonpost/data-homicides/"
    "master/homicide-data.csv"
)

MAP_PATH = DATA_DIR / "map_ucr.csv"
WAPO_ALL_PATH = DATA_DIR / "wapo_all.csv"
WAPO_DALLAS_PATH = DATA_DIR / "wapo_dallas.csv"

# Number of Dallas rows we expect in the Post file. If we get a different
# number, the source changed or our filter is wrong.
EXPECTED_DALLAS_ROWS = 1567


def fetch(url, path):
    """Download url to path unless path already exists.

    Prints "cached: <path>" when the file is already there, otherwise
    prints how big the saved file is. The bytes are written exactly as
    received, so the raw file is unchanged.

    Raises requests.HTTPError on a bad HTTP status, and RuntimeError if the
    server returned an HTML page instead of a CSV (for example, a rotated
    Dropbox link that shows a "file not found" web page).
    """
    # Don't download again if we already have the file. This saves time and
    # avoids hammering the source servers.
    if path.exists():
        print(f"cached: {path}")
        return path

    # timeout=120 means a stuck server can't hang the script forever.
    # raise_for_status() stops on 404/500 errors instead of saving an
    # error page as if it were data.
    response = requests.get(url, timeout=120)
    response.raise_for_status()

    # A broken Dropbox link often comes back as status 200 with an HTML web
    # page. Check the content type and the first bytes so we never save HTML
    # as a .csv.
    content_type = response.headers.get("Content-Type", "").lower()
    first_bytes = response.content[:200].lstrip().lower()
    if "text/html" in content_type or first_bytes.startswith((b"<!doctype", b"<html")):
        raise RuntimeError(
            f"Got HTML instead of CSV from {url}. The link has probably "
            "rotated. Copy the current CSV link for UCR65_25.csv from "
            "https://www.murderdata.org/p/data-docs.html "
            '(under "UCR clearance data") and update MAP_URL in src/get_data.py.'
        )

    # Write the raw bytes. No parsing, so the file stays exactly as published.
    path.write_bytes(response.content)
    size_mb = path.stat().st_size / 1_000_000
    print(f"saved: {path} ({size_mb:.1f} MB)")
    return path


def make_wapo_dallas():
    """Build data/wapo_dallas.csv from the full Post file.

    Keeps only Dallas rows, drops the victim name columns (we only do
    aggregate analysis, so names are never needed), and checks the row count.
    Returns the Dallas DataFrame.
    """
    # The Post file is NOT UTF-8. Reading it as UTF-8 raises
    # UnicodeDecodeError, so read it as latin-1.
    wapo = pd.read_csv(WAPO_ALL_PATH, encoding="latin-1")

    # Filter on city, not state: state == "TX" would also include Houston,
    # San Antonio and Fort Worth.
    dallas = wapo[wapo["city"] == "Dallas"]

    # Remove victim names before anything is saved. Real people are in this
    # file, and nothing downstream needs their names.
    dallas = dallas.drop(columns=["victim_last", "victim_first"])

    # index=False so pandas doesn't add an unnamed row-number column.
    dallas.to_csv(WAPO_DALLAS_PATH, index=False)

    # Check the row count. A different number means the source or our filter
    # changed, so any results built on it should not be trusted yet.
    rows = len(dallas)
    print(f"wapo_dallas rows: {rows:,}")
    if rows == EXPECTED_DALLAS_ROWS:
        print(f"OK: row count matches expected {EXPECTED_DALLAS_ROWS:,}")
    else:
        print("!" * 70)
        print(
            f"WARNING: expected {EXPECTED_DALLAS_ROWS:,} Dallas rows "
            f"but got {rows:,}. Check the source before using it."
        )
        print("!" * 70)
    return dallas


def main():
    """Create data/, download both sources, and build the Dallas extract."""
    # exist_ok=True: no error if data/ is already there.
    DATA_DIR.mkdir(exist_ok=True)

    # Step 1: raw downloads, saved unchanged.
    fetch(MAP_URL, MAP_PATH)
    fetch(WAPO_URL, WAPO_ALL_PATH)

    # Step 2: derived Dallas file with names removed.
    make_wapo_dallas()


# Only run main() when this file is executed directly (python -m src.get_data),
# not when another module imports it.
if __name__ == "__main__":
    main()
