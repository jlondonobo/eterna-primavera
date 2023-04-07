import os

import geopandas as gpd
import h3
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from geojson import Feature, FeatureCollection
from shapely import Polygon, wkt

load_dotenv()


def import_css(file_name: str) -> None:
    """Import a CSS file into the Streamlit app."""
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


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


def get_geojson_border(h3_id):
    if h3.h3_is_valid(h3_id):
        return Polygon(h3.h3_to_geo_boundary(h3_id, geo_json=True))


def get_h3_borders(h3_series: pd.Series) -> gpd.GeoSeries:
    borders = h3_series.apply(get_geojson_border)
    return gpd.GeoSeries(borders)


def gdf_to_json_with_value(
    gdf: gpd.GeoDataFrame,
    id_col: str,
    geometry_col: str,
    value_field: str,
) -> FeatureCollection:
    """Return geojson from GeoDataFrame."""
    list_features = []
    for _, row in gdf.iterrows():
        feature = Feature(
            geometry=row[geometry_col],
            id=row[id_col],
            properties={"value": row[value_field]},
        )
        list_features.append(feature)
    feat_collection = FeatureCollection(list_features)
    return feat_collection


def plot_h3_listings(df: pd.DataFrame, lat: str, lon: str, h3_level: int):
    df["h3"] = df.apply(lambda x: h3.geo_to_h3(x[lat], x[lon], h3_level), axis=1)

    count_hex = df.groupby("h3", as_index=False).size()
    count_hex["h3_geometry"] = get_h3_borders(count_hex["h3"])
    count_hex = count_hex.dropna()
    
    geojson_obj = gdf_to_json_with_value(count_hex, "h3", "h3_geometry", "size")

    fig = px.choropleth_mapbox(
        count_hex,
        geojson=geojson_obj,
        locations="h3",
        color="size",
        mapbox_style="carto-positron",
        zoom=10,
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
