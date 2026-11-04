"""Stretch analyses on the Dallas clearance series (Week 9 stretch goals).

What it does (reads reports/dallas_series.csv, which it does NOT change):
    a) Adds The Washington Post as a second source: per-year case and
       arrest counts for Dallas, joined onto the FBI series.
       -> reports/dallas_fbi_vs_wapo.csv
    b) Builds the cumulative "unsolved pile": (reported - cleared) per year,
       added up over time.
       -> reports/dallas_unsolved_pile.csv
    c) Breaks that down by decade to find which decade added the most
       unsolved cases.
       -> reports/dallas_unsolved_by_decade.csv

Two different definitions are compared here:
    FBI "cleared"            = arrest OR exceptional clearance.
    WaPo "Closed by arrest"  = arrest only.
So WaPo's arrest rate is expected to be lower than the FBI clearance rate.

Only counts are used. No victim-level fields are written anywhere.

How to run (from the repo root, after get_data and series):
    .venv/bin/python -m src.series_stretch
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
REPORTS_DIR = Path("reports")
SERIES_PATH = REPORTS_DIR / "dallas_series.csv"
WAPO_DALLAS_PATH = DATA_DIR / "wapo_dallas.csv"

FBI_VS_WAPO_PATH = REPORTS_DIR / "dallas_fbi_vs_wapo.csv"
PILE_PATH = REPORTS_DIR / "dallas_unsolved_pile.csv"
DECADE_PATH = REPORTS_DIR / "dallas_unsolved_by_decade.csv"


def heading(title):
    """Print a clear section heading so the output is easy to paste into the PR."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def load_series():
    """Read the FBI series built by src/series.py, indexed by year."""
    return pd.read_csv(SERIES_PATH, index_col="year")


def wapo_per_year():
    """Count WaPo Dallas cases and arrests per year.

    year         = first 4 characters of reported_date (stored as YYYYMMDD)
    wapo_cases   = number of homicides (count of uid)
    wapo_arrests = number with disposition == "Closed by arrest"
    """
    # Read reported_date as text so we can safely slice the first 4 chars.
    wapo = pd.read_csv(WAPO_DALLAS_PATH, dtype={"reported_date": str})
    wapo["year"] = wapo["reported_date"].str[:4].astype(int)

    # True/False column: was this case closed by an arrest? Summing it counts
    # the Trues. WaPo's definition is arrest only.
    wapo["arrest"] = wapo["disposition"] == "Closed by arrest"

    return wapo.groupby("year").agg(
        wapo_cases=("uid", "count"),
        wapo_arrests=("arrest", "sum"),
    )


def compare_fbi_wapo(series):
    """Stretch (a): left-join WaPo counts onto the FBI series and compare.

    Left join keeps all 61 FBI years. Years WaPo doesn't cover get blanks
    (NaN), which is correct because WaPo has no data for them, not zeros.
    """
    heading("STRETCH A: FBI vs WASHINGTON POST")
    wapo = wapo_per_year()
    joined = series.join(wapo, how="left")

    # WaPo's arrest-only rate, next to the FBI's arrest-or-exceptional rate.
    joined["wapo_arrest_rate"] = joined["wapo_arrests"] / joined["wapo_cases"]
    # Positive gap = FBI counts more murders than WaPo for that year.
    joined["cases_gap"] = joined["reported"] - joined["wapo_cases"]

    REPORTS_DIR.mkdir(exist_ok=True)
    joined.to_csv(FBI_VS_WAPO_PATH)
    print(f"wrote {FBI_VS_WAPO_PATH}")

    # Show only years both sources cover.
    overlap = joined.dropna(subset=["wapo_cases"])
    print(f"WaPo covers {overlap.index.min()}-{overlap.index.max()}")
    print(overlap[["reported", "wapo_cases", "cases_gap", "clearance", "wapo_arrest_rate"]].round(3))

    # The specific year the lab asks about.
    r2010 = joined.loc[2010]
    print(
        f"\n2010: FBI reported {int(r2010['reported'])}, WaPo cases "
        f"{int(r2010['wapo_cases'])} -> gap of {int(r2010['cases_gap'])} "
        f"({r2010['cases_gap'] / r2010['reported']:.1%} of the FBI count)"
    )
    print(
        f"2010 rates: FBI clearance {r2010['clearance']:.1%} (arrest OR exceptional) "
        f"vs WaPo arrest rate {r2010['wapo_arrest_rate']:.1%} (arrest only)"
    )

    # 2017 is a partial year in WaPo (data ends early 2017), so it isn't
    # a fair comparison and shouldn't be read as a real gap.
    if 2017 in overlap.index:
        print(
            f"NOTE: WaPo 2017 is partial ({int(joined.loc[2017, 'wapo_cases'])} rows; "
            "data ends early 2017), so the 2017 gap is not a real disagreement."
        )
    return joined


def unsolved_pile(series):
    """Stretch (b): unsolved per year = reported - cleared, plus a running total.

    This is approximate. Because FBI clearances can belong to earlier years'
    cases, a year's 'unsolved' can be off, but the running total is still a
    fair picture of the backlog.
    """
    heading("STRETCH B: CUMULATIVE UNSOLVED PILE")
    pile = series[["reported", "cleared"]].copy()
    pile["unsolved"] = pile["reported"] - pile["cleared"]
    # cumsum() adds each year's unsolved onto all the years before it.
    pile["cumulative_unsolved"] = pile["unsolved"].cumsum()

    pile.to_csv(PILE_PATH)
    print(f"wrote {PILE_PATH}")

    # Print a few checkpoints instead of all 61 rows.
    for year in [1965, 1975, 1985, 1995, 2005, 2015, pile.index.max()]:
        print(f"by end of {year}: {int(pile.loc[year, 'cumulative_unsolved']):,} unsolved")
    return pile


def by_decade(pile):
    """Stretch (c): add up unsolved cases by decade and find the biggest one.

    Decade = year rounded down to a multiple of 10 (1974 -> 1970).
    The 2020s are incomplete (2020-2025 only, and 2025 is partial).
    """
    heading("STRETCH C: UNSOLVED CASES BY DECADE")
    # Integer division by 10 then times 10 drops the last digit of the year.
    decade = (pile.index // 10) * 10
    decades = pile.groupby(decade).agg(
        years=("unsolved", "count"),
        reported=("reported", "sum"),
        cleared=("cleared", "sum"),
        unsolved=("unsolved", "sum"),
    )
    decades.index.name = "decade"
    decades["clearance"] = decades["cleared"] / decades["reported"]

    decades.to_csv(DECADE_PATH)
    print(f"wrote {DECADE_PATH}")
    print(decades.round(3))

    top = decades["unsolved"].idxmax()
    print(
        f"\nDecade adding the most unsolved cases: {top}s "
        f"({int(decades.loc[top, 'unsolved']):,} unsolved of "
        f"{int(decades.loc[top, 'reported']):,} reported)"
    )
    print("NOTE: the 2020s only cover 2020-2025, and 2025 is a partial year.")
    return decades


def main():
    """Run all three stretch analyses in order."""
    series = load_series()
    compare_fbi_wapo(series)
    pile = unsolved_pile(series)
    by_decade(pile)


# Only run when executed directly (python -m src.series_stretch), not on import.
if __name__ == "__main__":
    main()
