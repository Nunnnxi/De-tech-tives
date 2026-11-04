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

## Rebuild the reports

Run from the repo root. `data/` is gitignored, so `get_data` downloads it again.

```
python -m src.get_data
python -m src.series
python -m src.charts
python -m src.casemap
```

## Sources

- Murder Accountability Project, UCR homicide and clearance data (UCR65_25), murderdata.org, accessed 2026-11-04.
- The Washington Post, Unsolved Homicide Database, github.com/washingtonpost/data-homicides, 2018. CC BY-NC-SA 4.0.

See `reports/SOURCES.md` for which output uses which source.
