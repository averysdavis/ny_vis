"""Faceted histograms of listing price by neighbourhood group (small multiples)."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR.parent / "AB_NYC_2019 - 2 Col.csv"
GROUP_COL = "neighbourhood_group"
VALUE_COL = "price"

GROUP_ORDER = ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"]

GROUP_COLORS = {
    "Bronx": "#FFD166",
    "Brooklyn": "#F4A261",
    "Manhattan": "#E76F51",
    "Queens": "#2A9D8F",
    "Staten Island": "#264653",
}

PRICE_CAP = 500  # x-axis cap; a small number of listings above this are excluded
BIN_WIDTH = 25


def load_data():
    df = pd.read_csv(CSV_PATH)
    df = df[[GROUP_COL, VALUE_COL]].dropna()
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

    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 3.2 * nrows), sharex=True, sharey=True)
    axes = axes.flatten()

    for ax, group in zip(axes, GROUP_ORDER):
        values = df.loc[df[GROUP_COL] == group, VALUE_COL]
        values = values[values <= PRICE_CAP]

        ax.hist(values, bins=bins, color=GROUP_COLORS[group], edgecolor="white", linewidth=0.5)
        ax.set_title(group, fontsize=11, fontweight="bold")
        ax.set_xlim(0, PRICE_CAP)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", color="lightgray", linewidth=0.5, zorder=0)
        ax.set_axisbelow(True)

    # hide any unused axes in the grid
    for ax in axes[n:]:
        ax.set_visible(False)

    for ax in axes[:n]:
        if ax.get_subplotspec().is_last_row():
            ax.set_xlabel("Price")
    for i, ax in enumerate(axes[:n]):
        if ax.get_subplotspec().is_first_col():
            ax.set_ylabel("listings")

    fig.suptitle("Distribution of Listing Price by Borough", fontsize=14, fontweight="bold")
    fig.text(
        0.5,
        0.01,
        f"Price capped at ${PRICE_CAP}; {n_hidden:,} listings above this ({n_hidden / n_total:.1%} of total) are not shown.",
        ha="center",
        fontsize=9,
        color="gray",
    )

    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(SCRIPT_DIR / "histogram-basic.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
