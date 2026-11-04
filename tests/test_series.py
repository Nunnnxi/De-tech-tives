"""Tests for the Week 9 Dallas series and the WaPo Dallas extract.

What it checks:
    - reports/dallas_series.csv has exactly the columns later weeks rely on,
      61 rows, and the known anchor values.
    - data/wapo_dallas.csv has 1,567 rows and no victim name columns.

If a file is missing (e.g. a reviewer hasn't run `python -m src.get_data`
or `python -m src.series` yet), the test is SKIPPED, not failed, so nobody
gets a false failure.

How to run (from the repo root):
    .venv/bin/python -m pytest
"""

from pathlib import Path

import pandas as pd
import pytest

SERIES_PATH = Path("reports/dallas_series.csv")
WAPO_DALLAS_PATH = Path("data/wapo_dallas.csv")


def load_or_skip(path, **read_kwargs):
    """Read a CSV, or skip the calling test if the file hasn't been built yet."""
    if not path.exists():
        pytest.skip(f"{path} not found; run src.get_data / src.series first")
    return pd.read_csv(path, **read_kwargs)


def test_series_columns_exact():
    """The series must have exactly these 4 columns in this order (weeks 10/12/14 read it)."""
    series = load_or_skip(SERIES_PATH)
    assert list(series.columns) == ["year", "reported", "cleared", "clearance"]


def test_series_has_61_rows():
    """One row per year, 1965-2025, with no gaps or duplicates."""
    series = load_or_skip(SERIES_PATH)
    assert len(series) == 61
    assert list(series["year"]) == list(range(1965, 2026))


# Each tuple is (year, reported, cleared): known values from the source.
@pytest.mark.parametrize(
    "year, reported, cleared",
    [
        (1965, 116, 109),
        (1991, 500, 350),
        (2020, 247, 130),
        (2025, 139, 72),
    ],
)
def test_series_anchor_values(year, reported, cleared):
    """Anchor years must match the known reported/cleared counts and clearance rate."""
    series = load_or_skip(SERIES_PATH, index_col="year")
    row = series.loc[year]
    assert row["reported"] == reported
    assert row["cleared"] == cleared
    # Clearance should equal cleared / reported (approx because of floats).
    assert row["clearance"] == pytest.approx(cleared / reported)


def test_wapo_dallas_row_count():
    """The Dallas extract of the Post file must have exactly 1,567 rows."""
    wapo = load_or_skip(WAPO_DALLAS_PATH)
    assert len(wapo) == 1567


def test_wapo_dallas_has_no_victim_names():
    """Victim name columns must have been dropped (aggregate analysis only)."""
    wapo = load_or_skip(WAPO_DALLAS_PATH)
    assert "victim_first" not in wapo.columns
    assert "victim_last" not in wapo.columns
