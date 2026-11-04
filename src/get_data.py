"""Downloads the week 9 data into data/. Run from the repo root: python -m src.get_data"""
from pathlib import Path

import pandas as pd
import requests

DATA = Path("data")

# Dropbox links can rotate. If this one breaks, get the new CSV link from
# https://www.murderdata.org/p/data-docs.html
MAP_URL = ("https://www.dropbox.com/scl/fi/4y2a6yy0pv4lxffm7sa4v/UCR65_25.csv"
           "?rlkey=jhs7ktqhb9h3dnml1wety4nhb&st=7rxppnar&dl=1")
WAPO_URL = ("https://raw.githubusercontent.com/washingtonpost/"
            "data-homicides/master/homicide-data.csv")


def fetch(url: str, dest: Path) -> None:
    """Download url to dest, unless we already have the file."""
    if dest.exists():
        print(f"cached: {dest}")
        return
    r = requests.get(url, timeout=120)
    r.raise_for_status()  # stop here instead of saving an error page as a csv
    dest.write_bytes(r.content)
    print(f"saved: {dest} ({dest.stat().st_size:,} bytes)")


def main() -> None:
    DATA.mkdir(exist_ok=True)
    fetch(MAP_URL, DATA / "map_ucr.csv")
    fetch(WAPO_URL, DATA / "wapo_all.csv")

    # The Post's file is Latin-1, so reading it as UTF-8 crashes.
    wapo = pd.read_csv(DATA / "wapo_all.csv", encoding="latin-1")

    # Filter on city, not state, because the file has other Texas cities.
    # Victim names get dropped right away so they can't end up in any output.
    dallas = wapo[wapo["city"] == "Dallas"].drop(
        columns=["victim_last", "victim_first"])
    dallas.to_csv(DATA / "wapo_dallas.csv", index=False)
    print(f"wapo_dallas.csv: {len(dallas)} rows (expect 1567)")


if __name__ == "__main__":
    main()
