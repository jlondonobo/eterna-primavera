import pandas as pd
import streamlit as st
from shapely import wkt

from transformers.trim_outliers import trim_outliers

COLS_OF_INTERES = [
    "id",
    "area",
    "offer",
    "property_type",
    "price_m2",
    "is_new",
    "price",
    "rooms.name",
    "stratum.name",
    "baths.name",
    "locations.location_point",
    "locations.cities",
    "age.name",
    "categories",
]


def parse_prices(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: This should be part of the data pipeline, not part of the app.
    """Parse prices as numeric and convert to millions."""
    return df.assign(
        price=lambda df: trim_outliers(pd.to_numeric(df["price"])),
        price_mm=lambda df: df["price"] / 1000000,
        price_m2=lambda df: trim_outliers(pd.to_numeric(df["price_m2"])),
        price_m2_mm=lambda df: df["price_m2"] / 1000000,
    )


@st.cache_data
def load_listings():
    """Returns listings data."""
    listings = pd.read_parquet(
        "eterna-primavera/aux_data/listings_2023-04-08.parquet", columns=COLS_OF_INTERES
    )

    listings["geometry"] = listings["locations.location_point"].apply(wkt.loads)
    listings["lat"] = listings["geometry"].apply(lambda p: p.y)
    listings["lon"] = listings["geometry"].apply(lambda p: p.x)
    listings["lat"] = listings["lat"].where(listings["lat"].between(4, 11), pd.NA)
    listings["lon"] = listings["lon"].where(listings["lon"].between(-76, -73), pd.NA)
    listings["area"] = pd.to_numeric(listings["area"])

    listings = listings.pipe(parse_prices)
    listings = listings.drop_duplicates(subset=["id"])
    return listings
