"""Ridgeline chart of listing price distribution by borough, split by room type."""

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

PRICE_CAP = 1000  # x-axis cap; a small number of listings above this are excluded


def load_data():
    df = pd.read_csv(CSV_PATH, usecols=[GROUP_COL, TYPE_COL, VALUE_COL])
    df = df.dropna(subset=[GROUP_COL, TYPE_COL, VALUE_COL])
    df = df[(df[VALUE_COL] > 0) & (df[VALUE_COL] <= PRICE_CAP)]
    return df


def main():
    df = load_data()

    # Rows are plotted bottom-to-top, so this is reversed from the desired
    # top-to-bottom reading order: Bronx > Brooklyn > Manhattan > Queens >
    # Staten Island, each block running Entire home/apt (top) to Shared
    # room (bottom).
    boroughs_bottom_up = list(reversed(GROUP_ORDER))
    types_bottom_up = list(reversed(TYPE_ORDER))
    rows = [(borough, room_type) for borough in boroughs_bottom_up for room_type in types_bottom_up]
    n = len(rows)
    block_size = len(TYPE_ORDER)

    x_grid = np.linspace(0, PRICE_CAP, 500)

    fig, ax = plt.subplots(figsize=(9, 10))

    row_height = 1.0
    overlap = 1.5

    for i, (borough, room_type) in enumerate(rows):
        values = df.loc[(df[GROUP_COL] == borough) & (df[TYPE_COL] == room_type), VALUE_COL]
        baseline = i * row_height

        if values.nunique() > 1:
            kde = gaussian_kde(values)
            density = kde(x_grid)
            density = density / density.max()
            y = baseline + density * row_height * overlap
        else:
            y = np.full_like(x_grid, baseline)

        ax.fill_between(x_grid, baseline, y, color=TYPE_COLORS[room_type], alpha=0.85, zorder=n - i)
        ax.plot(x_grid, y, color="black", linewidth=0.7, zorder=n - i)

    # one y-tick per borough, placed at the middle row of its 3-row block
    tick_positions = [
        (block_start + block_size / 2 - 0.5) * row_height for block_start in range(0, n, block_size)
    ]
    ax.set_yticks(tick_positions)
    ax.set_yticklabels(boroughs_bottom_up)

    # faint separators between borough blocks
    for block_start in range(block_size, n, block_size):
        ax.axhline(block_start * row_height, color="lightgray", linewidth=0.8, zorder=0)

    ax.set_xlabel("Price")
    ax.set_ylabel("Borough")
    ax.set_xlim(0, PRICE_CAP)
    ax.set_ylim(0, (n - 1) * row_height + row_height * overlap)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", color="lightgray", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=TYPE_COLORS[t], edgecolor="black") for t in TYPE_ORDER]
    ax.legend(handles, TYPE_ORDER, loc="upper right", frameon=False)

    ax.set_title("Listing Price Distribution by Borough and Room Type", fontsize=13, fontweight="bold")

    fig.tight_layout()
    fig.savefig(SCRIPT_DIR / "ridgeline-type.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
