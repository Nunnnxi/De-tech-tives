"""Tests for the Week 10 chart and map artifacts.

What it checks:
    - reports/clearance_trend.png exists, isn't empty, and is a real PNG.
    - reports/dallas_map.html has one CircleMarker per mappable case, contains
      the legend (title, counts, source), and has no popups or tooltips.

If an artifact (or the data used to count expected markers) hasn't been
built yet, the test is SKIPPED, not failed.

How to run (from the repo root):
    .venv/bin/python -m pytest
"""

from pathlib import Path

import pandas as pd
import pytest

TREND_PATH = Path("reports/clearance_trend.png")
MAP_PATH = Path("reports/dallas_map.html")
WAPO_DALLAS_PATH = Path("data/wapo_dallas.csv")

# Every PNG file starts with these 8 bytes. Checking them proves the file
# is an actual image and not an empty or error file named .png.
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def require(path):
    """Skip the calling test if path hasn't been built yet."""
    if not path.exists():
        pytest.skip(f"{path} not found; run the Week 9/10 scripts first")


def map_html():
    """Return the saved map's HTML text, or skip if it hasn't been built."""
    require(MAP_PATH)
    return MAP_PATH.read_text(encoding="utf-8")


def test_trend_png_exists_and_not_empty():
    """The chart PNG must exist, have content, and start with the PNG signature."""
    require(TREND_PATH)
    data = TREND_PATH.read_bytes()
    assert len(data) > 10_000  # a real 11x4.5in, 150-dpi chart is far bigger
    assert data.startswith(PNG_SIGNATURE)


def test_map_marker_count():
    """One CircleMarker per case that has coordinates (1,567 minus dropped rows).

    folium writes exactly one "L.circleMarker(" call per marker into the
    HTML, so counting that text counts the dots.
    """
    html = map_html()
    require(WAPO_DALLAS_PATH)
    expected = len(pd.read_csv(WAPO_DALLAS_PATH).dropna(subset=["lat", "lon"]))
    assert html.count("L.circleMarker(") == expected
    # Today no rows are dropped, so this should be the full 1,567.
    assert expected == 1567


def test_map_has_legend():
    """The legend's title, both category labels and the source line must be in the HTML."""
    html = map_html()
    assert 'id="map-legend"' in html
    assert "Dallas homicides 2007-2017" in html
    assert "Open / no arrest (676)" in html
    assert "Closed (891: 813 by arrest + 78 without arrest)" in html
    assert "Source: Washington Post Unsolved Homicide Database" in html


def test_map_has_no_popups_or_tooltips():
    """Privacy: dots must not carry popups or tooltips (nothing about a person)."""
    html = map_html()
    assert "bindPopup" not in html
    assert "bindTooltip" not in html
