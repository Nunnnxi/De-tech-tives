"""Map every Dallas homicide in the Washington Post data for a council office (Week 10).

What it does:
    1. Reads data/wapo_dallas.csv (built by src/get_data.py; victim names
       already removed) and drops rows with no lat/lon.
    2. Saves reports/dallas_map.html: one dot per case, orange = open / no
       arrest, green = closed, with a fixed legend showing counts and source.
    3. Prints the open-case share by area of the city (a simple 3x3 grid)
       and for the Forest Lane / Audelia Road corridor, so we can describe
       where open cases pool. Also saved as reports/dallas_open_share_by_area.csv.
    4. Stretch: saves reports/dallas_map_age.html, the same dots colored by
       victim age bucket.

Definitions: the map uses WaPo dispositions, NOT the FBI "cleared" count.
    "Open/No arrest"        -> orange
    "Closed by arrest"      -> green
    "Closed without arrest" -> green (WaPo's second "closed" category)

Privacy: the dots have no popups or tooltips. Nothing about any person is
shown or written to the HTML, only a position and a color.

How to run (from the repo root, after src.get_data):
    .venv/bin/python -m src.casemap
"""

from pathlib import Path

import folium
import pandas as pd

DATA_DIR = Path("data")
REPORTS_DIR = Path("reports")
WAPO_DALLAS_PATH = DATA_DIR / "wapo_dallas.csv"
MAP_PATH = REPORTS_DIR / "dallas_map.html"
AGE_MAP_PATH = REPORTS_DIR / "dallas_map_age.html"
AREA_PATH = REPORTS_DIR / "dallas_open_share_by_area.csv"

# Map center (roughly downtown Dallas) and a light base map so colored
# dots stand out.
CENTER = [32.78, -96.80]
ZOOM = 11
# The lab specifies tiles="cartodbpositron", but CARTO now requires an API
# key: without one every tile is an "API KEY REQUIRED" placeholder image.
# Esri's World Light Gray Canvas is a similar light-gray basemap that needs
# no key, and folium adds its attribution automatically.
TILES = "Esri.WorldGrayCanvas"

ORANGE = "#E67E22"  # open / no arrest
GREEN = "#1E8449"   # closed (by arrest or without arrest)

OPEN = "Open/No arrest"
BY_ARREST = "Closed by arrest"
WITHOUT_ARREST = "Closed without arrest"

LEGEND_TITLE = "Dallas homicides 2007-2017"
SOURCE_TEXT = "Source: Washington Post Unsolved Homicide Database"

# Grid lines for the "where does orange pool" analysis. They are about
# 4-5 km either side of downtown, giving 9 areas named in plain words.
LAT_SOUTH_EDGE, LAT_NORTH_EDGE = 32.74, 32.82
LON_WEST_EDGE, LON_EAST_EDGE = -96.85, -96.75

# Forest Lane / Audelia Road corridor in northeast Dallas (approximate box).
CORRIDOR = {"lat": (32.90, 32.93), "lon": (-96.75, -96.70)}

# Age buckets for the stretch map. right=False means each bin includes its
# left edge: [0, 18) is 0-17, [18, 25) is 18-24, and so on.
AGE_BINS = [0, 18, 25, 35, 50, float("inf")]
AGE_LABELS = ["0-17", "18-24", "25-34", "35-49", "50+"]
AGE_COLORS = {
    "0-17": "#7B3294",
    "18-24": "#C2A5CF",
    "25-34": "#E66101",
    "35-49": "#FDB863",
    "50+": "#5E3C99",
    "Unknown": "#9E9E9E",  # gray, so "no data" never looks like a real group
}


def load_cases():
    """Read the Dallas WaPo file and drop rows that can't be placed on a map.

    A single NaN lat or lon can make Leaflet render a blank map, so those
    rows are removed. Prints how many were dropped so nothing disappears
    without being noticed.
    """
    cases = pd.read_csv(WAPO_DALLAS_PATH)
    before = len(cases)
    cases = cases.dropna(subset=["lat", "lon"])
    dropped = before - len(cases)
    print(f"rows read: {before:,}; dropped for missing lat/lon: {dropped}; kept: {len(cases):,}")
    return cases


def disposition_counts(cases):
    """Count each WaPo disposition, plus the combined "closed" total for green.

    Green mixes WaPo's two closed categories (by arrest and without arrest),
    so the legend shows the split to stay honest about what green means.
    """
    counts = cases["disposition"].value_counts()
    by_arrest = int(counts.get(BY_ARREST, 0))
    without = int(counts.get(WITHOUT_ARREST, 0))
    return {
        "open": int(counts.get(OPEN, 0)),
        "by_arrest": by_arrest,
        "without_arrest": without,
        # Anything that isn't "Open/No arrest" is drawn green, so count it
        # the same way: total minus open.
        "closed": len(cases) - int(counts.get(OPEN, 0)),
    }


