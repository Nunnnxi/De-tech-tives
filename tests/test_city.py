"""Tests for the Week 11 city feed: data/case.db and the city-vs-FBI table.

What it checks:
    - data/case.db has an incidents table with 1,100+ murder rows, numeric
      service years, flattened lat / lon, and a quarantine table.
    - The raw JSON cache exists, so a rerun won't call the API again.
    - reports/dallas_city_vs_fbi.csv has its fixed columns and 2014-2025.

Files that haven't been built yet (e.g. a reviewer without a token) make the
test SKIP, not fail.

How to run (from the repo root):
    .venv/bin/python -m pytest
"""

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

DB_PATH = Path("data/case.db")
RAW_PATH = Path("data/raw_incidents.json")
GAP_PATH = Path("reports/dallas_city_vs_fbi.csv")


@pytest.fixture
def con():
    """Open case.db, or skip if src.fetch_city hasn't been run."""
    if not DB_PATH.exists():
        pytest.skip(f"{DB_PATH} not found; run src.fetch_city first")
    connection = sqlite3.connect(DB_PATH)
    yield connection
    connection.close()


def test_incidents_row_count(con):
    """The murder filter should return the 1,100+ rows the handout expects."""
    n = pd.read_sql("SELECT COUNT(*) AS n FROM incidents", con)["n"][0]
    assert n >= 1100


def test_servyr_is_numeric(con):
    """servyr must be stored as a number, or GROUP BY / BETWEEN go wrong."""
    years = pd.read_sql("SELECT servyr FROM incidents", con)["servyr"]
    assert pd.api.types.is_numeric_dtype(years)


def test_location_was_flattened(con):
    """The nested geocoded_column must be replaced by lat / lon columns."""
    cols = pd.read_sql("SELECT * FROM incidents LIMIT 1", con).columns
    assert "lat" in cols and "lon" in cols
    assert "geocoded_column" not in cols


def test_quarantine_table_exists(con):
    """Bad service years are documented in a quarantine table, not deleted."""
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type = 'table'", con)
    assert "quarantine" in set(tables["name"])


def test_raw_cache_exists(con):
    """The raw JSON cache must exist so a rerun doesn't re-fetch from the API."""
    assert RAW_PATH.exists()


def test_city_vs_fbi_table():
    """The gap table has fixed columns and one row per overlapping year."""
    if not GAP_PATH.exists():
        pytest.skip(f"{GAP_PATH} not found; run src.queries first")
    gap = pd.read_csv(GAP_PATH)
    assert list(gap.columns) == [
        "year", "city_murders", "fbi_reported", "city_share_of_fbi", "note",
    ]
    assert list(gap["year"]) == list(range(2014, 2026))
