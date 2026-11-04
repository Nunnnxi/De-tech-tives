"""Build the Dallas Police Department homicide clearance series (Deliverable #1).

What it does:
    1. Inspects both raw files (shape, columns, head, missing values) before
       any analysis, so we know what we are working with.
    2. Pulls the Dallas Police Department (ORI TXDPD00) rows out of the
       MAP / FBI UCR archive and builds one row per year:
       year, reported, cleared, clearance.
    3. Writes reports/dallas_series.csv. Weeks 10, 12 and 14 read this
       file, so its four columns must not change.
    4. Checks known anchor values (PASS/FAIL), runs the three required
       sanity checks, and prints the 5 most suspicious years with a reason.

Definition note: this series uses the FBI UCR definition of "cleared",
which is a clearance by arrest OR by "exceptional means" (e.g. the
suspect died or the prosecutor declined). That is broader than The
Washington Post's "Closed by arrest", which counts arrests only.

Only aggregate counts are used. No victim-level data is read here except
in inspect_sources(), and the Post extract it reads already has the victim
name columns removed.

How to run (from the repo root, after `python -m src.get_data`):
    .venv/bin/python -m src.series
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
REPORTS_DIR = Path("reports")
MAP_PATH = DATA_DIR / "map_ucr.csv"
WAPO_DALLAS_PATH = DATA_DIR / "wapo_dallas.csv"
SERIES_PATH = REPORTS_DIR / "dallas_series.csv"

# ORI is the FBI's unique agency code. TXDPD00 = Dallas Police Department.
# We filter on ORI and NOT on Agency == "Dallas", because that name matches
# four different agencies (Dallas TX, GA, NC and OR). Dallas County Sheriff
# (TX05700) is also a different agency, and the ORI filter excludes it.
DALLAS_ORI = "TXDPD00"

# The archive covers 1965-2025, so Dallas should have one row per year.
FIRST_YEAR = 1965
LAST_YEAR = 2025
EXPECTED_DALLAS_ROWS = LAST_YEAR - FIRST_YEAR + 1  # 61

# Known values to check against: year -> (reported, cleared).
# If any of these fail, the filter or the source changed.
ANCHORS = {
    1965: (116, 109),  # first year in the archive
    1991: (500, 350),  # the peak year for murders reported
    2020: (247, 130),
    2025: (139, 72),   # partial year, still being reported
}


def heading(title):
    """Print a clear section heading so the output is easy to paste into the PR."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def inspect_sources():
    """Print shape, columns, head() and missing-value counts for both raw files.

    We look before we analyze (shape -> head -> columns). The MAP file's real
    columns are YEAR, MRD (murders reported) and CLR (murders cleared), not
    the Year/Homicides/Cleared shown in the lecture deck's example.
    The MAP "Name" column is the AGENCY name, not a person.
    """
    heading("STEP 3: INSPECT SOURCES")

    # MAP / FBI UCR archive: one row per agency per year.
    map_ucr = pd.read_csv(MAP_PATH)
    print(f"\n--- {MAP_PATH} ---")
    print("shape:", map_ucr.shape)
    print("columns:", list(map_ucr.columns))
    print(map_ucr.head())
    print("missing values per column:")
    print(map_ucr.isna().sum())
    # How many distinct agencies are in the file.
    print("distinct agencies (ORI):", map_ucr["ORI"].nunique())

    # Washington Post Dallas extract: one row per homicide.
    # get_data.py already dropped victim_first / victim_last, but we drop
    # them again here (errors="ignore") so names can never be printed even
    # if someone rebuilt the file differently.
    wapo = pd.read_csv(WAPO_DALLAS_PATH)
    wapo = wapo.drop(columns=["victim_first", "victim_last"], errors="ignore")
    print(f"\n--- {WAPO_DALLAS_PATH} ---")
    print("shape:", wapo.shape)
    print("columns:", list(wapo.columns))
    print(wapo.head())
    print("missing values per column:")
    print(wapo.isna().sum())


