"""Builds Dallas PD's clearance-by-year series and runs the audit checks.

Run from the repo root after get_data: python -m src.series
Writes reports/dallas_series.csv with columns year, reported, cleared, clearance.

"Cleared" here is the FBI definition: arrest OR exceptional means (like the
suspect died). The Washington Post only counts arrests, so don't mix the two.
"""
import pandas as pd

MAP_PATH = "data/map_ucr.csv"
WAPO_PATH = "data/wapo_dallas.csv"
OUTPUT_PATH = "reports/dallas_series.csv"

# Filter on ORI, not Agency. Agency == "Dallas" also picks up agencies in
# Georgia, North Carolina, and Oregon.
DALLAS_PD_ORI = "TXDPD00"
FIRST_YEAR = 1965
LAST_YEAR = 2025
EXPECTED_ROWS = 61  # one row per year, 1965 through 2025

# Our 5 most suspicious years, most suspicious first. 2017, 2018, 2007, and 1974
# are the 4 biggest swings from the jump check (1975 is just 1974 bouncing back).
# 2025 makes the list because the year is still being reported.
# These are questions for the audit. We don't know the causes yet.
SUSPICIOUS_YEARS = {
    2017: "Cleared cases jumped by 48 while reported murders fell by 4, so did "
          "older cases get counted in 2017, or did the reporting change?",
    2018: "Lowest rate in the whole series, right after the 2017 spike, so were "
          "clearances pushed from one year into the other?",
    2007: "Fell 23 points in one year, then stayed in the 50s and 60s through "
          "2015, and 2005-2006 look unusually high next to it, so which side "
          "is the odd one?",
    1974: "One-year V shape: cleared fell by 73 (reported only fell by 34), then "
          "bounced right back in 1975, so were clearances missing that year?",
    2025: "Partial year that's still being reported, so it isn't comparable to "
          "full years yet.",
}


def first_look(name: str, df: pd.DataFrame) -> None:
    """Print shape, columns, and head so we know what we're holding."""
    print(f"\n--- {name} ---")
    print(df.shape)
    print(df.columns.tolist())
    print(df.head())


def build_series(df: pd.DataFrame) -> pd.DataFrame:
    """Turn the national file into one row per year for Dallas PD."""
    dallas = df[df["ORI"] == DALLAS_PD_ORI]
    print(f"\nDallas PD rows: {len(dallas)} (expect {EXPECTED_ROWS})")
    if len(dallas) != EXPECTED_ROWS:
        raise ValueError(f"Expected {EXPECTED_ROWS} Dallas rows, got {len(dallas)}")

    per_year = dallas.groupby("YEAR").agg(
        reported=("MRD", "sum"),
        cleared=("CLR", "sum"),
    )
    per_year["cleared"] = per_year["cleared"].astype(int)  # CLR loads as a float
    per_year["clearance"] = per_year["cleared"] / per_year["reported"]
    per_year.index.name = "year"
    return per_year


def sanity_checks(per_year: pd.DataFrame) -> None:
    """Run the 3 required checks. Nothing gets dropped or fixed, only reported."""
    print("\nCheck 1: years with a clearance rate over 100%")
    over_100 = per_year[per_year["clearance"] > 1]
    print("none" if over_100.empty else over_100)

    print("\nCheck 2: missing years")
    expected_years = set(range(FIRST_YEAR, LAST_YEAR + 1))
    missing = sorted(expected_years - set(per_year.index))
    print(missing if missing else "none")

    print("\nCheck 3: biggest year-over-year jumps in clearance")
    jumps = per_year["clearance"].diff().abs().sort_values(ascending=False)
    print(jumps.head(5).round(3).to_string())


def print_suspicious(per_year: pd.DataFrame) -> None:
    """Print each suspicious year with its numbers and our reasoning."""
    print("\n5 most suspicious years")
    for year, reason in SUSPICIOUS_YEARS.items():
        row = per_year.loc[year]
        print(f"{year} ({int(row['cleared'])}/{int(row['reported'])}, "
              f"{row['clearance']:.1%}): {reason}")


def main() -> None:
    df = pd.read_csv(MAP_PATH)
    first_look("MAP archive", df)
    first_look("WaPo Dallas", pd.read_csv(WAPO_PATH))

    per_year = build_series(df)
    per_year.to_csv(OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH}")

    sanity_checks(per_year)
    print_suspicious(per_year)


if __name__ == "__main__":
    main()
