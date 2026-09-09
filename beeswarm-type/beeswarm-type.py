"""Beeswarm plot of listing price by borough, split by room type."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

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

PRICE_CAP = 500  # y-axis cap; a small number of listings above this are excluded
SAMPLE_PER_SUBGROUP = 120  # a true beeswarm can't legibly place tens of thousands of points
RANDOM_STATE = 0


def load_data():
    df = pd.read_csv(CSV_PATH, usecols=[GROUP_COL, TYPE_COL, VALUE_COL])
    df = df.dropna(subset=[GROUP_COL, TYPE_COL, VALUE_COL])
    df = df[(df[VALUE_COL] > 0) & (df[VALUE_COL] <= PRICE_CAP)]
    return df


def main():
    df = load_data()

    sampled = pd.concat(
        df[(df[GROUP_COL] == group) & (df[TYPE_COL] == room_type)].sample(
            min(((df[GROUP_COL] == group) & (df[TYPE_COL] == room_type)).sum(), SAMPLE_PER_SUBGROUP),
            random_state=RANDOM_STATE,
        )
        for group in GROUP_ORDER
        for room_type in TYPE_ORDER
    )

    fig, ax = plt.subplots(figsize=(11, 6))

    sns.swarmplot(
        data=sampled,
        x=GROUP_COL,
        y=VALUE_COL,
        order=GROUP_ORDER,
        hue=TYPE_COL,
        hue_order=TYPE_ORDER,
        palette=TYPE_COLORS,
        dodge=True,
        size=2.8,
        edgecolor="black",
        linewidth=0.3,
        ax=ax,
    )

    ax.set_xlabel("Borough")
    ax.set_ylabel("Price")
    ax.set_ylim(0, PRICE_CAP)
    ax.set_title("Listing Price by Borough and Room Type", fontsize=13, fontweight="bold")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="lightgray", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

    ax.legend(title=None, loc="upper right", frameon=False)

    fig.text(
        0.5,
        0.01,
        f"y-axis capped at ${PRICE_CAP}; each borough/room-type combination shows a random sample of up to {SAMPLE_PER_SUBGROUP} listings.",
        ha="center",
        fontsize=9,
        color="gray",
    )

    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(SCRIPT_DIR / "beeswarm-type.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