def load_dallas():
    """Load the MAP archive and return only the Dallas Police Department rows.

    Prints the Dallas row count and warns if it isn't 61 (one per year,
    1965-2025), because the series shouldn't be trusted until that holds.
    """
    map_ucr = pd.read_csv(MAP_PATH)

    # Filter on the agency code, not the name (see DALLAS_ORI above).
    dallas = map_ucr[map_ucr["ORI"] == DALLAS_ORI]

    heading("DALLAS ROW COUNT")
    print(f"Dallas PD ({DALLAS_ORI}) rows: {len(dallas)}")
    print(f"years: {dallas['YEAR'].min()} to {dallas['YEAR'].max()}")
    if len(dallas) == EXPECTED_DALLAS_ROWS:
        print(f"OK: {EXPECTED_DALLAS_ROWS} rows ({FIRST_YEAR}-{LAST_YEAR})")
    else:
        print(f"WARNING: expected {EXPECTED_DALLAS_ROWS} rows, got {len(dallas)}")

    # sum() treats a missing CLR as 0, which would quietly under-count
    # clearances. Warn so a missing value is noticed and not hidden.
    missing_clr = dallas["CLR"].isna().sum()
    if missing_clr:
        print(f"WARNING: {missing_clr} Dallas rows have missing CLR (counted as 0)")
    return dallas


def build_series(dallas):
    """Aggregate Dallas rows to one row per year.

    Columns: reported (sum of MRD), cleared (sum of CLR), and
    clearance = cleared / reported. The index is named "year".
    "cleared" uses the FBI definition: arrest OR exceptional clearance.
    """
    # groupby + sum gives one row per year. Dallas has one row per year
    # already, but summing is still correct if a year ever appears twice.
    per_year = dallas.groupby("YEAR").agg(
        reported=("MRD", "sum"),
        cleared=("CLR", "sum"),
    )

    # CLR is stored as a float in the source (because other agencies have
    # blanks). Counts are whole numbers, so store them as integers to keep
    # the CSV clean (109, not 109.0).
    per_year["cleared"] = per_year["cleared"].astype(int)

    # Clearance rate. Can exceed 1.0 because the FBI counts a clearance in
    # the year it happens, even if the murder happened in an earlier year.
    per_year["clearance"] = per_year["cleared"] / per_year["reported"]

    # Lowercase name so the CSV header reads: year, reported, cleared, clearance
    per_year.index.name = "year"
    return per_year


def write_series(per_year):
    """Write reports/dallas_series.csv with exactly year, reported, cleared, clearance.

    Later weeks read this file, so we select the three value columns
    explicitly. That way no extra column can get in by accident.
    """
    REPORTS_DIR.mkdir(exist_ok=True)
    per_year[["reported", "cleared", "clearance"]].to_csv(SERIES_PATH)
    print(f"\nwrote {SERIES_PATH} ({len(per_year)} rows)")


def check_anchors(per_year):
    """Compare known reported/cleared values to the series and print PASS/FAIL.

    Also confirms 1991 is the peak year for murders reported.
    Returns True only if every check passes.
    """
    heading("ANCHOR CHECKS")
    all_pass = True

    # Compare each anchor year's values to what we built.
    for year, (exp_rep, exp_clr) in ANCHORS.items():
        if year in per_year.index:
            got_rep = int(per_year.loc[year, "reported"])
            got_clr = int(per_year.loc[year, "cleared"])
            ok = (got_rep, got_clr) == (exp_rep, exp_clr)
        else:
            got_rep = got_clr = None
            ok = False
        all_pass = all_pass and ok
        print(
            f"{'PASS' if ok else 'FAIL'}  {year}: expected {exp_rep}/{exp_clr}, "
            f"got {got_rep}/{got_clr}"
        )

    # 1991 should be the single highest year for murders reported.
    peak_year = int(per_year["reported"].idxmax())
    ok = peak_year == 1991
    all_pass = all_pass and ok
    print(f"{'PASS' if ok else 'FAIL'}  peak reported year: expected 1991, got {peak_year}")
    return all_pass


def sanity_checks(per_year):
    """Run the three required sanity checks and print each under its own heading.

    1. Rates over 100%: a FINDING about how clearances are counted, not a bug.
    2. Missing years: listed, never filled in.
    3. Biggest year-over-year changes in the clearance rate.
    Returns (over_100, missing_years, top_jumps) so other code can reuse them.
    """
    # --- Check 1: clearance > 100% ---
    heading("SANITY CHECK 1: CLEARANCE RATES OVER 100%")
    over_100 = per_year[per_year["clearance"] > 1]
    if over_100.empty:
        print("None. No year has clearance > 100%.")
    else:
        print(over_100)
        # This is not a data error. The FBI counts a clearance in the year
        # it happens, so arrests in older (prior-year) cases add to this
        # year's numerator but not its denominator. Dallas's own Datapoints
        # dashboard says its measure "can exceed 100%".
        print(
            "FINDING (not a bug): clearances of prior-year cases are counted "
            "in the year they are cleared, which can push the rate above 100%."
        )

    # --- Check 2: missing years ---
    heading("SANITY CHECK 2: MISSING YEARS")
    # Every year we expect, minus every year we have = the gaps.
    missing_years = sorted(set(range(FIRST_YEAR, LAST_YEAR + 1)) - set(per_year.index))
    if missing_years:
        # We list gaps; we never fill them in (no guessing or interpolating).
        print(f"Missing years (NOTED, not filled in): {missing_years}")
    else:
        print(f"None. Every year {FIRST_YEAR}-{LAST_YEAR} is present.")

    # --- Check 3: biggest year-over-year changes ---
    heading("SANITY CHECK 3: TOP 5 YEAR-OVER-YEAR CLEARANCE JUMPS")
    # diff() = this year's rate minus last year's; abs() so drops and rises
    # rank together. The year shown is the year the jump lands in.
    top_jumps = per_year["clearance"].diff().abs().sort_values(ascending=False).head(5)
    for year, jump in top_jumps.items():
        prev = per_year.loc[year - 1, "clearance"]
        cur = per_year.loc[year, "clearance"]
        print(f"{year}: {jump * 100:5.1f} pts  ({prev:.1%} -> {cur:.1%})")

    return over_100, missing_years, top_jumps


