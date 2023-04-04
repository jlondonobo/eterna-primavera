import pandas as pd
import plotly.express as px
import streamlit as st
from real_estate.finca_raiz import main, search
from shapely import wkt

COLUMNS_TO_SHOW = [
    "price",
    "area",
    "price_m2",
    "is_new",
    "description",
    "stratum.name",
    "rooms.name",
    "baths.name",
    "client.client_type",
    "client.first_name",
    "client.company_name",
    "contact.phones",
]


def format_option(option):
    return option.replace("-", " ").title()


st.set_page_config(
    page_title="Bienvenido a la Eterna Primavera",
    page_icon="👋",
)

st.markdown("# Eterna Primavera: Análisis de Propiedades Raiz en Medellín")

text_input = st.text_input("Búsqueda de términos clave", "La Estrella, Antioquia")

st.sidebar.write("## Selecciona tu opción")
property_types = st.sidebar.multiselect(
    "Tipo de propiedad",
    search.PROPERTY_TYPES,
    default="apartment",
    format_func=format_option,
)
offers = st.sidebar.multiselect(
    "Tipo de oferta",
    search.OFFERS,
    default="rent",
    format_func=format_option,
)

sc = main.FincaRaizClient(1000)

total_properies = sc.total_listings(
    text_input, offer=offers, property_type=property_types
)
st.metric("Total de propiedades con estas características", f"{total_properies:,}")

if len(property_types) == 1 and len(offers) == 1:
    df = sc.search(text_input, offer=offers, property_type=property_types)
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

    st.write("## Demo de caracterísitcas")
    st.write(f"_{len(df)} propiedades_")
    st.dataframe(df.filter(COLUMNS_TO_SHOW))

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
