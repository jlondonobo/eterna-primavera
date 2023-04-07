import geopandas as gpd
import streamlit as st


@st.cache_data
def load_cities() -> gpd.GeoDataFrame:
    """Returns a GeoDataFrame with the geometries of the cities in the Valle Aburra."""
    return gpd.read_parquet("eterna-primavera/aux_data/valle_aburra.parquet")
