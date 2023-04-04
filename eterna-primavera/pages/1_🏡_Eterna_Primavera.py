import constants
import language
import pandas as pd
import plotly.express as px
import streamlit as st
from cities import City, get_city_tag, get_fr_tag, get_name
from real_estate.finca_raiz import main, search
from shapely import wkt


@st.cache_data
def fetch_properties(city: City, offers: str, property_type: str) -> pd.DataFrame:
    city_tags = [get_city_tag(city), get_fr_tag(city)]

    df = sc.search(offer=offers, property_type=property_type, cities=city_tags)

    df["geometry"] = df["locations.location_point"].apply(wkt.loads)
    df["lat"] = df["geometry"].apply(lambda p: p.y)
    df["lon"] = df["geometry"].apply(lambda p: p.x)
    df["lat"] = df["lat"].where(df["lat"].between(4, 11), pd.NA)
    df["lon"] = df["lon"].where(df["lon"].between(-76, -73), pd.NA)

    df["price_m2"] = pd.to_numeric(df["price_m2"])
    min = df["price_m2"].quantile(0.05)
    max = df["price_m2"].quantile(0.95)
    df["price_m2"] = df["price_m2"].where(
        (df["price_m2"] > min) & (df["price_m2"] < max), pd.NA
    )
    return df


@st.cache_data
def fetch_stat_total_listings(
    city: City,
    offer: str,
    property_type: str,
) -> int:
    city_tags = [get_city_tag(city), get_fr_tag(city)]

    return sc.total_listings(
        offer=offer,
        property_type=property_type,
        cities=city_tags,
    )


st.set_page_config(
    page_title="Eterna Primavera",
    page_icon="🏡",
)


# Sidebar
with st.sidebar:
    st.markdown("## Selecciona tu opción")
    city = City(
        st.selectbox("Ciudad", [c.value for c in City], index=0, format_func=get_name)
    )
    property_type = st.selectbox(
        "Tipo de propiedad",
        search.PROPERTY_TYPES,
        index=0,
        format_func=language.ES["property_type"].get,
    )
    offer = st.selectbox(
        "Tipo de oferta",
        search.OFFERS,
        index=0,
        format_func=language.ES["offer"].get,
    )


sc = main.FincaRaizClient(20)
total_properies = fetch_stat_total_listings(city, offer, property_type)
st.metric("Total de propiedades con estas características", f"{total_properies:,}")


df = fetch_properties(city, offer, property_type)
st.write("## Demo de caracterísitcas")
st.write(f"_{len(df)} propiedades_")
st.dataframe(df.filter(constants.DISPLAY_COLUMNS))

st.write("### Localización")
st.map(data=df.dropna(subset=["lat", "lon"]), zoom=5)

st.plotly_chart(px.histogram(df, x="price_m2", title="Precio m<sup>2</sup>"))
st.plotly_chart(px.histogram(df, x="rooms.name", title="Numero de cuartos"))
st.plotly_chart(px.histogram(df, x="baths.name", title="Numero de baños"))

strat = px.histogram(df, x="stratum.name", title="Estrato")
strat.update_xaxes(
    categoryorder="array",
    categoryarray=[
        "Estrato 1",
        "Estrato 2",
        "Estrato 3",
        "Estrato 4",
        "Estrato 5",
        "Estrato 6",
    ],
)
st.plotly_chart(strat)
