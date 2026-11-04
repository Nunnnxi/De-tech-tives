"""Draws the Dallas clearance trend chart from our week 9 series.

Run from the repo root after series: python -m src.charts
Writes reports/clearance_trend.png
"""
import pandas as pd
import matplotlib.pyplot as plt

SERIES_PATH = "reports/dallas_series.csv"
OUTPUT_PATH = "reports/clearance_trend.png"

FIRST_YEAR = 1965
LAST_YEAR = 2025
PARTIAL_YEAR = 2025  # still being reported, so it gets its own marker
FLAGGED_YEAR = 2017  # our #1 suspicious year from week 9
LINE_COLOR = "#196B24"


def main() -> None:
    s = pd.read_csv(SERIES_PATH)
    s["pct"] = s["clearance"] * 100

    # Reindex to every year so a missing year would become NaN and break the
    # line. There are no gaps right now, but the chart shouldn't hide one later.
    full = s.set_index("year").reindex(range(FIRST_YEAR, LAST_YEAR + 1))

    fig, ax = plt.subplots(figsize=(11, 5.5))

    # Full years only here, so the partial year doesn't look like a normal point.
    complete = full.copy()
    complete.loc[PARTIAL_YEAR, "pct"] = None
    ax.plot(complete.index, complete["pct"], color=LINE_COLOR,
            linewidth=2, marker="o", markersize=4)

    # Dashed line and hollow marker for the partial year.
    last_two = full.loc[PARTIAL_YEAR - 1:PARTIAL_YEAR, "pct"]
    ax.plot(last_two.index, last_two, color=LINE_COLOR, linewidth=2, linestyle="--")
    partial_pct = full.loc[PARTIAL_YEAR, "pct"]
    ax.plot(PARTIAL_YEAR, partial_pct, color=LINE_COLOR, marker="o", markersize=8,
            markerfacecolor="white", markeredgewidth=2)
    ax.annotate(f"{PARTIAL_YEAR}: {partial_pct:.0f}%\npartial year",
                xy=(PARTIAL_YEAR, partial_pct), xytext=(PARTIAL_YEAR - 2, 22),
                ha="center", arrowprops=dict(arrowstyle="->", color="#555555"))

    # Always 0 to 100. A tighter axis would make small dips look like collapses.
    ax.set_ylim(0, 100)
    ax.set_xlim(FIRST_YEAR - 1, LAST_YEAR + 2)
    ax.set_xlabel("Year")
    # The label says whose definition this is so it survives a screenshot.
    ax.set_ylabel("Homicide clearance (%), FBI definition\n"
                  "(arrest or exceptional means)\n"
                  "Source: FBI UCR via Murder Accountability Project")
    ax.set_title("Dallas Police Department homicide clearance rate, 1965–2025")
    ax.grid(alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)

    # Pull the values from the data so the note can't go stale.
    flagged_pct = full.loc[FLAGGED_YEAR, "pct"]
    next_pct = full.loc[FLAGGED_YEAR + 1, "pct"]
    ax.annotate(f"{FLAGGED_YEAR}: {flagged_pct:.0f}%, then "
                f"{FLAGGED_YEAR + 1}: {next_pct:.0f}%\nreporting change?",
                xy=(FLAGGED_YEAR, flagged_pct),
                xytext=(FLAGGED_YEAR - 3, flagged_pct + 11), ha="center",
                arrowprops=dict(arrowstyle="->", color="#555555"))

    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=150)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
