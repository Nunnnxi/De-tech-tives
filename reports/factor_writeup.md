# Factor writeup: De-tech-tives

## Hypothesis (as locked at standup)

> We hypothesize that the Dallas-Fort Worth unemployment rate is associated with Dallas homicide clearance, in the **negative** direction.

The reasoning: when unemployment rises, city revenue falls and the police budget is squeezed (fewer detectives, less overtime, slower lab work). Hard times may also bring more robbery- and drug-related killings, which are harder to solve. Because city budgets are set from the previous year's revenue, we also ran the pre-registered lag-1 variant: does **last year's** unemployment predict this year's clearance?

## Data

- **Clearance:** `reports/dallas_series.csv` (FBI UCR via the Murder Accountability Project, Dallas Police Department, ORI `TXDPD00`). Clearance = cleared / reported, where "cleared" means arrest **or** exceptional clearance. Years used: 1990-2025.
- **Factor:** unemployment rate, Dallas-Fort Worth-Arlington metro area, annual, not seasonally adjusted (BLS Local Area Unemployment Statistics), FRED series `LAUMT481910000000003A`, https://fred.stlouisfed.org/series/LAUMT481910000000003A, downloaded 2026-11-18 by `src/get_fred.py`. One row per year, 1990-2025.
- **After merge:** 36 rows (1990-2025). The lag-1 model has 35 (1991-2025), because there is no 1989 rate in the series.
- The merged dataset is in `reports/factor_merged.csv` and the numbers below are in `reports/factor_results.csv`, both written by `src/factor.py`.
- 2025 is a partial FBI year (still being reported). We kept it because the pre-registered design uses every overlapping year.

## Result

| Model | coef | p | R² | n |
|---|---|---|---|---|
| `clearance ~ unemployment` (primary) | **+0.0197** | 0.100 | 0.078 | 36 (1990-2025) |
| `clearance ~ unemployment_lag1` | **+0.0239** | 0.048 | 0.113 | 35 (1991-2025) |

How to read it: clearance is on a 0-1 scale, so a coef of +0.0197 means each extra percentage point of unemployment goes with about **2 percentage points higher** clearance.

- **The direction is the opposite of what we predicted.** Both slopes are positive.
- **The primary model is not statistically significant** (p = 0.10), and unemployment accounts for about 8% of the year-to-year variation in clearance.
- **The lag-1 model just crosses p < 0.05** (p = 0.048, 95% CI 0.000 to 0.048, R² = 0.11). This is weaker evidence than it looks, for the reasons in the confounders section: the lower end of the interval touches zero, and the Durbin-Watson statistic of 1.52 shows the yearly errors are correlated, which makes plain OLS p-values too optimistic.

## Two named confounders

### 1. The long downward trend in clearance (time)

Clearance fell steadily for reasons that have nothing to do with the economy (the long-run decline seen across US cities, changes in case mix, witness cooperation, forensic workloads). Over 1990-2025 clearance is strongly correlated with the calendar year (r = -0.65), and DFW unemployment drifted slightly lower over the same period (r = -0.19).

| Period | Mean clearance | Mean unemployment |
|---|---|---|
| 1990s | 70.7% | 4.9% |
| 2000s | 63.9% | 5.4% |
| 2010s | 59.4% | 5.2% |
| 2020-25 | 51.0% | 4.6% |

The lowest-clearance years (2018: 39.9%, 2022-2024: about 46-48%) happen to fall in a low-unemployment stretch, and the recession years 2009-2011 (unemployment 7.8-8.2%) came while clearance was still about 65%. That alone can produce a positive slope with no causal link. Time is a confounder: it moves both variables. We did not add a time-trend control, because that would be a third, unregistered model. It is the first thing a follow-up should test.

### 2. Murder volume (caseload per detective)

The number of murders each year changes how much time detectives can give each case, and it also moves with economic conditions and the crime waves behind them. Dallas averaged 309 murders a year in the 1990s versus 152 in the 2010s. If recessions shift how many murders happen or what kind they are, unemployment could look related to clearance only through caseload. In our data murders and unemployment are only weakly related (r = 0.13), so this channel is probably small here, but our design cannot rule it out.

**Also worth noting:** 2017 (79.6%, unemployment 3.7%) and 2018 (39.9%, 3.6%) are the outliers flagged in Week 9. With only 36 points, two extreme years can pull the line on their own.

## Verdict

Over 1990-2025, the Dallas-Fort Worth unemployment rate is **not detectably associated with** Dallas homicide clearance in the negative direction we pre-registered. Our hypothesis is not supported. The same-year relationship is weak, positive and not statistically significant (coef = +0.020, p = 0.10, R² = 0.08, n = 36). The lag-1 variant is also positive and borderline (coef = +0.024, p = 0.048, R² = 0.11, n = 35). We do not treat it as a finding, because the shared downward time trend and correlated yearly errors can produce a result like this by themselves.

We do not claim causation, because this is one variable observed over 36 years, with no control for the long-run decline in clearance, caseload or case mix. The economy explains little of why Dallas solves fewer murders than it used to. The causes are more likely inside the long-run trend that both of our confounders point to.
