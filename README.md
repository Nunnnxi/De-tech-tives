# De-tech-tives

ITSS 3312 squad repo.

- `src/` - package code (`intake.py`, `models.py`, `patterns.py`)
- `tests/` - pytest tests, run `pytest` from the repo root
- `data/` - raw inputs
- `reports/` - outputs (CSVs, charts, maps)
- `claudefiles/` - course materials
  - `md/` - weekly supplements, data sources overview, build roadmap
  - `pptxs/` - weekly lecture decks

Each week, add the new supplement `.md` files to `claudefiles/md/` and the new decks to `claudefiles/pptxs/`.

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
