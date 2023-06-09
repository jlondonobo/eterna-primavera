import os
from typing import Literal, Union

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
    geodata = geodata.assign(
        is_selected=lambda df: id_is_selected(df[id_col], selection),
        population_2023=lambda df: df["population_2023"].apply(lambda x: f"{x:,}"),
    )

    fig = px.choropleth_mapbox(
        geodata,
        geojson=geojson_data,
        locations=id_col,
        color="is_selected",
        color_discrete_map={True: selected_color, False: default_color},
        mapbox_style=None,
        zoom=zoom,
        center=center,
        hover_data=hover_data,
    )

    fig.update_layout(
        mapbox_style="light",
        mapbox_accesstoken=os.environ["MAPBOX_TOKEN"],
        margin=dict(l=0, r=0, t=0, b=0),
        uirevision="Don't change",
        showlegend=False,
    )
    return fig


def h3_choropleth_from_latlon(
    type: Literal["count", "price"],
    data: pd.DataFrame,
    lat: str,
    lon: str,
    h3_level: int,
    hover_data: Union[dict, None] = None,
    zoom: int = 9,
    center: dict = {"lat": 6.240833, "lon": -75.530553},
):
    """Return choropleth map of H3 hexagons from lat/lon columns."""
    value_var = "counter" if type == "count" else "price_m2"
    agg_fun = {"counter": "count", "price_m2": "mean"}

    hex_statistic = (
        data.assign(
            h3=lambda df: latlon_to_h3(df, lat, lon, h3_level),
            counter=1,
        )
        .groupby("h3", as_index=False)
        .agg(agg_fun)
        .assign(h3_geometry=lambda df: ploygons_from_h3(df["h3"]).scale(0.85, 0.85))
        .dropna()
    )

    geojson_obj = gdf_to_json(hex_statistic, "h3", "h3_geometry", value_var)
    if type == "count":
        min = hex_statistic["counter"].quantile(0.1)
        max = hex_statistic["counter"].quantile(0.99)
    elif type == "price":
        min = hex_statistic["price_m2"].quantile(0.1)
        max = hex_statistic["price_m2"].quantile(0.99)
        
    range_color = [min, max]

    fig = px.choropleth_mapbox(
        hex_statistic,
        geojson=geojson_obj,
        locations="h3",
        color=value_var,
        mapbox_style="carto-positron",
        zoom=zoom,
        center=center,
        hover_data=hover_data,
        labels={"price_m2": "Precio m²", "counter": "No. Propiedades"},
        opacity=0.7,
        color_continuous_scale="Sunsetdark",
        range_color=range_color,
    )

    fig.update_layout(
        mapbox_style="light",
        mapbox_accesstoken=os.environ["MAPBOX_TOKEN"],
        margin=dict(l=0, r=0, t=0, b=0),
        uirevision="Don't change",
        showlegend=False,
        height=700,
        
    )
    fig.update_traces(marker_line_width=0)
    return fig


def plot_donut(s: pd.Series) -> go.Figure:
    """Return a donut chart from a Series."""
    mapper = {
        "rooms": "No. Habitaciones",
        "baths": "No. Baños",
        "stratum": "Estrato",
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
        margin=dict(l=0, r=0, t=70, b=0),
        showlegend=False,
        title=dict(
            text=mapper[s.name],
            x=0.5,
            xanchor="center",
        ),
        height=300,
    )
    return fig
