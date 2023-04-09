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

TEMP_DISABLED_PROPERTY_TYPES = [
    "Casa Campestre",
    "Proyecto",
]


def parse_prices(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: This should be part of the data pipeline, not part of the app.
    """Parse prices as numeric and convert to millions."""
    return df.assign(
        price=lambda df: trim_outliers(pd.to_numeric(df["price"]), max=0.98),
        # price_mm=lambda df: df["price"] / 1000000,
        price_m2=lambda df: trim_outliers(pd.to_numeric(df["price_m2"]), max=0.98),
        # price_m2_mm=lambda df: df["price_m2"] / 1000000,
    )


def flatten_offer(s: pd.Series) -> pd.Series:
    return s.apply(lambda x: x[0]["name"])


def flatten_property_type(s: pd.Series) -> pd.Series:
    SIMPLE_PROPERTY_MAPPER = {
        "Apartamento": "Apartamento",
        "Casa": "Casa",
        "Apartaestudio": "Apartamento",
        "Casa Campestre": "Casa Campestre",
        "Finca": "Casa Campestre",
        "Proyecto": "Proyecto",
    }
    
    property_count = s.apply(lambda x: len(x))
    # There are some properties with more than one property type
    # this is might not be fully accurate
    return s.apply(lambda x: x[0]["name"]).map(SIMPLE_PROPERTY_MAPPER)


def group_if_above(s: pd.Series, threshold: int, group_name: str) -> pd.Series:
    numeric = pd.to_numeric(s, errors="coerce")
    return s.where(numeric < threshold, group_name)


def group_stratum(s: pd.Series):
    others = [
        "Campestre",
        "Estrato 0",
        "Estrato 1",
    ]
    return s.where(~s.isin(others), pd.NA)


def drop_poorly_inputed(listings: pd.DataFrame) -> pd.DataFrame:
    """Drop listings with poorly inputed data."""
    low_price = (listings["price"] < 30_000_000) & (listings["offer"] == "Venta")
    large_area = listings["area"] > 500

    return listings[~low_price & ~large_area]


def city_to_code(s: pd.Series) -> pd.Series:
    MAPPER = {
        "MEDELLÍN": "05001",
        "ENVIGADO": "05266",
        "SABANETA": "05631",
        "BELLO": "05088",
        "ITAGUÍ": "05360",
        "LA ESTRELLA": "05380",
        "COPACABANA": "05212",
        "CALDAS": "05129",
        "GIRARDOTA": "05308",
        "BARBOSA": "05079",
    }
    return s.str.upper().map(MAPPER)



@st.cache_data
def load_listings():
    """Returns listings data."""
    listings = pd.read_parquet(
        "eterna-primavera/aux_data/listings_2023-04-08.parquet", columns=COLS_OF_INTERES
    )
    listings = listings.reset_index(drop=True)
    listings["geometry"] = listings["locations.location_point"].apply(wkt.loads)
    listings["lat"] = listings["geometry"].apply(lambda p: p.y)
    listings["lon"] = listings["geometry"].apply(lambda p: p.x)
    listings["lat"] = listings["lat"].where(listings["lat"].between(4, 11), pd.NA)
    listings["lon"] = listings["lon"].where(listings["lon"].between(-76, -73), pd.NA)
    listings["area"] = pd.to_numeric(listings["area"])

    listings = listings.pipe(parse_prices)
    listings = listings.drop_duplicates(subset=["id"])
    listings = (
        listings
        .assign(
            offer=lambda df: flatten_offer(df["offer"]),
            property_type=lambda df: flatten_property_type(df["property_type"]),
            rooms=lambda df: group_if_above(df["rooms.name"], 5, "5+"),
            baths=lambda df: group_if_above(df["baths.name"], 4, "4+"),
            stratum=lambda df: group_stratum(df["stratum.name"]),
            city=lambda df: flatten_offer(df["locations.cities"]),
            city_code=lambda df: city_to_code(df["city"]),
        )
        .query("~property_type.isin(@TEMP_DISABLED_PROPERTY_TYPES)")
        .pipe(drop_poorly_inputed)
    )
    return listings
