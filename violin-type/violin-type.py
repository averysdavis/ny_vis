"""Grouped violin plots of listing price by borough, clustered by room type."""

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

PRICE_CAP = 500  # y-axis cap; a small number of listings above this are excluded from view
VIOLIN_WIDTH = 0.25


def load_data():
    df = pd.read_csv(CSV_PATH, usecols=[GROUP_COL, TYPE_COL, VALUE_COL])
    df = df.dropna(subset=[GROUP_COL, TYPE_COL, VALUE_COL])
    df = df[df[VALUE_COL] > 0]
    return df


def main():
    df_all = load_data()

    n_total = len(df_all)
    n_hidden = len(df_all[df_all[VALUE_COL] > PRICE_CAP])

    df = df_all[df_all[VALUE_COL] <= PRICE_CAP]

    fig, ax = plt.subplots(figsize=(11, 6))

    offsets = [(-1) * VIOLIN_WIDTH, 0, VIOLIN_WIDTH]

    for room_type, offset in zip(TYPE_ORDER, offsets):
        data = [
            df.loc[(df[GROUP_COL] == group) & (df[TYPE_COL] == room_type), VALUE_COL]
            for group in GROUP_ORDER
        ]
        positions = [i + offset for i in range(len(GROUP_ORDER))]

        parts = ax.violinplot(
            data, positions=positions, widths=VIOLIN_WIDTH * 0.9, showmedians=True, showextrema=True
        )

        for body in parts["bodies"]:
            body.set_facecolor(TYPE_COLORS[room_type])
            body.set_edgecolor("black")
            body.set_alpha(0.9)

        for key in ("cbars", "cmins", "cmaxes", "cmedians"):
            parts[key].set_color("black")
            parts[key].set_linewidth(1.1 if key == "cmedians" else 0.6)

    ax.set_xticks(range(len(GROUP_ORDER)))
    ax.set_xticklabels(GROUP_ORDER)
    ax.set_xlim(-0.5, len(GROUP_ORDER) - 0.5)
    ax.set_ylim(0, PRICE_CAP)

    ax.set_xlabel("Borough")
    ax.set_ylabel("Price")
    ax.set_title("Listing Price by Borough and Room Type", fontsize=13, fontweight="bold")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="lightgray", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=TYPE_COLORS[t], edgecolor="black") for t in TYPE_ORDER]
    ax.legend(handles, TYPE_ORDER, loc="upper right", frameon=False)

    fig.text(
        0.5,
        0.01,
        f"y-axis capped at ${PRICE_CAP}; {n_hidden:,} listings above this ({n_hidden / n_total:.1%} of total) are not shown.",
        ha="center",
        fontsize=9,
        color="gray",
    )

    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(SCRIPT_DIR / "violin-type.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