def add_legend(m, title, rows, note=None):
    """Pin a fixed-position HTML legend to the bottom-left of a folium map.

    rows is a list of (color, label) pairs. position: fixed keeps the
    legend in place when the reader pans or zooms. Only aggregate text goes
    in it.
    """
    # One colored dot plus its label per row.
    items = "".join(
        f'<div><span style="display:inline-block;width:11px;height:11px;'
        f'border-radius:50%;background:{color};margin-right:6px;"></span>{label}</div>'
        for color, label in rows
    )
    note_html = f'<div style="margin-top:4px;font-style:italic;">{note}</div>' if note else ""
    html = f"""
    <div id="map-legend" style="position: fixed; bottom: 24px; left: 24px; z-index: 9999;
         background: white; padding: 8px 12px; border: 1px solid #999; border-radius: 6px;
         font: 13px/1.5 Arial, sans-serif; box-shadow: 0 1px 4px rgba(0,0,0,0.3);">
      <div style="font-weight: bold; margin-bottom: 4px;">{title}</div>
      {items}
      {note_html}
      <div style="margin-top: 4px; font-size: 11px; color: #555;">{SOURCE_TEXT}</div>
    </div>
    """
    # Add the legend to the page itself (not as a map layer), so it is
    # saved inside the HTML file.
    m.get_root().html.add_child(folium.Element(html))


def new_map():
    """Create an empty base map centered on Dallas."""
    return folium.Map(location=CENTER, zoom_start=ZOOM, tiles=TILES)


def add_dot(m, lat, lon, color):
    """Add one small case dot. Deliberately no popup or tooltip (privacy)."""
    folium.CircleMarker(
        location=[lat, lon],
        radius=3,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        weight=1,
    ).add_to(m)


def disposition_map(cases):
    """Required map: dots colored by disposition, legend, saved to dallas_map.html."""
    m = new_map()

    # itertuples is a fast row loop. We only touch lat, lon and disposition.
    n_markers = 0
    for row in cases.itertuples(index=False):
        color = ORANGE if row.disposition == OPEN else GREEN
        add_dot(m, row.lat, row.lon, color)
        n_markers += 1
    print(f"markers drawn: {n_markers:,}")

    # Counts come from the data, not typed in.
    c = disposition_counts(cases)
    print(
        f"legend counts: open {c['open']:,}; closed {c['closed']:,} "
        f"= {c['by_arrest']:,} by arrest + {c['without_arrest']:,} without arrest"
    )
    add_legend(m, LEGEND_TITLE, [
        (ORANGE, f"Open / no arrest ({c['open']:,})"),
        (GREEN, f"Closed ({c['closed']:,}: {c['by_arrest']:,} by arrest "
                f"+ {c['without_arrest']:,} without arrest)"),
    ])

    REPORTS_DIR.mkdir(exist_ok=True)
    m.save(str(MAP_PATH))
    print(f"wrote {MAP_PATH}")
    return n_markers


def area_name(lat, lon):
    """Name the 3x3 grid area a point falls in, e.g. "southeast" or "central"."""
    # North/south part of the name from latitude.
    ns = "south" if lat < LAT_SOUTH_EDGE else "north" if lat >= LAT_NORTH_EDGE else ""
    # East/west part of the name from longitude (more negative = further west).
    ew = "west" if lon < LON_WEST_EDGE else "east" if lon >= LON_EAST_EDGE else ""
    return (ns + ew) or "central"


