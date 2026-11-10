import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


TRAILS_METRIC = "outputs/trail_metrics.geojson"
TOP_GAIN_OUTPUT = "outputs/top10_gain.png"
LENGTH_GAIN_OUTPUT = "outputs/length_vs_gain.png"
LENGTH_CUTOFF = 0.1
BINS = [0, 251, 501, 801, float("inf")]
LABELS = ["Easy", "Moderate", "Difficult", "Very Challenging"]
COLORS = {
    "Easy": "green",
    "Moderate": "blue",
    "Difficult": "purple",
    "Very Challenging": "red",
    "Unknown": "gray",
}


def load_metrics():
    trails = gpd.read_file(TRAILS_METRIC)
    trails = trails[trails["length_mi"] >= LENGTH_CUTOFF].copy()
    trails["difficulty"] = pd.cut(
        trails["gain_per_mi"],
        bins=BINS,
        labels=LABELS,
        right=False,
    )
    trails["difficulty"] = trails["difficulty"].cat.add_categories("Unknown").fillna(
        "Unknown"
    )
    return trails


def make_top_gain_chart(trails):
    top_gain = trails.nlargest(10, "gain_ft").sort_values("gain_ft")
    labels = [
        f"{name} ({length:.2f} mi)"
        for name, length in zip(top_gain["TRAILNAME"], top_gain["length_mi"])
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(labels, top_gain["gain_ft"], color="steelblue")
    ax.bar_label(bars, fmt="%.0f ft", padding=4)
    ax.set_xlabel("Total elevation gain (feet)")
    ax.set_title("Top 10 Trail Segments by Total Elevation Gain")
    ax.set_xlim(right=top_gain["gain_ft"].max() * 1.15)
    fig.tight_layout()
    fig.savefig(TOP_GAIN_OUTPUT, dpi=150)
    plt.close(fig)


def make_length_gain_chart(trails):
    fig, ax = plt.subplots(figsize=(9, 6))
    for difficulty, group in trails.groupby("difficulty", observed=False):
        ax.scatter(
            group["length_mi"],
            group["gain_ft"],
            label=difficulty,
            color=COLORS[str(difficulty)],
            alpha=0.75,
            edgecolors="white",
            linewidths=0.4,
        )
    ax.set_xscale("log")
    ax.set_xlabel("Segment length (miles, log scale)")
    ax.set_ylabel("Total elevation gain (feet)")
    ax.set_title("Trail Segment Length vs. Total Elevation Gain")
    ax.legend(title="Difficulty")
    fig.tight_layout()
    fig.savefig(LENGTH_GAIN_OUTPUT, dpi=150)
    plt.close(fig)


def main():
    trails = load_metrics()
    print(f"Loaded {len(trails)} segments after the {LENGTH_CUTOFF}-mile filter.")
    make_top_gain_chart(trails)
    make_length_gain_chart(trails)
    print(f"Wrote {TOP_GAIN_OUTPUT}")
    print(f"Wrote {LENGTH_GAIN_OUTPUT}")


if __name__ == "__main__":
    main()