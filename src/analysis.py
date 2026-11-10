import shapely

from data_cleaning import load_trails, add_length_mi
from spatial_analysis import load_dem, segment_gain


def build_trail_metrics():
    # build a GeoDataFrame with trail metrics including length, gain, and gain per mile
    trails = add_length_mi(load_trails())
    dem = load_dem()
    trails['gain_ft'] = trails.geometry.apply(lambda g: segment_gain(dem, g))
    trails['gain_per_mi'] = trails['gain_ft'] / trails['length_mi']
    return trails


if __name__ == '__main__':
    trails = build_trail_metrics()
    print(trails.iloc[0][['TRAILNAME', 'length_mi', 'gain_ft']])
    # web maps need lat/lon, so export in EPSG:4326
    out = trails.to_crs('EPSG:4326')
    # a point that lies on each trail, as "lat, lon" text for the popup
    out['location'] = out.geometry.apply(
        lambda g: f"{g.representative_point().y:.5f}, {g.representative_point().x:.5f}"
    )
    # round coordinates to about 1 m so the file is smaller
    out['geometry'] = out.geometry.apply(lambda g: shapely.set_precision(g, 1e-5))
    out.to_file('outputs/trail_metrics.geojson', driver='GeoJSON')
    print(f'wrote {len(trails)} segments to outputs/trail_metrics.geojson')