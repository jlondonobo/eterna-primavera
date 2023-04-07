
import geopandas as gpd
from geojson import Feature, FeatureCollection


def gdf_to_json(
    gdf: gpd.GeoDataFrame,
    id_col: str,
    geometry_col: str,
    value_col: str = "",
) -> FeatureCollection:
    """Return geojson from GeoDataFrame."""
    feature_sequence = []
    for _, row in gdf.iterrows():
        properties = {"value": row[value_col]} if value_col else None
        feature = Feature(
            geometry=row[geometry_col],
            id=row[id_col],
            properties=properties,
        )
        feature_sequence.append(feature)
    feat_collection = FeatureCollection(feature_sequence)
    return feat_collection
