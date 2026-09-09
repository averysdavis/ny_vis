"""Raincloud plots of listing price by borough.

Each row combines three layers, all showing the same distribution:
  - the "cloud": a half-violin (KDE) density curve
  - a thin boxplot summarizing the quartiles
  - the "rain": a jittered sample of the raw points
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

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
SAMPLE_PER_GROUP = 200  # the "rain" layer samples for legibility, the cloud and box use all data
RANDOM_STATE = 0

ROW_HEIGHT = 1.0
CLOUD_FRAC = 0.5  # top half of each row is the density cloud
BOX_Y_FRAC = 0.40  # box center, as a fraction up from the row's bottom
BOX_WIDTH_FRAC = 0.12
RAIN_Y_LOW_FRAC = 0.04
RAIN_Y_HIGH_FRAC = 0.32


def load_data():
    df = pd.read_csv(CSV_PATH)
    df = df[[GROUP_COL, VALUE_COL]].dropna()
    df = df[(df[VALUE_COL] > 0) & (df[VALUE_COL] <= PRICE_CAP)]
    return df


def main():
    df = load_data()
    rng = np.random.default_rng(RANDOM_STATE)

    n = len(GROUP_ORDER)
    x_grid = np.linspace(0, PRICE_CAP, 400)

    fig, ax = plt.subplots(figsize=(9, 7))

    for i, group in enumerate(GROUP_ORDER):
        values = df.loc[df[GROUP_COL] == group, VALUE_COL]
        color = GROUP_COLORS[group]

        # The y-axis is reversed (Bronx-on-top), so a larger y renders lower
        # on screen. The cloud's flat edge sits at the bottom of the row
        # (y = i + ROW_HEIGHT) and the density pushes the other edge *up*
        # (smaller y) toward the box above it, giving a hill silhouette
        # rather than an inverted trough.
        kde = gaussian_kde(values)
        density = kde(x_grid)
        density = density / density.max() * (ROW_HEIGHT * CLOUD_FRAC)
        cloud_baseline = i + ROW_HEIGHT
        ax.fill_between(
            x_grid, cloud_baseline - density, cloud_baseline, color=color, alpha=0.85, edgecolor="black", linewidth=0.6, zorder=2
        )

        box = ax.boxplot(
            values,
            positions=[i + BOX_Y_FRAC],
            orientation="horizontal",
            widths=BOX_WIDTH_FRAC,
            patch_artist=True,
            manage_ticks=False,
            flierprops={"markersize": 2, "markerfacecolor": "gray", "markeredgecolor": "none", "alpha": 0.3},
        )
        for patch in box["boxes"]:
            patch.set_facecolor(color)
            patch.set_alpha(0.95)
            patch.set_edgecolor("black")
        for median in box["medians"]:
            median.set_color("black")

        sample = values.sample(min(len(values), SAMPLE_PER_GROUP), random_state=RANDOM_STATE)
        y_jitter = i + rng.uniform(RAIN_Y_LOW_FRAC, RAIN_Y_HIGH_FRAC, size=len(sample))
        ax.scatter(sample, y_jitter, s=6, color=color, alpha=0.5, edgecolor="none", zorder=1)

    ax.set_yticks([i + 0.5 for i in range(n)])
    ax.set_yticklabels(GROUP_ORDER)
    ax.set_ylim(n, 0)  # Bronx at top, without double-flipping via invert_yaxis
    ax.set_xlim(0, PRICE_CAP)

    ax.set_xlabel("Price")
    ax.set_ylabel("Borough")
    ax.set_title("Listing Price by Borough", fontsize=13, fontweight="bold")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", color="lightgray", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

    fig.text(
        0.5,
        0.01,
        f"x-axis capped at ${PRICE_CAP}; the 'rain' layer samples up to {SAMPLE_PER_GROUP} points per borough (cloud and box use all data).",
        ha="center",
        fontsize=9,
        color="gray",
    )

    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(SCRIPT_DIR / "raincloud-basic.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
