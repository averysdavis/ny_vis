"""Ridgeline chart of listing price distribution by neighbourhood group."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR.parent / "AB_NYC_2019 - 2 Col.csv"
GROUP_COL = "neighbourhood_group"
VALUE_COL = "price"

# Plotted bottom-to-top, so this is reversed from the desired top-to-bottom
# reading order: Bronx, Brooklyn, Manhattan, Queens, Staten Island.
GROUP_ORDER = ["Staten Island", "Queens", "Manhattan", "Brooklyn", "Bronx"]

GROUP_COLORS = {
    "Bronx": "#FFD166",
    "Brooklyn": "#F4A261",
    "Manhattan": "#E76F51",
    "Queens": "#2A9D8F",
    "Staten Island": "#264653",
}

PRICE_CAP = 20000  # drop extreme outliers so the KDE isn't dominated by them


def load_data():
    df = pd.read_csv(CSV_PATH)
    df = df[[GROUP_COL, VALUE_COL]].dropna()
    df = df[(df[VALUE_COL] > 0) & (df[VALUE_COL] <= PRICE_CAP)]
    return df


def main():
    df = load_data()

    groups = GROUP_ORDER
    n = len(groups)

    x_grid = np.linspace(0, df[VALUE_COL].max(), 500)

    fig, ax = plt.subplots(figsize=(8, 6))

    overlap = 1.6  # vertical spacing multiplier; >1 makes ridges overlap
    row_height = 1.0

    for i, group in enumerate(groups):
        values = df.loc[df[GROUP_COL] == group, VALUE_COL]
        kde = gaussian_kde(values)
        density = kde(x_grid)
        density = density / density.max()  # normalize each ridge to same peak height

        baseline = i * row_height
        y = baseline + density * row_height * overlap

        ax.fill_between(x_grid, baseline, y, color=GROUP_COLORS[group], alpha=0.9, zorder=n - i)
        ax.plot(x_grid, y, color="black", linewidth=0.8, zorder=n - i)

    ax.set_yticks([i * row_height for i in range(n)])
    ax.set_yticklabels(groups)
    ax.set_xlabel("Price")
    ax.set_ylabel("Borough")
    ax.set_xlim(0, df[VALUE_COL].max())
    ax.set_ylim(0, (n - 1) * row_height + row_height * overlap)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", color="lightgray", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig(SCRIPT_DIR / "ridgeline-basic.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
