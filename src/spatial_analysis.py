import numpy as np
import pandas as pd
import shapely
import xarray as xr
import rioxarray

FT_PER_M = 3.28084  # feet per meter
DEM_PATH = "data/smokies_dem.tif"
SAMPLE_SPACING = 30  # meters
SMOOTH_WINDOW = 31  # meters

def load_dem(path=DEM_PATH):
    # Load the DEM as a xarray DataArray
    return rioxarray.open_rasterio(path, masked=True).squeeze()  # remove the band dimension

def sample_profile(dem, geom):
    # swample the DEM along a geometry
    pts = np.asarray(shapely.segmentize(geom, SAMPLE_SPACING).coords)
    xs = xr.DataArray(pts[:, 0], dims='pt')
    ys = xr.DataArray(pts[:, 1], dims='pt')
    return dem.interp(x=xs, y=ys, method='linear').values.astype(float)


def gain_ft(elev, window=SMOOTH_WINDOW):
    # calculate the total gain in feet for a given elevation profile
    smoothed = pd.Series(elev).rolling(window, center=True, min_periods=1).median().to_numpy()
    d = np.diff(smoothed)
    return d[d > 0].sum() * FT_PER_M


def segment_gain(dem, geom):
    # calculate the total gain in feet for a given geometry
    parts = geom.geoms if geom.geom_type == 'MultiLineString' else [geom]
    return sum(gain_ft(sample_profile(dem, p)) for p in parts)
