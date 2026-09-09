"""Basic boxplots of listing price by neighbourhood group."""

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

PRICE_CAP = 500  # y-axis cap; a small number of listings above this are excluded from view


def load_data():
    df = pd.read_csv(CSV_PATH)
    df = df[[GROUP_COL, VALUE_COL]].dropna()
    df = df[df[VALUE_COL] > 0]
    return df


def main():
    df = load_data()

    n_total = len(df)
    n_hidden = len(df[df[VALUE_COL] > PRICE_CAP])

    data = [df.loc[df[GROUP_COL] == group, VALUE_COL] for group in GROUP_ORDER]

    fig, ax = plt.subplots(figsize=(8, 6))

    box = ax.boxplot(
        data,
        tick_labels=GROUP_ORDER,
        patch_artist=True,
        widths=0.6,
        medianprops={"color": "black", "linewidth": 1.5},
        flierprops={"markersize": 3, "markerfacecolor": "gray", "markeredgecolor": "none", "alpha": 0.4},
    )

    for patch, group in zip(box["boxes"], GROUP_ORDER):
        patch.set_facecolor(GROUP_COLORS[group])
        patch.set_edgecolor("black")
        patch.set_alpha(0.9)

    ax.set_ylim(0, PRICE_CAP)
    ax.set_ylabel("Price")
    ax.set_xlabel("Borough")
    ax.set_title("Listing Price by Borough", fontsize=13, fontweight="bold")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="lightgray", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

    fig.text(
        0.5,
        0.01,
        f"y-axis capped at ${PRICE_CAP}; {n_hidden:,} listings above this ({n_hidden / n_total:.1%} of total) are not shown.",
        ha="center",
        fontsize=9,
        color="gray",
    )

    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(SCRIPT_DIR / "boxplot-basic.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
