# De-tech-tives

ITSS 3312 squad repo.

- `src/` - package code, one `python -m src.<module>` script per step (see each week below)
- `tests/` - pytest tests, run `pytest` from the repo root
- `data/` - raw inputs
- `reports/` - outputs (CSVs, charts, maps)
- `claudefiles/` - course materials
  - `md/` - weekly supplements, data sources overview, build roadmap
  - `pptxs/` - weekly lecture decks

Each week, add the new supplement `.md` files to `claudefiles/md/` and the new decks to `claudefiles/pptxs/`.

## What the data says so far

The project uses three sources on Dallas homicides. Each defines "solved" differently, and they don't all agree.

| Source | Years | "Solved" means | Used for |
|---|---|---|---|
| FBI / Murder Accountability Project | 1965-2025 | arrest **or** exceptional clearance | `dallas_series.csv`, trend chart |
| Washington Post | 2007-early 2017 | arrest only | case map, week 13 model |
| City of Dallas live feed | June 2014-now | (no clearance used) | `case.db`, reporting-gap audit |

**1. Dallas solves a smaller share of murders than it used to.** FBI clearance fell every decade:

| Decade | Murders | Cleared |
|---|---|---|
| 1960s (from 1965) | 790 | 90% |
| 1970s | 2,295 | 86% |
| 1980s | 3,173 | 73% |
| 1990s | 3,091 | 71% |
| 2000s | 2,066 | 63% |
| 2010s | 1,522 | 59% |
| 2020s (to 2025) | 1,220 | 51% |

Murders peaked in 1991 (500). 2018 is the record-low clearance year (39.9%), and 2017 is a suspicious jump to 79.6%. Reported minus cleared, summed since 1965, leaves about 4,127 cases (`dallas_unsolved_pile.csv`).

**2. FBI and Washington Post counts agree.** For 2007-2016 the two case counts are within about 5 per year. WaPo's arrest rate is always lower than the FBI clearance rate, because WaPo counts arrests only. WaPo's 2017 is a partial year (45 cases).

**3. Murders are concentrated in the south, but so are cases of every outcome.** On the WaPo map, 43% of 1,567 cases are open. The open share is fairly even across areas (40-47%), so the south has more unsolved cases mainly because it has more cases. The city feed agrees: 61.5% of its murders are in the Southeast, South Central and Southwest divisions.

**4. The city's public feed shows about half the murders it reports to the FBI.** For the full years 2015-2024, the feed has 51.5% of the FBI count (2020: 102 vs 247). Since the FBI and WaPo agree, the feed is the odd one out. Candidate reasons: privacy filtering, cases reclassified from another offense later, and the feed being a research copy rather than the system of record. We tested one more, one row per incident instead of per victim. The feed has 1,168 rows but only 1,133 distinct case numbers, so it already has extra rows, and that reason does not explain the gap. See `reports/dallas_city_vs_fbi.csv`.

## Setup

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Week 9: Dallas clearance series

### Rebuild everything (Mac/Linux)

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m src.get_data         # downloads raw files into data/ (gitignored)
.venv/bin/python -m src.series           # writes reports/dallas_series.csv + sanity checks
.venv/bin/python -m src.series_stretch   # optional stretch outputs in reports/
.venv/bin/python -m pytest
```

### Definitions

- **FBI "cleared"** (used in `reports/dallas_series.csv`) = arrest **or** exceptional clearance.
- **WaPo "Closed by arrest"** = arrest only.

### Data sources

- Murder Accountability Project, UCR homicide and clearance data (UCR65_25), murderdata.org, accessed 2026-11-04.
- The Washington Post, Unsolved Homicide Database, github.com/washingtonpost/data-homicides, 2018 (license CC BY-NC-SA 4.0).

See `reports/SOURCES.md` for details.

## Week 10: The Picture

### Rebuild (after `src.get_data` and `src.series`)

```
.venv/bin/python -m src.charts           # reports/clearance_trend.png (+ _rolling.png)
.venv/bin/python -m src.casemap          # reports/dallas_map.html (+ dallas_map_age.html, area table)
.venv/bin/python -m src.map_screenshot   # optional: reports/dallas_map.png (needs Chrome + internet)
.venv/bin/python -m pytest
```

### What each artifact shows

- **`reports/clearance_trend.png`** (for a newsroom): Dallas Police Department homicide clearance rate for every year 1965-2025, on a 0-100% axis. 2017's jump and 2018's record low are annotated, and 2025 is marked as a partial year. Any missing year would show as a break in the line.
- **`reports/dallas_map.html`** (for a council office): every Washington Post Dallas homicide 2007-2017 as one dot. Orange = open / no arrest; green = closed. The legend gives the counts. The dots have no popups or tooltips.

![Dallas homicide map](reports/dallas_map.png)

### Definitions

- **Chart** uses the FBI "cleared" count: arrest **or** exceptional clearance (MAP / FBI UCR).
- **Map** uses Washington Post dispositions: "Open/No arrest" (orange) vs "Closed by arrest" + "Closed without arrest" (both green).

## Week 11: The Tap (live city data)

### Setup (each detective, once)

Get a free app token at dallasopendata.com (My Profile > Edit Profile > Developer Settings > Create New App Token) and put it in `.env` at the repo root. `.env` is gitignored; never commit it.

```
DALLAS_APP_TOKEN=paste_your_token_here
```

### Rebuild

```
.venv/bin/python -m src.fetch_city   # API -> data/raw_incidents.json (cache) -> data/case.db
.venv/bin/python -m src.queries      # three answers + reports/dallas_city_vs_fbi.csv
.venv/bin/python -m pytest
```

`fetch_city` only calls the API when `data/raw_incidents.json` is missing. Delete that file to re-fetch.

### Definition

- **City feed "murder"** = `offincident` contains MURDER or equals HOMICIDE (City of Dallas Police Incidents, `qv6i-rri7`, June 2014 to now).

### Squad slice

The percent of murders in the three southern patrol divisions (Southeast, South Central, Southwest). The Week 10 map showed most WaPo cases in the southern half of the city, and this checks whether that holds in the city's own feed after 2017.

### Reporting gap

For the full years 2015-2024, the city's public feed shows about half (51.5%) of the murders Dallas reported to the FBI. See `reports/dallas_city_vs_fbi.csv`. This is documented, not "fixed" by scaling.
