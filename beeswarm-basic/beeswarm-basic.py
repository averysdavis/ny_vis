"""Beeswarm plot of listing price by borough (unsorted, fixed category order)."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

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

PRICE_CAP = 500  # y-axis cap; a small number of listings above this are excluded
SAMPLE_PER_GROUP = 300  # a true beeswarm can't legibly place tens of thousands of points
RANDOM_STATE = 0


def load_data():
    df = pd.read_csv(CSV_PATH)
    df = df[[GROUP_COL, VALUE_COL]].dropna()
    df = df[(df[VALUE_COL] > 0) & (df[VALUE_COL] <= PRICE_CAP)]
    return df


def main():
    df = load_data()

    sampled = pd.concat(
        df[df[GROUP_COL] == group].sample(
            min((df[GROUP_COL] == group).sum(), SAMPLE_PER_GROUP), random_state=RANDOM_STATE
        )
        for group in GROUP_ORDER
    )

    fig, ax = plt.subplots(figsize=(9, 6))

    sns.swarmplot(
        data=sampled,
        x=GROUP_COL,
        y=VALUE_COL,
        order=GROUP_ORDER,  # fixed category order, not sorted by price/count
        hue=GROUP_COL,
        hue_order=GROUP_ORDER,
        palette=GROUP_COLORS,
        size=3,
        edgecolor="black",
        linewidth=0.3,
        legend=False,
        ax=ax,
    )

    ax.set_xlabel("Borough")
    ax.set_ylabel("Price")
    ax.set_ylim(0, PRICE_CAP)
    ax.set_title("Listing Price by Borough", fontsize=13, fontweight="bold")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="lightgray", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

    fig.text(
        0.5,
        0.01,
        f"y-axis capped at ${PRICE_CAP}; each borough shows a random sample of up to {SAMPLE_PER_GROUP} listings.",
        ha="center",
        fontsize=9,
        color="gray",
    )

    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(SCRIPT_DIR / "beeswarm-basic.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
