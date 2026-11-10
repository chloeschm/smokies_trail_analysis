"""Download USGS 3DEP elevation for the trail extent and save it in EPSG:5070.

Run from the project root with the project environment (needs py3dep and internet):
    python src/download_dem.py

Writes data/smokies_dem.tif, the path the pipeline reads. It overwrites any
existing file at that path, so keep a copy first if you already have one.
"""
import geopandas as gpd
import py3dep
import rioxarray  # noqa: F401  (registers the .rio accessor)

TRAILS_PATH = 'data/trails.geojson'
OUT_PATH = 'data/smokies_dem.tif'
REQUEST_CRS = 'EPSG:4326'
RESOLUTION_M = 10  # requested from 3DEP; output is reprojected below
PAD_DEG = 0.01
PROJECTED_CRS = 'EPSG:5070'


def trail_bbox(path=TRAILS_PATH, pad=PAD_DEG):
    # bounding box of all trails in lon/lat, padded by a small margin
    minx, miny, maxx, maxy = gpd.read_file(path).total_bounds
    return (minx - pad, miny - pad, maxx + pad, maxy + pad)


def main():
    bbox = trail_bbox()
    print('bbox (lon/lat):', [round(v, 4) for v in bbox])
    dem = py3dep.get_dem(bbox, resolution=RESOLUTION_M, crs=REQUEST_CRS)
    print('downloaded:', dem.shape, dem.rio.crs)
    dem = dem.rio.reproject(PROJECTED_CRS)
    print('reprojected:', dem.shape, dem.rio.crs, dem.rio.resolution())
    dem.rio.to_raster(OUT_PATH)
    print('saved', OUT_PATH)


if __name__ == '__main__':
    main()
