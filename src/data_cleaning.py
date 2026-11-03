import geopandas as gpd

TRAILS_PATH = "data/trails.geojson"
PROJECTED_CRS = "EPSG:5070"
METERS_PER_MILE = 1609.34

def load_trails(path=TRAILS_PATH):
    return gpd.read_file(path).to_crs(PROJECTED_CRS)

def add_length_mi(trails):
    trails = trails.copy()
    trails["length_mi"] = trails.length / METERS_PER_MILE
    return trails

