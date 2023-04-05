import os

import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from geojson import Feature, FeatureCollection

load_dotenv()


@st.cache_data
def load_geometries() -> gpd.GeoDataFrame:
    """Returns a GeoDataFrame with the geometries of the cities in the Valle Aburra."""
    return gpd.read_parquet("eterna-primavera/aux_data/valle_aburra.parquet")


def city_is_selected(gdf: gpd.GeoDataFrame, selected_city: str) -> pd.Series:
    """Returns a boolean series indicating whether a city is selected or not."""
    # If no city is selected (==''), return a series of False
    return gdf["MPIO_CDPMP"] == selected_city


def gdf_to_json(
    gdf: gpd.GeoDataFrame,
    id_col: str,
    geometry_col: str,
    # value_field: str,
) -> FeatureCollection:
    """Return geojson from GeoDataFrame."""
    list_features = []
    for _, row in gdf.iterrows():
        feature = Feature(
            geometry=row[geometry_col],
            id=row[id_col],
            # properties={"value": row[value_field]},
        )
        list_features.append(feature)
    feat_collection = FeatureCollection(list_features)
    return feat_collection


def plot_map_with_selection(
    selected_city: str,
):
    geometries = load_geometries()
    geojson_obj = gdf_to_json(geometries, "MPIO_CDPMP", "geometry")
    is_selected = city_is_selected(geometries, selected_city)

    fig = px.choropleth_mapbox(
        geometries,
        geojson=geojson_obj,
        locations="MPIO_CDPMP",
        color=is_selected,
        color_discrete_map={True: "#EAB9A5", False: "#F4F4F4"},
        mapbox_style="carto-positron",
        zoom=9,
        center={"lat": 6.240833, "lon": -75.530553},
        # TODO: Add extra info and show get_name() on hover
        # hover_data={
        #     "size": True,
        #     "h3": False
        # }
    )
    
    fig = fig.update_layout(
        mapbox_style=os.environ["MAPBOX_STYLE"],
        mapbox_accesstoken=os.environ["MAPBOX_TOKEN"],
        margin=dict(l=0, r=0, t=0, b=0),
        uirevision="Don't change",  # this option forces zoom to stay the same when data is updated),
        showlegend=False,
    )
    return fig