def where_orange_pools(cases):
    """Print and save the open-case share by area and for the NE corridor.

    Share = open cases / all cases in that area. Compare each area to the
    citywide share: higher means orange "pools" there. Areas with few cases
    can swing a lot, so case counts are shown next to every share.
    """
    print("\n" + "=" * 70)
    print("WHERE DOES ORANGE POOL? (open / no arrest share by area)")
    print("=" * 70)

    df = cases[["lat", "lon", "disposition"]].copy()
    df["is_open"] = df["disposition"] == OPEN
    df["area"] = [area_name(lat, lon) for lat, lon in zip(df["lat"], df["lon"])]

    citywide = df["is_open"].mean()
    print(f"citywide open share: {citywide:.1%} ({df['is_open'].sum():,} of {len(df):,})")
    print(
        f"grid: south < {LAT_SOUTH_EDGE} <= central < {LAT_NORTH_EDGE} <= north (lat); "
        f"west < {LON_WEST_EDGE} <= central < {LON_EAST_EDGE} <= east (lon)\n"
    )

    by_area = summarize_areas(df, "area", citywide)
    print("3x3 grid:")
    print(by_area.round(3).to_string())

    # Same question with a simpler 2x2 split at downtown. Results that change
    # between the two splits are fragile and shouldn't be claimed strongly.
    df["quadrant"] = [
        ("south" if lat < CENTER[0] else "north") + ("west" if lon < CENTER[1] else "east")
        for lat, lon in zip(df["lat"], df["lon"])
    ]
    by_quadrant = summarize_areas(df, "quadrant", citywide)
    print(f"\n2x2 split at downtown (lat {CENTER[0]}, lon {CENTER[1]}):")
    print(by_quadrant.round(3).to_string())

    # The specific corridor we were asked about.
    in_box = (
        df["lat"].between(*CORRIDOR["lat"]) & df["lon"].between(*CORRIDOR["lon"])
    )
    box = df[in_box]
    box_share = box["is_open"].mean() if len(box) else float("nan")
    print(
        f"\nForest Lane / Audelia corridor (lat {CORRIDOR['lat']}, lon {CORRIDOR['lon']}): "
        f"{box['is_open'].sum()} open of {len(box)} cases = {box_share:.1%} "
        f"({(box_share - citywide) * 100:+.1f} pts vs citywide)"
    )

    # Save both tables plus corridor and citywide rows so the PR numbers come
    # from a file. "grid" says which split each row belongs to.
    n_open = int(df["is_open"].sum())
    extra = pd.DataFrame(
        {
            "cases": [len(box), len(df)],
            "open": [int(box["is_open"].sum()), n_open],
            "open_share": [box_share, citywide],
            "vs_citywide_pts": [(box_share - citywide) * 100, 0.0],
            "share_of_all_open": [box["is_open"].sum() / n_open, 1.0],
        },
        index=["forest_audelia_corridor", "citywide"],
    )
    out = pd.concat(
        [by_area.assign(grid="3x3"), by_quadrant.assign(grid="2x2"), extra.assign(grid="other")]
    )
    out.index.name = "area"
    out.to_csv(AREA_PATH)
    print(f"wrote {AREA_PATH}")
    return out


def summarize_areas(df, column, citywide):
    """Group cases by an area column and compare each area's open share to citywide.

    cases             = all homicides in the area
    open              = open / no arrest cases in the area
    open_share        = open / cases (how often cases there stay open)
    vs_citywide_pts   = open_share minus citywide, in percentage points
    share_of_all_open = this area's slice of ALL open cases citywide (where
                        the orange dots physically are, which mostly follows
                        where homicides happen)
    """
    t = df.groupby(column).agg(cases=("is_open", "size"), open=("is_open", "sum"))
    t["open_share"] = t["open"] / t["cases"]
    t["vs_citywide_pts"] = (t["open_share"] - citywide) * 100
    t["share_of_all_open"] = t["open"] / df["is_open"].sum()
    return t.sort_values("open_share", ascending=False)


def age_map(cases):
    """Stretch: dots colored by victim age bucket, saved to dallas_map_age.html.

    Ages are text in the source (some say "Unknown"), so to_numeric with
    errors="coerce" turns anything that isn't a number into NaN, which we
    label "Unknown" with its own gray color. Only the bucket is used, never
    the exact age.
    """
    age = pd.to_numeric(cases["victim_age"], errors="coerce")
    bucket = pd.cut(age, bins=AGE_BINS, labels=AGE_LABELS, right=False)
    # cut returns a Categorical; add "Unknown" as a category before filling.
    bucket = bucket.cat.add_categories("Unknown").fillna("Unknown")

    m = new_map()
    for lat, lon, b in zip(cases["lat"], cases["lon"], bucket):
        add_dot(m, lat, lon, AGE_COLORS[b])

    # Legend lists every bucket, including empty ones, so the reader sees
    # what is missing.
    counts = bucket.value_counts()
    print("\nage bucket counts:", {k: int(counts.get(k, 0)) for k in AGE_COLORS})
    rows = [(AGE_COLORS[k], f"{k} ({int(counts.get(k, 0)):,})") for k in AGE_COLORS]

    # If every age is unknown, say so on the map rather than leaving readers
    # to wonder why it's all gray.
    note = None
    if counts.get("Unknown", 0) == len(cases):
        note = "Age is not recorded for any Dallas case in this source."
        print("NOTE: every Dallas record has victim_age = Unknown; the age map is all gray.")

    add_legend(m, "Dallas homicides 2007-2017 by victim age", rows, note)
    m.save(str(AGE_MAP_PATH))
    print(f"wrote {AGE_MAP_PATH}")


def main():
    """Build the disposition map, print the pooling analysis, build the age map."""
    cases = load_cases()
    disposition_map(cases)
    where_orange_pools(cases)
    age_map(cases)


# Only run when executed directly (python -m src.casemap), not on import.
if __name__ == "__main__":
    main()
