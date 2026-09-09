"""Raincloud plots of listing price by borough, split by room type.

One panel per borough; within each panel, three stacked raincloud rows (one
per room type). Each row combines a half-violin "cloud", a thin boxplot, and
a jittered "rain" of raw points, all colored by room type.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

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
SAMPLE_PER_ROW = 80  # the "rain" layer samples for legibility, the cloud and box use all data
RANDOM_STATE = 0

ROW_HEIGHT = 1.0
CLOUD_FRAC = 0.5
BOX_Y_FRAC = 0.40
BOX_WIDTH_FRAC = 0.12
RAIN_Y_LOW_FRAC = 0.04
RAIN_Y_HIGH_FRAC = 0.32


def load_data():
    df = pd.read_csv(CSV_PATH, usecols=[GROUP_COL, TYPE_COL, VALUE_COL])
    df = df.dropna(subset=[GROUP_COL, TYPE_COL, VALUE_COL])
    df = df[(df[VALUE_COL] > 0) & (df[VALUE_COL] <= PRICE_CAP)]
    return df


def draw_raincloud_row(ax, values, i, color, x_grid, rng):
    if values.nunique() > 1:
        kde = gaussian_kde(values)
        density = kde(x_grid)
        density = density / density.max() * (ROW_HEIGHT * CLOUD_FRAC)
    else:
        density = np.zeros_like(x_grid)

    cloud_baseline = i + ROW_HEIGHT
    ax.fill_between(
        x_grid, cloud_baseline - density, cloud_baseline, color=color, alpha=0.85, edgecolor="black", linewidth=0.5, zorder=2
    )

    box = ax.boxplot(
        values,
        positions=[i + BOX_Y_FRAC],
        orientation="horizontal",
        widths=BOX_WIDTH_FRAC,
        patch_artist=True,
        manage_ticks=False,
        flierprops={"markersize": 1.5, "markerfacecolor": "gray", "markeredgecolor": "none", "alpha": 0.3},
    )
    for patch in box["boxes"]:
        patch.set_facecolor(color)
        patch.set_alpha(0.95)
        patch.set_edgecolor("black")
    for median in box["medians"]:
        median.set_color("black")
        median.set_linewidth(1.0)

    sample = values.sample(min(len(values), SAMPLE_PER_ROW), random_state=RANDOM_STATE)
    y_jitter = i + rng.uniform(RAIN_Y_LOW_FRAC, RAIN_Y_HIGH_FRAC, size=len(sample))
    ax.scatter(sample, y_jitter, s=5, color=color, alpha=0.55, edgecolor="none", zorder=1)


def main():
    df = load_data()
    rng = np.random.default_rng(RANDOM_STATE)

    n_rows = len(TYPE_ORDER)
    x_grid = np.linspace(0, PRICE_CAP, 400)

    n = len(GROUP_ORDER)
    ncols = 3
    nrows = -(-n // ncols)

    fig, axes = plt.subplots(nrows, ncols, figsize=(5.2 * ncols, 4.6 * nrows), sharex=True)
    axes = axes.flatten()

    for ax, borough in zip(axes, GROUP_ORDER):
        for i, room_type in enumerate(TYPE_ORDER):
            values = df.loc[(df[GROUP_COL] == borough) & (df[TYPE_COL] == room_type), VALUE_COL]
            draw_raincloud_row(ax, values, i, TYPE_COLORS[room_type], x_grid, rng)

        ax.set_yticks([i + 0.5 for i in range(n_rows)])
        ax.set_yticklabels(TYPE_ORDER, fontsize=8)
        ax.set_ylim(n_rows, 0)
        ax.set_xlim(0, PRICE_CAP)
        ax.set_title(borough, fontsize=11, fontweight="bold")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.grid(axis="x", color="lightgray", linewidth=0.5, zorder=0)
        ax.set_axisbelow(True)

    for ax in axes[n:]:
        ax.set_visible(False)

    for ax in axes[:n]:
        if ax.get_subplotspec().is_last_row():
            ax.set_xlabel("Price")

    fig.suptitle("Listing Price by Borough and Room Type", fontsize=14, fontweight="bold")
    fig.text(
        0.5,
        0.01,
        f"x-axis capped at ${PRICE_CAP}; each row's 'rain' samples up to {SAMPLE_PER_ROW} points (cloud and box use all data).",
        ha="center",
        fontsize=9,
        color="gray",
    )

    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    fig.savefig(SCRIPT_DIR / "raincloud-type.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
