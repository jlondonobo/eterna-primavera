from typing import Literal

import pandas as pd
import streamlit as st
from cities import City
from loaders.load_cities import load_cities

CITIES = load_cities()


def import_css(file_name: str) -> None:
    """Import a CSS file into the Streamlit app."""
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def id_is_selected(s: pd.Series, selected_id: str) -> pd.Series:
    """Returns a boolean series indicating if a polygon is selected."""
    return s == selected_id


def get_name(city: City) -> str:
    """Retrun canonical name of the city."""
    return CITIES.at[city, "NOMBRE"]


def get_inhabitants(city: City, year: Literal[2023, 2035]) -> int:
    """Return estimated number of inhabitants for a city in a given year."""    
    column = "population_2023" if year == 2023 else "population_2035"
    return CITIES.at[city, column]


def filter_listings(
    listings: pd.DataFrame,
    city: City,
    offer: Literal["sell", "rent"],
    property_type: Literal["apartment", "studio", "house", "country-house", "farm"],
    rooms: list[int],
    bathrooms: list[int],
    stratum: list[str],
) -> pd.DataFrame:
    """Return a filtered dataframe with listings."""
    df = listings[
        (listings["city"] == city)
        & (listings["offer"] == offer)
        & (listings["property_type"] == property_type)
        & (listings["rooms"].isin(rooms))
        & (listings["baths"].isin(bathrooms))
        & (listings["stratum"].isin(stratum))
    ]
    return df
