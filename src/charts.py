"""Draw the Dallas homicide clearance trend chart for a newsroom (Week 10).

What it does:
    1. Reads reports/dallas_series.csv (built by src/series.py).
    2. Saves reports/clearance_trend.png: the full 1965-2025 series on a
       0-100% axis, source in the axis label, 2025 marked as a partial
       year, and our Week 9 suspicious years (2017 and 2018) annotated.
    3. Stretch: saves reports/clearance_trend_rolling.png, the same chart
       plus a 5-year rolling average. It is a separate file so the
       required chart stays uncluttered.

"Cleared" here is the FBI UCR definition: arrest OR exceptional clearance.

The script only saves files; it never opens a window (no plt.show()).

How to run (from the repo root, after src.get_data and src.series):
    .venv/bin/python -m src.charts
"""

from pathlib import Path

# Use the non-interactive "Agg" backend so matplotlib draws straight to a
# file and never tries to open a window (works on servers and in CI too).
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (must come after use("Agg"))
import pandas as pd  # noqa: E402

REPORTS_DIR = Path("reports")
SERIES_PATH = REPORTS_DIR / "dallas_series.csv"
TREND_PATH = REPORTS_DIR / "clearance_trend.png"
ROLLING_PATH = REPORTS_DIR / "clearance_trend_rolling.png"

# The full span of the source archive. We always plot all of it so the
# chart can't be accused of cherry-picking a flattering window.
FIRST_YEAR = 1965
LAST_YEAR = 2025
PARTIAL_YEAR = 2025  # still being reported, so incomplete

LINE_COLOR = "#196B24"     # dark green for the main series
PARTIAL_COLOR = "#C0392B"  # red so the partial year stands out
ROLLING_COLOR = "#8FBF94"  # light green for the rolling average

TITLE = "Dallas Police Department homicide clearance rate, 1965-2025"
Y_LABEL = (
    "Homicide clearance (%)\n"
    "Source: FBI UCR via Murder Accountability Project\n"
    "(FBI definition: arrest or exceptional clearance)"
)


def load_series():
    """Read the series and return it indexed by every year 1965-2025.

    Adds pct = clearance * 100. Reindexing to the full range turns any
    missing year into NaN. That matters because plt.plot draws a straight
    line across gaps between the points it has, which would hide missing
    data. With NaN in the gap, matplotlib breaks the line instead.
    Prints how many years were missing.
    """
    df = pd.read_csv(SERIES_PATH, index_col="year")
    df["pct"] = df["clearance"] * 100

    # reindex adds a NaN row for any year not in the CSV.
    s = df.reindex(range(FIRST_YEAR, LAST_YEAR + 1))
    missing = s["pct"].isna().sum()
    print(f"years missing from the series: {missing}")
    return s


def draw_base(ax, s):
    """Draw the parts every version of the chart shares, on the given axes.

    That means the line, the partial-year marker, the 0-100 axis, the
    labels and the grid.
    """
    # Main series. Any NaN years from the reindex show up as breaks.
    ax.plot(s.index, s["pct"], marker="o", markersize=4, lw=2,
            color=LINE_COLOR, label="Clearance rate (yearly)")

    # Mark the partial year with a bigger, hollow red marker on top of the
    # normal one, instead of dropping it. Readers see it but know not to
    # compare it directly with full years.
    p = s.loc[PARTIAL_YEAR, "pct"]
    ax.plot([PARTIAL_YEAR], [p], marker="o", markersize=11,
            markerfacecolor="none", markeredgecolor=PARTIAL_COLOR, mew=2,
            linestyle="none", label=f"{PARTIAL_YEAR} partial year")
    # Text label points down at the hollow marker from above.
    ax.annotate(f"{PARTIAL_YEAR} partial year\n({p:.1f}%, still being reported)",
                xy=(PARTIAL_YEAR, p), xytext=(PARTIAL_YEAR - 0.5, 88),
                ha="right", fontsize=9, color=PARTIAL_COLOR,
                arrowprops=dict(arrowstyle="->", color=PARTIAL_COLOR))

    # Honesty: the y-axis starts at 0 so drops aren't exaggerated, and ends
    # at 100 because a rate can't normally go above 100%.
    ax.set_ylim(0, 100)
    ax.set_xlim(FIRST_YEAR - 1, LAST_YEAR + 1)
    ax.set_ylabel(Y_LABEL, fontsize=9)
    ax.set_xlabel("Year")
    ax.set_title(TITLE, fontsize=13, weight="bold")
    ax.grid(alpha=0.3)


