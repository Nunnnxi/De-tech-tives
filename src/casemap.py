"""Maps every Dallas homicide in the Washington Post data by outcome.

Run from the repo root after get_data: python -m src.casemap
Writes reports/dallas_map.html
"""
import folium
import pandas as pd

WAPO_PATH = "data/wapo_dallas.csv"
OUTPUT_PATH = "reports/dallas_map.html"
EXPECTED_MARKERS = 1567

# The handout's "cartodbpositron" tiles now need an API key and cover the map in
# "API KEY REQUIRED" watermarks, so we use a light Esri basemap that doesn't.
TILES = ("https://server.arcgisonline.com/ArcGIS/rest/services/"
         "Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}")
TILE_CREDIT = "Tiles &copy; Esri"

# Three colors, not two. "Closed without arrest" can't share green with arrests
# because the Post only counts a case as solved when it's closed by arrest.
COLORS = {
    "Open/No arrest": "#E67E00",         # orange
    "Closed by arrest": "#2E7D32",       # green
    "Closed without arrest": "#5B7FD6",  # blue
}

# Rough boxes for the areas in our PR notes: (south, north, west, east).
AREAS = {
    "Southeast": (32.60, 32.76, -96.76, -96.50),
    "South Oak Cliff": (32.60, 32.72, -96.87, -96.76),
    "Forest/Audelia": (32.88, 32.95, -96.78, -96.68),
    "Far North": (32.95, 33.10, -97.00, -96.50),
}


def add_markers(m: folium.Map, cases: pd.DataFrame) -> None:
    """Add one dot per case. No popups, since this is aggregate analysis only."""
    for _, row in cases.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=3,
            color=COLORS[row["disposition"]],
            fill=True,
            fill_opacity=0.6,
            weight=1,
        ).add_to(m)


def legend_html(cases: pd.DataFrame) -> str:
    """Build the legend with counts from the data, not typed in by hand."""
    counts = cases["disposition"].value_counts()
    rows = "".join(
        f'<span style="color:{color}">●</span> {label} ({counts[label]})<br>'
        for label, color in COLORS.items()
    )
    return f"""
<div style="position:fixed;bottom:30px;left:30px;background:white;padding:8px 12px;
border:1px solid #999;font-family:sans-serif;font-size:13px;z-index:9999">
<b>Dallas homicides, Jan 2007 to Apr 2017</b><br>
{rows}
Source: Washington Post Unsolved Homicide Database
</div>"""


def print_area_shares(cases: pd.DataFrame) -> None:
    """Compare each area's open share to the city, since dots alone can mislead.

    Lots of orange in an area could just mean lots of homicides there, so the
    share of cases still open is the fairer comparison.
    """
    is_open = cases["disposition"] == "Open/No arrest"
    print(f"Citywide: {is_open.sum()}/{len(cases)} open ({is_open.mean():.1%})")
    for name, (south, north, west, east) in AREAS.items():
        in_area = cases["lat"].between(south, north) & cases["lon"].between(west, east)
        share = is_open[in_area].mean()
        print(f"{name}: {is_open[in_area].sum()}/{in_area.sum()} open ({share:.1%})")


def main() -> None:
    cases = pd.read_csv(WAPO_PATH)

    # A missing lat or lon makes the whole map render blank, so drop those rows
    # and say how many went, since this week needs all 1,567 on the map.
    before = len(cases)
    cases = cases.dropna(subset=["lat", "lon"])
    print(f"Dropped {before - len(cases)} rows with no location")

    m = folium.Map(location=[32.78, -96.80], zoom_start=11,
                   tiles=TILES, attr=TILE_CREDIT)
    add_markers(m, cases)
    m.get_root().html.add_child(folium.Element(legend_html(cases)))
    m.save(OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH} with {len(cases)} markers (expect {EXPECTED_MARKERS})")
    print_area_shares(cases)


if __name__ == "__main__":
    main()
