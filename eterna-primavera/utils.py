from typing import Literal

import pandas as pd
import streamlit as st
from cities import City
from loaders.load_cities import load_cities

CITIES = load_cities()


DENSITY_INHABITANTS_PER_KM2 = {
    "05001": 6376,
    "05088": 3688,
    "05360": 13122,
    "05266": 2904,
    "05129": 589,
    "05631": 5489,
    "05212": 1112,
    "05380": 2044,
    "05308": 662,
    "05079": 252,
    "": 3347,
}

TIME_TO_CENTER = {
    "05001": 0,
    "05088": 70,
    "05360": 30,
    "05266": 25,
    "05129": 50,
    "05631": 35,
    "05212": 80,
    "05380": 40,
    "05308": 90,
    "05079": 110,
    "": 0,
}


def get_density(city: City) -> int:
    """Return density of inhabitants per km2 for a city."""
    return DENSITY_INHABITANTS_PER_KM2[city]


def get_time_to_center(city: City) -> int:
    """Return time in minutes to get to the city center."""
    return TIME_TO_CENTER[city]
    

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


@st.cache_data
def filter_listings(
    listings: pd.DataFrame,
    city: City,
    offer: Literal["sell", "rent"],
    property_type: Literal["apartment", "studio", "house", "country-house", "farm"],
    rooms: list[str],
    bathrooms: list[str],
    stratum: list[str],
) -> pd.DataFrame:
    """Return a filtered dataframe with listings."""
    df = listings[
        (listings["city_code"] == city)
        & (listings["offer"] == offer)
        & (listings["property_type"] == property_type)
        & (listings["rooms"].isin(rooms))
        & (listings["baths"].isin(bathrooms))
        & (listings["stratum"].isin(stratum))
    ]
    return df
