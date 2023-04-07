import geopandas as gpd
import pandas as pd
import streamlit as st


@st.cache_data
def load_cities() -> gpd.GeoDataFrame:
    """Returns a GeoDataFrame with the geometries of the cities in the Valle Aburra."""
    population = (
        pd.read_json("eterna-primavera/aux_data/population.json", orient="index")
        [0]
    )
    geometries = gpd.read_parquet("eterna-primavera/aux_data/valle_aburra.parquet")
    return (
        geometries
        .assign(population=lambda df: df["MPIO_CDPMP"].map(population))
    )