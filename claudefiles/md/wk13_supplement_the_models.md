# Week 13 Supplement — The Models: scikit-learn and Cross-Examination

Companion to deck 13. Lab: Operation The Model + The Fight.

**Data this week:** no new downloads. Features come from `data/wapo_dallas.csv` (week 9) and/or `data/case.db` (week 11). Rebuild either with `python -m src.get_data` or `python -m src.fetch_city` if missing.

**Install before class** (inside the venv, then freeze):
```bash
pip install scikit-learn
pip freeze > requirements.txt
```

**Before class:** reread the factor writeup of the squad you will cross-examine (pairings 1↔3, 2↔4). Bring two attacks.

---

## 1. Build the feature table

The target is "unsolved." Pick one source and stick with it.

**Option A: WaPo file (recommended, cleaner target).** 1,567 cases, 2007–2017, disposition is explicit.

```python
import pandas as pd

w = pd.read_csv("data/wapo_dallas.csv")
w["date"] = pd.to_datetime(w.reported_date, format="%Y%m%d")
w["year"] = w.date.dt.year
w["month"] = w.date.dt.month
w["age"] = pd.to_numeric(w.victim_age, errors="coerce")        # "Unknown" -> NaN
w["unsolved"] = (w.disposition != "Closed by arrest").astype(int)

cases = w.dropna(subset=["age", "lat", "lon"])
X = pd.get_dummies(cases[["age", "year", "month", "lat", "lon", "victim_sex", "victim_race"]],
                   columns=["victim_sex", "victim_race"], drop_first=True)
y = cases["unsolved"]
print(X.shape, y.mean())      # how many rows survived, base rate of unsolved
```

Note what you lost: rows with unknown age are disproportionately unsolved. Say so in the notes.

**Option B: case.db.** 1,100-ish murders, 2014–present. Richer case attributes, murkier target.

```python
import sqlite3
con = sqlite3.connect("data/case.db")
c = pd.read_sql("""SELECT servyr, month1, premise, division, beat, victimtype,
                          status, ucr_disp, lat, lon FROM incidents""", con)
print(c.status.value_counts()); print(c.ucr_disp.value_counts())
```

Inspect `status` and `ucr_disp` first. Define `unsolved` from what the values actually say (e.g. `ucr_disp` containing `OPEN` or `SUSPENDED`). Write the exact rule in `model_notes.md`. Then one-hot `premise`, `division`, `victimtype`.

**Never** use `victim_first` or `victim_last` as a feature. They were dropped in `get_data.py` for a reason.

## 2. Three models, one honest table

```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=42)

models = {
    "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    "tree":     DecisionTreeClassifier(max_depth=4, random_state=42),
    "mlp":      make_pipeline(StandardScaler(),
                              MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=500, random_state=42)),
}
results = []
for name, m in models.items():
    m.fit(X_tr, y_tr)
    results.append({"model": name, "train": m.score(X_tr, y_tr), "test": m.score(X_te, y_te)})
print(pd.DataFrame(results).round(3))
print("baseline (always predict majority):", round(max(y_te.mean(), 1 - y_te.mean()), 3))
```

Quote **test** scores only. Always print the majority-class baseline next to them. A model at 0.58 when the baseline is 0.57 has learned almost nothing, and that is a legitimate finding.

## 3. Feature importances

```python
logit = models["logistic"].named_steps["logisticregression"]
coefs = pd.Series(logit.coef_[0], index=X.columns).sort_values()
print(coefs)

tree = models["tree"]
imp = pd.Series(tree.feature_importances_, index=X.columns).sort_values(ascending=False)
print(imp.head(10))
imp.to_csv("reports/feature_importances.csv")       # week 14's Model tab reads this
```

Logistic coefficients are standardized, so sign and magnitude are comparable across features. Positive = associated with unsolved.

## 4. `reports/model_notes.md` — three careful sentences

Template for each sentence: "[Feature] is associated with a [higher/lower] probability of a case remaining unsolved in the 2007–2017 Dallas data (test accuracy ____ vs baseline ____); this is consistent with / differs from the national pattern, and may reflect ____ rather than ____."

The literature says weapon and victim-offender relationship dominate nationally. WaPo's Dallas file does not carry either field. Your model cannot find what it was not given. Say that.

Then add: "The two strongest attacks received in cross-examination were: ____ and ____. Our responses: ____."

## 5. Cross-examination: the rules

8 minutes per pairing. 2 minutes they present their factor verdict. 4 minutes your squad attacks. 2 minutes they defend.

Legal attacks: unnamed confounders, reverse causation, case-mix drift, cherry-picked year windows, a verdict stronger than the model supports, a factor that is really a proxy for time.

Illegal attacks: style, typos, people.

Prepare in writing. Example: "Your factor is unemployment 1990–2024. Clearance fell 2007–2011 while unemployment rose, but detective headcount also fell in those years. How do you separate the two?"

## 6. Results checklist

- [ ] `src/predict.py` builds the feature table, splits 75/25 with `random_state=42`, trains three models
- [ ] Printed table: train and test score per model plus the majority baseline
- [ ] `reports/feature_importances.csv` written
- [ ] `reports/model_notes.md`: three sentences, non-causal language, the two attacks received and responses
- [ ] Reviewer re-ran `predict.py` and matched every quoted number
- [ ] Merged via reviewed PR

## 7. Common errors

| Symptom | Fix |
|---|---|
| `could not convert string to float` | A text column slipped into `X`. `pd.get_dummies` it or drop it. |
| MLP warns about convergence | Raise `max_iter` or accept it. Report the score as is. |
| Test score 0.99 | Target leaked into features (e.g. `status` in X when target came from `ucr_disp`). Remove it. |
| Different numbers on reviewer's machine | `random_state` missing somewhere, or `data/` differs. Rerun `get_data`. |
