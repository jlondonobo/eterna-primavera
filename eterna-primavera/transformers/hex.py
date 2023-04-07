import geopandas as gpd
import h3
import pandas as pd
from shapely import Polygon


def polygon_from_h3(h3_id):
    """Returns a shapely Polygon from a H3 ID."""
    if h3.h3_is_valid(h3_id):
        return Polygon(h3.h3_to_geo_boundary(h3_id, geo_json=True))


def ploygons_from_h3(h3_series: pd.Series) -> gpd.GeoSeries:
    """Retruns a GeoSeries of shapely Polygons from a H3 Series."""
    borders = h3_series.apply(polygon_from_h3)
    return gpd.GeoSeries(borders)


def latlon_to_h3(data: pd.DataFrame, lat: str, lon: str, h3_level: int) -> pd.Series:
    "Returns a series of H3 IDs from lat/lon columns."
    return data.apply(lambda x: h3.geo_to_h3(x[lat], x[lon], h3_level), axis=1)