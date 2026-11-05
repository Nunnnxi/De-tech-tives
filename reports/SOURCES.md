# Sources

Every number in `reports/` is produced by a script in `src/`. No CSV here is hand-edited.

## Data sources

1. **Murder Accountability Project**, UCR homicide and clearance data (UCR65_25), murderdata.org, accessed 2026-11-04.
   Saved unchanged as `data/map_ucr.csv` by `src/get_data.py`.
   Used for: `dallas_series.csv` (Dallas Police Department, ORI `TXDPD00`, 1965-2025).

2. **The Washington Post**, Unsolved Homicide Database, github.com/washingtonpost/data-homicides, 2018. License: CC BY-NC-SA 4.0.
   Saved unchanged as `data/wapo_all.csv`; the Dallas extract `data/wapo_dallas.csv` has the victim name columns removed.
   Used for: `dallas_fbi_vs_wapo.csv` (stretch comparison). Covers 2007 to early 2017 (2017 is partial, 45 rows).

## Definitions (they are not the same)

- **FBI / UCR "cleared"** (MAP file, `CLR` column): a clearance by arrest **or** by exceptional means. A clearance is counted in the year it happens, even for a murder from an earlier year, so a yearly rate can exceed 100%.
- **Washington Post "Closed by arrest"**: arrest only. "Closed without arrest" is counted separately and is not included in our `wapo_arrests`.

## Files in reports/

| File | Built by | Contents |
|---|---|---|
| `dallas_series.csv` | `src/series.py` | year, reported, cleared, clearance (FBI definition). Read by weeks 10, 12, 14; columns are fixed. |
| `dallas_fbi_vs_wapo.csv` | `src/series_stretch.py` | FBI series left-joined with WaPo per-year cases and arrests |
| `dallas_unsolved_pile.csv` | `src/series_stretch.py` | reported - cleared per year and its running total |
| `dallas_unsolved_by_decade.csv` | `src/series_stretch.py` | unsolved cases summed by decade |
| `clearance_trend.png` | `src/charts.py` | Week 10 newsroom chart: FBI clearance %, 1965-2025, 0-100 axis, 2025 marked partial, 2017/2018 annotated |
| `clearance_trend_rolling.png` | `src/charts.py` | same chart plus a centered 5-year rolling average (stretch) |
| `dallas_map.html` | `src/casemap.py` | Week 10 council map: one dot per WaPo Dallas case 2007-2017, orange = Open/No arrest, green = Closed (by arrest + without arrest). No popups/tooltips. |
| `dallas_open_share_by_area.csv` | `src/casemap.py` | open-case share by 3x3 grid area, 2x2 quadrant, and the Forest Lane / Audelia corridor |
| `dallas_map_age.html` | `src/casemap.py` | same dots colored by victim age bucket (stretch). Age is "Unknown" for every Dallas record in the WaPo file, so all dots are gray. |
| `dallas_map.png` | `src/map_screenshot.py` | headless-Chrome screenshot of `dallas_map.html` for the README (stretch) |

Map basemap: Esri World Light Gray Canvas (Tiles © Esri; Esri, DeLorme, NAVTEQ). The lab specified CARTO Positron, but CARTO now requires an API key.

All outputs are aggregate counts. No victim names or victim-level records are published.
