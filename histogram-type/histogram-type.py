"""Faceted histograms of listing price by borough, split by room type.

One panel per neighbourhood group; within each panel, overlapping histograms
for Entire home/apt, Private room, and Shared room so both the borough effect
and the room-type effect are visible at once.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR.parent / "AB_NYC_2019.csv"
GROUP_COL = "neighbourhood_group"
TYPE_COL = "room_type"
VALUE_COL = "price"

GROUP_ORDER = ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"]
TYPE_ORDER = ["Entire home/apt", "Private room", "Shared room"]

TYPE_COLORS = {
    "Entire home/apt": "#E76F51",
    "Private room": "#2A9D8F",
    "Shared room": "#264653",
}

PRICE_CAP = 500  # x-axis cap; a small number of listings above this are excluded
BIN_WIDTH = 25


def load_data():
    df = pd.read_csv(CSV_PATH, usecols=[GROUP_COL, TYPE_COL, VALUE_COL])
    df = df.dropna(subset=[GROUP_COL, TYPE_COL, VALUE_COL])
    df = df[df[VALUE_COL] > 0]
    return df


def main():
    df = load_data()

    n_total = len(df)
    n_shown = len(df[df[VALUE_COL] <= PRICE_CAP])
    n_hidden = n_total - n_shown

    bins = list(range(0, PRICE_CAP + BIN_WIDTH, BIN_WIDTH))

    n = len(GROUP_ORDER)
    ncols = 3
    nrows = -(-n // ncols)  # ceil

    fig, axes = plt.subplots(nrows, ncols, figsize=(4.5 * ncols, 3.4 * nrows), sharex=True, sharey=True)
    axes = axes.flatten()

    for ax, group in zip(axes, GROUP_ORDER):
        for room_type in TYPE_ORDER:
            values = df.loc[(df[GROUP_COL] == group) & (df[TYPE_COL] == room_type), VALUE_COL]
            values = values[values <= PRICE_CAP]

            ax.hist(
                values,
                bins=bins,
                color=TYPE_COLORS[room_type],
                alpha=0.55,
                label=room_type,
                histtype="stepfilled",
                linewidth=1.2,
                edgecolor=TYPE_COLORS[room_type],
            )

        ax.set_title(group, fontsize=11, fontweight="bold")
        ax.set_xlim(0, PRICE_CAP)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", color="lightgray", linewidth=0.5, zorder=0)
        ax.set_axisbelow(True)

    for ax in axes[n:]:
        ax.set_visible(False)

    for ax in axes[:n]:
        if ax.get_subplotspec().is_last_row():
            ax.set_xlabel(VALUE_COL)
        if ax.get_subplotspec().is_first_col():
            ax.set_ylabel("listings")

    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=TYPE_COLORS[t], alpha=0.55, edgecolor=TYPE_COLORS[t]) for t in TYPE_ORDER]
    fig.legend(handles, TYPE_ORDER, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.02), frameon=False)

    fig.suptitle("Listing price by borough and room type", fontsize=14, fontweight="bold")
    fig.text(
        0.5,
        0.01 - 0.03,
        f"Price capped at ${PRICE_CAP}; {n_hidden:,} listings above this ({n_hidden / n_total:.1%} of total) are not shown.",
        ha="center",
        fontsize=9,
        color="gray",
    )

    fig.tight_layout(rect=(0, 0.08, 1, 0.94))
    fig.savefig(SCRIPT_DIR / "histogram-type.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
