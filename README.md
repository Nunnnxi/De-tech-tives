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
