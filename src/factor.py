"""Week 12: test our pre-registered factor against Dallas homicide clearance.

Pre-registered hypothesis (locked at standup, do not change after seeing data):
    "We hypothesize that the Dallas-Fort Worth unemployment rate is associated
    with Dallas homicide clearance, in the negative direction."

What it does:
    1. Merges reports/dallas_series.csv (FBI clearance, Week 9) with
       data/dfw_unemployment.csv (FRED, from src.get_fred) on year, and
       prints the shape and first rows so we eyeball it before modeling.
    2. Primary model:  clearance ~ unemployment          (same year)
    3. Lag-1 variant:  clearance ~ unemployment_lag1     (last year's rate)
       Tests the "budget hit comes a year later" story and reverse causation.
    4. Prints both OLS summaries (paste them into the PR) and writes:
         reports/factor_merged.csv   the merged dataset the models used
         reports/factor_results.csv  coef, p-value, R-squared, n per model
       so every number quoted in reports/factor_writeup.md is in a file.
    5. Side checks (descriptive only, NOT extra models): correlations, means
       by decade, and high- vs low-unemployment years, written to
         reports/factor_side_checks.csv
       These back the confounder discussion and the alternative explanation
       we tested after seeing the result ("fewer murders in bad times").

Clearance uses the FBI definition (arrest OR exceptional clearance).
Exactly two models, as pre-registered. Adding more until one "works" is
p-hacking.

Run after src.series and src.get_fred:
    .venv/bin/python -m src.factor
"""

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

SERIES_PATH = Path("reports/dallas_series.csv")
FACTOR_PATH = Path("data/dfw_unemployment.csv")
MERGED_PATH = Path("reports/factor_merged.csv")
RESULTS_PATH = Path("reports/factor_results.csv")
SIDE_CHECKS_PATH = Path("reports/factor_side_checks.csv")

# The two pre-registered models: name -> statsmodels formula.
MODELS = {
    "primary": "clearance ~ unemployment",
    "lag1": "clearance ~ unemployment_lag1",
}


def heading(title):
    """Print a clear section heading so the output is easy to paste into the PR."""
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def load_merged():
    """Merge the clearance series with unemployment and its 1-year lag."""
    series = pd.read_csv(SERIES_PATH)
    factor = pd.read_csv(FACTOR_PATH)

    # Cast both keys to int: a string year in one file gives a 0-row merge.
    series["year"] = series["year"].astype(int)
    factor["year"] = factor["year"].astype(int)

    # Lag by YEAR, not by row position: last year's rate is the row whose
    # year is one less. This stays correct even if a year were missing,
    # where .shift(1) would silently pair the wrong years.
    lagged = factor.rename(columns={"unemployment": "unemployment_lag1"})
    lagged["year"] = lagged["year"] + 1

    merged = (series.merge(factor, on="year", how="inner")
                    .merge(lagged, on="year", how="left"))
    return merged.sort_values("year").reset_index(drop=True)


def fit(formula, data):
    """Fit one OLS model, dropping rows with a missing value in its columns."""
    return smf.ols(formula, data=data).fit()


def results_row(name, formula, model):
    """Pull the numbers we quote (coef, p, R-squared, n) out of a fitted model."""
    term = formula.split("~")[1].strip()
    return {
        "model": name,
        "formula": formula,
        "coef": model.params[term],
        "p_value": model.pvalues[term],
        "ci_low": model.conf_int().loc[term, 0],
        "ci_high": model.conf_int().loc[term, 1],
        "r_squared": model.rsquared,
        "n": int(model.nobs),
        "first_year": None,
        "last_year": None,
    }


def side_checks(merged):
    """Descriptive numbers behind the writeup's confounders and side notes.

    Returns a long table: check, group, value, note. Nothing here is a model
    or a p-value; these are means and correlations to explain the result.
    """
    rows = []

    def add(check, group, value, note=""):
        rows.append({"check": check, "group": group, "value": round(float(value), 4), "note": note})

    # Confounder 1 (time trend) and 2 (murder volume): simple correlations.
    add("correlation", "year vs clearance", merged["year"].corr(merged["clearance"]),
        "clearance falls over time")
    add("correlation", "year vs unemployment", merged["year"].corr(merged["unemployment"]),
        "unemployment drifts slightly lower over time")
    add("correlation", "unemployment vs reported", merged["unemployment"].corr(merged["reported"]),
        "murders barely move with unemployment")
    add("correlation", "reported vs clearance", merged["reported"].corr(merged["clearance"]),
        "high-murder years had HIGHER clearance (the 1990s): the time trend again")

    # Means by period, to show the trend in plain numbers.
    periods = pd.cut(merged["year"], [1989, 1999, 2009, 2019, 2025],
                     labels=["1990s", "2000s", "2010s", "2020-25"])
    for label, grp in merged.groupby(periods, observed=True):
        add("period mean clearance", label, grp["clearance"].mean())
        add("period mean unemployment", label, grp["unemployment"].mean())
        add("period mean murders", label, grp["reported"].mean())

    # Alternative explanation tested after the result: did high-unemployment
    # years have FEWER murders (lighter caseload -> higher clearance)?
    median = merged["unemployment"].median()
    add("unemployment median", "1990-2025", median, "split point for high vs low")
    high = merged[merged["unemployment"] >= median]
    low = merged[merged["unemployment"] < median]
    for label, grp in (("high-unemployment years", high), ("low-unemployment years", low)):
        add("years", label, len(grp))
        add("mean murders", label, grp["reported"].mean())
        add("mean clearance", label, grp["clearance"].mean())

    return pd.DataFrame(rows)


def main():
    """Merge, eyeball, fit both pre-registered models, and save the results."""
    for path, cmd in ((SERIES_PATH, "src.series"), (FACTOR_PATH, "src.get_fred")):
        if not path.exists():
            raise SystemExit(f"{path} not found; run `python -m {cmd}` first")

    merged = load_merged()

    heading("Merged data (eyeball before modeling)")
    print(f"shape: {merged.shape}  years {merged['year'].min()}-{merged['year'].max()}")
    print(merged.head().to_string(index=False))

    rows = []
    for name, formula in MODELS.items():
        model = fit(formula, merged)
        used = merged.loc[model.model.data.row_labels, "year"]  # years in this model
        heading(f"{name}: {formula}")
        print(model.summary())
        row = results_row(name, formula, model)
        row["first_year"], row["last_year"] = int(used.min()), int(used.max())
        rows.append(row)

    results = pd.DataFrame(rows)
    heading("Numbers to quote")
    for r in results.itertuples():
        print(f"{r.model:8s} coef = {r.coef:+.4f}  p = {r.p_value:.3f}  "
              f"R2 = {r.r_squared:.3f}  n = {r.n} ({r.first_year}-{r.last_year})")
    print("\ncoef = change in clearance (0-1 scale) per 1 percentage point of "
          "unemployment; x100 for percentage points.")

    checks = side_checks(merged)
    heading("Side checks (descriptive only, not models)")
    print(checks.to_string(index=False))

    merged.to_csv(MERGED_PATH, index=False)
    results.to_csv(RESULTS_PATH, index=False)
    checks.to_csv(SIDE_CHECKS_PATH, index=False)
    print(f"\nwrote {MERGED_PATH} ({len(merged)} rows), {RESULTS_PATH}, {SIDE_CHECKS_PATH}")


if __name__ == "__main__":
    main()
