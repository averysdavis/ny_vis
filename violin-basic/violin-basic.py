"""Violin plots of listing price by borough."""

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

    # Feed the KDE only capped data -- otherwise the long tail out to the
    # true max (~$10,000) stretches the density so thin that everything
    # below $500 looks squashed flat.
    df_capped = df[df[VALUE_COL] <= PRICE_CAP]
    data = [df_capped.loc[df_capped[GROUP_COL] == group, VALUE_COL] for group in GROUP_ORDER]

    fig, ax = plt.subplots(figsize=(8, 6))

    parts = ax.violinplot(data, positions=range(len(GROUP_ORDER)), widths=0.8, showmedians=True, showextrema=True)

    for body, group in zip(parts["bodies"], GROUP_ORDER):
        body.set_facecolor(GROUP_COLORS[group])
        body.set_edgecolor("black")
        body.set_alpha(0.9)

    for key in ("cbars", "cmins", "cmaxes", "cmedians"):
        parts[key].set_color("black")
        parts[key].set_linewidth(1.2 if key == "cmedians" else 0.8)

    ax.set_xticks(range(len(GROUP_ORDER)))
    ax.set_xticklabels(GROUP_ORDER)
    ax.set_ylim(0, PRICE_CAP)

    ax.set_xlabel("Borough")
    ax.set_ylabel("Price")
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
    fig.savefig(SCRIPT_DIR / "violin-basic.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
