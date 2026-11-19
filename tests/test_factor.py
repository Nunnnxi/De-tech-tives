"""Tests for the Week 12 factor analysis.

What it checks:
    - data/dfw_unemployment.csv is one row per year with numeric rates.
    - reports/factor_merged.csv lines up the 1-year lag with the right year.
    - reports/factor_results.csv has exactly the two pre-registered models.

Files that haven't been built yet (e.g. a reviewer without a FRED key) make
the test SKIP, not fail.

How to run (from the repo root):
    .venv/bin/python -m pytest
"""

from pathlib import Path

import pandas as pd
import pytest

FACTOR_PATH = Path("data/dfw_unemployment.csv")
MERGED_PATH = Path("reports/factor_merged.csv")
RESULTS_PATH = Path("reports/factor_results.csv")


def load_or_skip(path):
    """Read a CSV, or skip the calling test if it hasn't been built yet."""
    if not path.exists():
        pytest.skip(f"{path} not found; run src.get_fred / src.factor first")
    return pd.read_csv(path)


def test_unemployment_one_row_per_year():
    """The factor must be one numeric row per year, starting in 1990."""
    factor = load_or_skip(FACTOR_PATH)
    assert list(factor.columns) == ["year", "unemployment"]
    assert factor["year"].is_unique
    assert factor["year"].min() == 1990
    assert factor["unemployment"].between(0, 30).all()


def test_lag_matches_previous_year():
    """unemployment_lag1 in year Y must equal unemployment in year Y-1."""
    merged = load_or_skip(MERGED_PATH).set_index("year")
    for year in merged.index[1:]:
        if year - 1 in merged.index:
            assert merged.loc[year, "unemployment_lag1"] == merged.loc[year - 1, "unemployment"]


def test_exactly_two_preregistered_models():
    """Only the primary and lag-1 models, no extra specifications."""
    results = load_or_skip(RESULTS_PATH)
    assert list(results["model"]) == ["primary", "lag1"]
    assert list(results["formula"]) == [
        "clearance ~ unemployment",
        "clearance ~ unemployment_lag1",
    ]
