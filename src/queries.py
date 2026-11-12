"""Ask data/case.db three questions, then compare it to the Week 9 FBI series.

What it prints:
    Q1. Murders per service year, 2014 to now (city feed, murder filter).
    Q2. Top 5 police beats by murder count since 2014.
    Q3. Our squad's slice: % of murders in the three southern patrol
        divisions (SOUTHEAST, SOUTH CENTRAL, SOUTHWEST).
        Why: the Week 10 map showed most WaPo cases (2007-2017) in the
        southern half of the city. This checks whether that concentration
        still holds in the city's own feed, which runs past 2017.
    Gap. City per-year counts next to the FBI "reported" count (MRD) from
        reports/dallas_series.csv for the overlapping years, written to
        reports/dallas_city_vs_fbi.csv. This is the reporting-gap audit.

Definitions (they are not the same):
    - City feed "murder" = offincident contains MURDER or equals HOMICIDE.
    - FBI "reported" = MRD in the MAP / UCR file (Week 9).

Run after src.fetch_city (and src.series for the FBI file):
    .venv/bin/python -m src.queries
"""

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("data/case.db")
SERIES_PATH = Path("reports/dallas_series.csv")
GAP_PATH = Path("reports/dallas_city_vs_fbi.csv")

SOUTHERN_DIVISIONS = ("SOUTHEAST", "SOUTH CENTRAL", "SOUTHWEST")

# Q1: murders per year. servyr was stored as a number by fetch_city.
Q1_PER_YEAR = """
    SELECT CAST(servyr AS INTEGER) AS year, COUNT(*) AS murders
    FROM incidents
    WHERE servyr BETWEEN 2014 AND 2026
    GROUP BY servyr
    ORDER BY servyr
"""

# Q2: top 5 beats since 2014 (the real-data version of Week 4's toy ranking).
Q2_TOP_BEATS = """
    SELECT beat, COUNT(*) AS murders
    FROM incidents
    WHERE beat IS NOT NULL AND servyr >= 2014
    GROUP BY beat
    ORDER BY murders DESC, beat
    LIMIT 5
"""

# Q3: squad slice. In SQLite a true comparison counts as 1, so SUM() of a
# condition counts the rows where it is true.
Q3_SOUTHERN_SHARE = f"""
    SELECT
        SUM(division IN {SOUTHERN_DIVISIONS}) AS southern,
        COUNT(*) AS total,
        ROUND(100.0 * SUM(division IN {SOUTHERN_DIVISIONS}) / COUNT(*), 1)
            AS pct_southern
    FROM incidents
    WHERE servyr >= 2014
"""

# Rows vs distinct case numbers: tests the "one row per victim vs one row
# per incident" explanation for the gap.
Q_ROWS_VS_CASES = """
    SELECT COUNT(*) AS rows, COUNT(DISTINCT incidentnum) AS distinct_cases
    FROM incidents
"""


def heading(title):
    """Print a clear section heading so the output is easy to paste into the PR."""
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def city_vs_fbi(per_year):
    """Join city per-year counts to the FBI series and return the comparison.

    Uses an inner join, so only years in BOTH sources appear (2014-2025).
    2014 is partial in the city feed (starts June 1) and 2025 is partial in
    the FBI file, so those two years are flagged.
    """
    fbi = pd.read_csv(SERIES_PATH, usecols=["year", "reported"])
    gap = per_year.merge(fbi, on="year", how="inner")
    gap = gap.rename(columns={"murders": "city_murders", "reported": "fbi_reported"})
    gap["city_share_of_fbi"] = (gap["city_murders"] / gap["fbi_reported"]).round(3)
    gap["note"] = ""
    gap.loc[gap["year"] == 2014, "note"] = "city feed starts 2014-06-01"
    gap.loc[gap["year"] == 2025, "note"] = "FBI year still being reported"
    return gap


def main():
    """Run the three queries and the FBI comparison, printing each result."""
    if not DB_PATH.exists():
        raise SystemExit(f"{DB_PATH} not found; run `python -m src.fetch_city` first")

    with sqlite3.connect(DB_PATH) as con:
        per_year = pd.read_sql(Q1_PER_YEAR, con)
        top_beats = pd.read_sql(Q2_TOP_BEATS, con)
        southern = pd.read_sql(Q3_SOUTHERN_SHARE, con)
        rows_vs_cases = pd.read_sql(Q_ROWS_VS_CASES, con)

    heading("Q1. Murders per year (city feed)")
    print(per_year.to_string(index=False))

    heading("Q2. Top 5 beats since 2014")
    print(top_beats.to_string(index=False))

    heading("Q3. Squad slice: % of murders in the southern divisions")
    print(f"divisions: {', '.join(SOUTHERN_DIVISIONS)}")
    print(southern.to_string(index=False))

    heading("Gap check: rows vs distinct case numbers")
    print(rows_vs_cases.to_string(index=False))

    if not SERIES_PATH.exists():
        print(f"\n{SERIES_PATH} not found; run `python -m src.series` for the FBI comparison")
        return

    gap = city_vs_fbi(per_year)
    heading("City feed vs FBI reported (MRD), overlapping years")
    print(gap.to_string(index=False))
    full_years = gap[gap["note"] == ""]
    total_share = full_years["city_murders"].sum() / full_years["fbi_reported"].sum()
    print(f"\nfull years 2015-2024: city feed = {total_share:.1%} of the FBI count")

    gap.to_csv(GAP_PATH, index=False)
    print(f"wrote {GAP_PATH} ({len(gap)} rows)")


if __name__ == "__main__":
    main()
