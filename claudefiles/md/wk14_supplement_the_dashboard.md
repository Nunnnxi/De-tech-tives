# Week 14 Supplement — The Dashboard: Streamlit on localhost

Companion to deck 14. Lab: Operation Localhost.

**Data this week:** no new downloads. The app reads what is already in `reports/` and `data/case.db`. Nothing is rewritten; everything is imported.

**Install before class** (inside the venv, then freeze):
```bash
pip install streamlit
pip freeze > requirements.txt
streamlit hello          # a demo app opens in your browser. If it does, you are ready.
```

**Before class, as a squad:** pick your app's name. It goes on a public URL next week.

---

## 1. What the app reads

| Tab | Reads | Produced in |
|---|---|---|
| Series | `reports/dallas_series.csv` | week 9 |
| Map | `reports/dallas_map.html` | week 10 |
| What-If | `reports/dallas_series.csv` | week 9 |
| Model | `reports/feature_importances.csv`, `reports/model_notes.md` | week 13 |
| Methodology (stretch) | `reports/factor_writeup.md`, your README | weeks 9–13 |

If any of these is missing on a squad laptop, run the script that produces it. Do not copy files between laptops.

`data/case.db` is gitignored, so on a fresh clone it will not exist. The app must either call `src.fetch_city` on first run (cached by `@st.cache_data`) or fall back gracefully to the reports it can find. Decide which and document it.

## 2. `src/app.py` skeleton

```python
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(page_title="The Dallas Clearance Project", layout="wide")
st.title("The Dallas Clearance Project")
st.caption("Squad N · ITSS/OPRE 3312 · FBI UCR via Murder Accountability Project; Washington Post; Dallas OpenData")

@st.cache_data
def load_series() -> pd.DataFrame:
    return pd.read_csv("reports/dallas_series.csv")

s = load_series()
tab_series, tab_map, tab_whatif, tab_model = st.tabs(["Series", "Map", "What-If", "Model"])

with tab_series:
    lo, hi = int(s.year.min()), int(s.year.max())
    years = st.slider("Years", lo, hi, (lo, hi))
    view = s[s.year.between(*years)].copy()
    view["clearance_pct"] = view.clearance * 100
    st.line_chart(view, x="year", y="clearance_pct", y_label="Clearance (%) — FBI definition")
    st.markdown("**Suspicious year:** 2017 — clearance jumps to 80% in one year, then falls to 40% in 2018. "
                "Consistent with a reporting change, not a policing change. See methodology.")

with tab_map:
    html = Path("reports/dallas_map.html").read_text(encoding="utf-8")
    components.html(html, height=600, scrolling=False)
    st.caption("1,567 Dallas homicides, 2007–2017. Orange = open / no arrest. Source: Washington Post.")

with tab_whatif:
    st.header("What if Dallas had held a different clearance rate?")
    base = st.slider("Counterfactual clearance %", 30, 90, 62)
    cf = s.copy()
    cf["cf_cleared"] = cf.reported * base / 100
    extra = (cf.cf_cleared - cf.cleared).clip(lower=0)
    st.metric("Additional cases that would have been cleared, 1965–2025", f"{int(extra.sum()):,}")
    st.caption("A model, not a promise. Assumes the clearance rate is a dial and nothing else changes. "
               "It says what outcomes would have been if rates had matched, not that anyone tried less hard.")

with tab_model:
    imp = pd.read_csv("reports/feature_importances.csv", index_col=0).squeeze()
    st.bar_chart(imp.head(10))
    st.markdown(Path("reports/model_notes.md").read_text(encoding="utf-8"))
```

Run: `streamlit run src/app.py`. Browser opens at http://localhost:8501.

## 3. Importing your own library

Anything that needs a computation, not just a file, is imported:

```python
from src.queries import top_beats       # week 11
from src.series import build_series     # week 9, if you wrapped it in a function
```

For this to work when Streamlit runs the file, the repo root must be on the path. Run from the repo root (`streamlit run src/app.py`), and add to the top of `app.py` if needed:

```python
import sys; sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
```

Zero copy-pasted logic. The reviewer checks.

## 4. The what-if caption is not optional

Every slider position is a claim about hundreds of families. Word the caption as a squad. It must say: this is a model; it assumes the rate is a dial; it describes outcomes, not effort. The week-1 framing stands: "if outcomes had matched," never "if police had tried harder."

## 5. Review: the reviewer runs the app

```bash
git checkout feature/wk14-app
pip install -r requirements.txt
streamlit run src/app.py
```

The reviewer clicks every tab, moves every slider, and confirms the What-If caption is present before approving. If `requirements.txt` does not reproduce the environment, the PR is not ready.

## 6. Results checklist

- [ ] `streamlit run src/app.py` launches clean on all four laptops
- [ ] Four tabs: Series (slider + chart + annotation), Map (embedded folium), What-If (slider + metric + honesty caption), Model (importances + three sentences)
- [ ] Everything imported from `src/` or read from `reports/`
- [ ] `requirements.txt` updated with streamlit; reviewer reproduced the environment
- [ ] App name chosen and in the `st.title`
- [ ] Merged via reviewed PR

## 7. Stretch

- `st.download_button("Download the series", s.to_csv(index=False), "dallas_series.csv")`
- A Methodology tab rendering your README's methodology section and the two clearance definitions
- `st.metric` row: cumulative unsolved (`(reported - cleared).sum()`), worst year, best year

## 8. Common errors

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: src` | Run from repo root, or add the `sys.path` line. |
| Map tab blank | `reports/dallas_map.html` missing on this laptop. Run `python -m src.casemap`. |
| App reruns slowly | Wrap every file read and every DB query in `@st.cache_data`. |
| Works for author, not reviewer | Freeze harder. `pip freeze > requirements.txt`, commit. |