def annotate_suspicious(ax, s):
    """Annotate 2017 and 2018, our top suspicious years from Week 9.

    All numbers are read from the series, not typed in. The text boxes sit
    in empty parts of the chart (2017 above the line, 2018 below it) so
    they don't cover the line or each other.
    """
    p2016, p2017, p2018 = (s.loc[y, "pct"] for y in (2016, 2017, 2018))

    # Is 2018 really the lowest full year? Check, so the label stays honest
    # if the data changes.
    lowest_year = int(s["pct"].idxmin())
    n_years = int(s["pct"].notna().sum())
    low_text = f"lowest of all {n_years} years" if lowest_year == 2018 else "sharp drop"

    # 2017: jump up. Text placed above and to the left, in the empty space
    # above the 1990s-2000s part of the line.
    ax.annotate(f"2017: jumps {p2016:.1f}% → {p2017:.1f}%\n(possible backlog cleared in bulk)",
                xy=(2017, p2017), xytext=(1996, 93),
                ha="center", fontsize=9,
                bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9),
                arrowprops=dict(arrowstyle="->", color="black",
                                connectionstyle="arc3,rad=-0.2"))

    # 2018: drop down. Text placed below the line on the left, where the
    # chart is empty (all years are well above 40%).
    ax.annotate(f"2018: {low_text}, {p2018:.1f}%\n"
                f"({p2017 - p2018:.1f}-pt drop right after 2017)",
                xy=(2018, p2018), xytext=(2003, 15),
                ha="center", fontsize=9,
                bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9),
                arrowprops=dict(arrowstyle="->", color="black",
                                connectionstyle="arc3,rad=0.2"))


def save(fig, path):
    """Tidy the layout, save the figure as a PNG and close it to free memory."""
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {path}")


def trend_chart(s):
    """Required chart: full series, annotated, saved to reports/clearance_trend.png."""
    fig, ax = plt.subplots(figsize=(11, 4.5))
    draw_base(ax, s)
    annotate_suspicious(ax, s)
    ax.legend(loc="lower left", fontsize=8)
    save(fig, TREND_PATH)


def rolling_chart(s):
    """Stretch: same chart plus a centered 5-year rolling average.

    center=True means each point averages that year with the 2 years before
    and the 2 after, so the smooth line isn't shifted later in time. The
    first and last 2 years have no full window, so they are left blank
    (NaN) instead of being averaged over fewer years. Note the last
    average shown (2023) includes the partial year 2025.
    """
    s = s.copy()
    s["rolling"] = s["pct"].rolling(5, center=True).mean()

    fig, ax = plt.subplots(figsize=(11, 4.5))
    # Draw the rolling line first and lighter, so it sits behind the yearly
    # line and doesn't take over.
    ax.plot(s.index, s["rolling"], lw=4, color=ROLLING_COLOR, alpha=0.9,
            label="5-year rolling average (centered)")
    draw_base(ax, s)
    annotate_suspicious(ax, s)
    ax.legend(loc="lower left", fontsize=8)
    save(fig, ROLLING_PATH)


def main():
    """Build both PNGs from reports/dallas_series.csv."""
    s = load_series()
    trend_chart(s)
    rolling_chart(s)


# Only run when executed directly (python -m src.charts), not on import.
if __name__ == "__main__":
    main()
