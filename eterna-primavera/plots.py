import os
from typing import Union

import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from transformers.gdf_to_json import gdf_to_json
from transformers.hex import latlon_to_h3, ploygons_from_h3
from utils import id_is_selected

load_dotenv()


def plot_highlighted_choropleth(
    geodata: gpd.GeoDataFrame,
    selection: str,
    id_col: str,
    geometry_col: str = "geometry",
    selected_color: str = "#EAB9A5",
    default_color: str = "#F4F4F4",
    hover_data: Union[dict, None] = None,
    zoom: int = 9,
    center: dict = {"lat": 6.240833, "lon": -75.530553},
) -> go.Figure:
    """Return choropleth map with highlighted selection."""
    geojson_data = gdf_to_json(geodata, id_col, geometry_col)
    is_selected = id_is_selected(geodata[id_col], selection)

    fig = px.choropleth_mapbox(
        geodata,
        geojson=geojson_data,
        locations=id_col,
        color=is_selected,
        color_discrete_map={True: selected_color, False: default_color},
        mapbox_style="carto-positron",
        zoom=zoom,
        center=center,
        hover_data=hover_data,
    )

    fig.update_layout(
        mapbox_style=os.environ["MAPBOX_STYLE"],
        mapbox_accesstoken=os.environ["MAPBOX_TOKEN"],
        margin=dict(l=0, r=0, t=0, b=0),
        # this option forces zoom to stay the same when data is updated
        uirevision="Don't change",
        showlegend=False,
    )
    return fig


def h3_choropleth_from_latlon(
    data: pd.DataFrame,
    lat: str,
    lon: str,
    h3_level: int,
    hover_data: Union[dict, None] = None,
    zoom: int = 9,
    center: dict = {"lat": 6.240833, "lon": -75.530553},
):
    """Return choropleth map of H3 hexagons from lat/lon columns."""

    hex_count = (
        data
        .assign(h3=lambda df: latlon_to_h3(df, lat, lon, h3_level))
        .groupby("h3", as_index=False)
        .size()
        .assign(h3_geometry=lambda df: ploygons_from_h3(df["h3"]))
        .dropna()
    )

    geojson_obj = gdf_to_json(hex_count, "h3", "h3_geometry", "size")

    fig = px.choropleth_mapbox(
        hex_count,
        geojson=geojson_obj,
        locations="h3",
        color="size",
        mapbox_style="carto-positron",
        zoom=zoom,
        center=center,
        hover_data=hover_data
    )

    fig.update_layout(
        mapbox_style=os.environ["MAPBOX_STYLE"],
        mapbox_accesstoken=os.environ["MAPBOX_TOKEN"],
        margin=dict(l=0, r=0, t=0, b=0),
        uirevision="Don't change",
        showlegend=False,
    )
    return fig


def plot_donut(s: pd.Series) -> go.Figure:
    """Return a donut chart from a Series."""
    mapper = {
        "rooms.name": "No. Habitaciones",
        "baths.name": "No. Baños",
        "stratum.name": "Estrato",
    }
    fig = go.Figure(
        data=[
            go.Pie(
                labels=s.index,
                values=s.values,
                hole=0.5,
                textinfo="label+percent",
                sort=False,
                direction="clockwise",
            )
        ]
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False,
        title=dict(
            text=mapper[s.name],
            x=0.5,
            xanchor="center",
        ),
        height=300,
    )
    return fig

