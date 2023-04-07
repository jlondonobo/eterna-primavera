import pandas as pd
import streamlit as st
from cities import City


@st.cache_data
def load_cities() -> pd.DataFrame:
    """Returns a DataFrame with the population of the cities in the Valle Aburra."""
    all_cities = pd.read_parquet("eterna-primavera/aux_data/cities.parquet")
    current_cities = [c.value for c in City]
    return all_cities.query("MPIO in @current_cities")