def pct(per_year, year):
    """Return a year's clearance rate formatted as a percent, e.g. '79.6%'."""
    return f"{per_year.loc[year, 'clearance']:.1%}"


def suspicious_years(per_year, over_100, missing_years):
    """Print the 5 most suspicious years, each with a one-line reason.

    The years were picked by reviewing the sanity-check output. Every number
    in the reasons is read from per_year, not typed in, so the text stays
    true if the data changes. Any >100% or missing years go to the front of
    the list, because they matter most.
    """
    heading("THE 5 MOST SUSPICIOUS YEARS")
    reasons = []

    # Rates over 100% and missing years always count as suspicious.
    for year in over_100.index:
        reasons.append((year, f"clearance {pct(per_year, year)} is over 100%; prior-year clearances inflate the numerator."))
    for year in missing_years:
        reasons.append((year, "no row in the source; gap noted, not filled."))

    # 2018: the lowest rate in the whole series, right after the 2017 high.
    r = per_year
    reasons.append((2018,
        f"lowest clearance of all {len(r)} years ({pct(r, 2018)}, "
        f"{r.loc[2018, 'cleared']} of {r.loc[2018, 'reported']}), a "
        f"{(r.loc[2017, 'clearance'] - r.loc[2018, 'clearance']) * 100:.1f}-pt "
        "drop right after 2017; the largest one-year move in the series."))

    # 2017: clearances jump while murders fall. This looks like a backlog
    # being cleared (prior-year cases counted in 2017), not better policing.
    reasons.append((2017,
        f"clearance jumps {pct(r, 2016)} -> {pct(r, 2017)}: cleared rose "
        f"{r.loc[2016, 'cleared']} -> {r.loc[2017, 'cleared']} while reported "
        f"fell {r.loc[2016, 'reported']} -> {r.loc[2017, 'reported']}; "
        "looks like old cases being cleared in bulk."))

    # 2007: we checked the "2007-2011 slide". The data shows one step down
    # in 2007, then a flat ~65% through 2011, so the step is what's odd.
    reasons.append((2007,
        f"one-step drop {pct(r, 2006)} -> {pct(r, 2007)} (3rd-largest jump), "
        f"then flat {pct(r, 2008)}-{pct(r, 2011)} through 2011; "
        "a step, not a gradual slide. Also the first year WaPo covers."))

    # 1974: a single bad year surrounded by ~90% years.
    reasons.append((1974,
        f"isolated dip to {pct(r, 1974)} between {pct(r, 1973)} (1973) and "
        f"{pct(r, 1975)} (1975); cleared fell to {r.loc[1974, 'cleared']} "
        "then bounced back. Possible reporting gap."))

    # 2025: the year isn't finished being reported, so it will change.
    reasons.append((2025,
        f"partial year ({r.loc[2025, 'reported']} reported, "
        f"{r.loc[2025, 'cleared']} cleared, {pct(r, 2025)}); still being "
        "reported, so not comparable to full years yet."))

    # Keep the top 5. >100%/missing years (if any) come first.
    for year, reason in reasons[:5]:
        print(f"{year}: {reason}")


def main():
    """Inspect sources, build and write the series, then run all checks."""
    inspect_sources()
    dallas = load_dallas()
    per_year = build_series(dallas)
    write_series(per_year)
    check_anchors(per_year)
    over_100, missing_years, _ = sanity_checks(per_year)
    suspicious_years(per_year, over_100, missing_years)


# Only run when executed directly (python -m src.series), not on import.
if __name__ == "__main__":
    main()
