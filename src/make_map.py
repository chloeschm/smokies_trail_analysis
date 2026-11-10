import pandas as pd
import geopandas as gpd
import folium

TRAILS_METRIC = "outputs/trail_metrics.geojson"
LENGTH_CUTOFF = 0.1  # miles
BINS = [0, 251, 501, 801, float("inf")]
LABELS = ["Easy", "Moderate", "Difficult", "Very Challenging"]
COLORS = {
    "Easy": "green",
    "Moderate": "blue",
    "Difficult": "purple",
    "Very Challenging": "red",
    "Unknown": "gray",
}

trails = gpd.read_file(TRAILS_METRIC)
print(f"Loaded {len(trails)} trail segments from {TRAILS_METRIC}")

if (trails["length_mi"] < LENGTH_CUTOFF).any():
    filtered_count = len(trails[trails["length_mi"] < LENGTH_CUTOFF])
    trails = trails[trails["length_mi"] >= LENGTH_CUTOFF]
    print(f"Filtered out {filtered_count} segments under {LENGTH_CUTOFF} miles.")
    print(f"Remaining {len(trails)} trail segments.")

trails["difficulty"] = pd.cut(
    trails["gain_per_mi"],
    bins=BINS,
    labels=LABELS,
    right=False
)

if trails["difficulty"].isnull().any():
    print("Warning: Some segments have missing gain_per_mi values. Assigning 'Unknown' difficulty.")
    trails["difficulty"] = trails["difficulty"].cat.add_categories("Unknown").fillna("Unknown")


smokies_center = [35.6118, -83.4895]  # approximate center of the GSMNP
m = folium.Map(location=smokies_center, zoom_start=11, tiles="OpenStreetMap")


def style_trail(feature):
    difficulty = feature["properties"].get("difficulty", "Unknown")
    return {
        "color": COLORS.get(difficulty, COLORS["Unknown"]),
        "weight": 5,
        "opacity": 0.7,
    }

map_data = trails[
    ["TRAILNAME", "length_mi", "gain_ft", "gain_per_mi", "difficulty", "geometry", "location"]
].copy()

folium.GeoJson(
    map_data.to_json(),
    name="Trail segments",
    style_function=style_trail,
    highlight_function=lambda feature: {"weight": 7, "opacity": 1},
    popup=folium.GeoJsonPopup(
        fields=[
            "TRAILNAME",
            "length_mi",
            "gain_ft",
            "gain_per_mi",
            "difficulty",
            "location",
        ],
        aliases=[
            "Trail",
            "Length (miles)",
            "Gain (feet)",
            "Gain per mile (feet)",
            "Difficulty",
            "Location",
        ],
        localize=True,
    ),
).add_to(m)
    
legend_html = '''
    <div style="position: fixed; bottom: 10px; right: 10px; background: white; padding: 10px; border: 1px solid #ccc; z-index: 1000;">
        <h4>Trail Difficulty</h4>
'''

for i, (bin, label) in enumerate(zip(BINS, LABELS)):
    color = COLORS[label]
    range_label = (
        f"{BINS[i]} to {BINS[i + 1] - 1} ft/mi"
        if i + 1 < len(BINS)
        else f"{BINS[i]}+ ft/mi"
    )
    legend_html += f'<p><span style="color: {color};">&#9679;</span> {label} - {range_label}</p>'
legend_html += '</div>'

m.get_root().html.add_child(folium.Element(legend_html))

# GitHub Pages serves docs/ as the site, so the map is written there as index.html
m.save("docs/index.html")