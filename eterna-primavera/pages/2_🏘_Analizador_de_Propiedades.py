import pandas as pd
import plotly.express as px
import streamlit as st
from cities import City
from constants import EXCHANGE_RATE
from loaders.load_cities import load_cities
from loaders.load_geometries import load_geometries
from loaders.load_listings import load_listings

st.set_page_config(page_title="Eterna Primavera", page_icon="🏡", layout="wide")

# Utils run the function load_cities() should fix this issue
# Meanwhile keep below st.set_page
from plots import h3_choropleth_from_latlon, plot_donut
from utils import filter_listings, get_name, import_css

listings = load_listings()
geometries = load_geometries()
cities = load_cities()


# Sidebar
with st.sidebar:
    valid_offers = ["Venta", "Arriendo"]
    valid_properties = ["Apartamento", "Casa"]

    st.markdown("## Selecciona tu opción")
    city = City(
        st.selectbox("Ciudad", [c.value for c in City], index=0, format_func=get_name)
    )
    property_type = st.selectbox(
        "Tipo de propiedad",
        valid_properties,
        index=0,
    )
    offer = st.selectbox(
        "Tipo de oferta",
        valid_offers,
        index=0,
    )
    currency = st.radio(
        "Moneda",
        ["COP", "USD"],
        horizontal=True,
    )


def update_currency(df: pd.DataFrame, currency: str) -> pd.DataFrame:
    """Convert prices to COP or USD."""
    df["price"] = df["price"] / EXCHANGE_RATE[currency]
    df["price_m2"] = df["price_m2"] / EXCHANGE_RATE[currency]
    return df


st.markdown("# Analizador de Propiedades")
with st.expander("Filtros Avanzados"):
    rooms = st.multiselect(
        "Habitaciones",
        ["1", "2", "3", "4", "5+"],
        ["1", "2", "3", "4", "5+"]
    )
    bathrooms = st.multiselect(
        "Baños",
        ["1", "2", "3", "4+"],
        ["1", "2", "3", "4+"]
    )
    stratum = st.multiselect(
        "Estrato",
        ["Estrato 3", "Estrato 4", "Estrato 5", "Estrato 6"],
        ["Estrato 3", "Estrato 4", "Estrato 5", "Estrato 6"],
    )

listings = update_currency(listings, currency)
listings = filter_listings(
    listings,
    city=city,
    property_type=property_type,
    offer=offer,
    rooms=rooms,
    bathrooms=bathrooms,
    stratum=stratum,
)

import_css("eterna-primavera/assets/2_analizador_style.css")

# ------ TITULO

# ------ METRICS
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(f"Precio promedio ({currency})", f"${listings['price'].mean():,.0f}")
with col2:
    st.metric("Área promedio", f"{listings['area'].mean():,.0f}m2")
with col3:
    st.metric("Total de propiedades", value=f"{len(listings):,}")

# ------ TABS
tab1, tab2, tab3 = st.tabs(
    ["Análisis de Precios", "Características de las Propiedades", "Localización"]
)
with tab1:
    st.markdown(
        f"## Precios de {property_type.lower()}s en {get_name(city)}"
    )

    def simple_histogram():
        """Plot price histogram"""
        histogram = px.histogram(
            listings, x="price_m2", labels={"price_m2": f"{currency} por m<sup>2</sup>"}
        )
        histogram.update_layout(bargap=0.05, height=500)
        histogram.update_xaxes(tickformat="$,.2s")
        return histogram

    st.plotly_chart(simple_histogram(), use_container_width=True)


with tab2:
    st.markdown("## Cuales son sus características?")

    rooms = listings["rooms"].value_counts().sort_index()
    baths = listings["baths"].value_counts().sort_index()
    stratum = listings["stratum"].value_counts().sort_index()

    def get_most_common_config(s: pd.Series) -> str:
        """Return most common type of Room, Bath or Stratum from value counts."""
        return str(s.idxmax())

    st.markdown(
        f"La mayoría de propiedades de esta búsqueda tienen **{get_most_common_config(rooms)} habitaciones**, **{get_most_common_config(baths)} baños** y son **{get_most_common_config(stratum).lower()}**."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(plot_donut(rooms), use_container_width=True)
    with col2:
        st.plotly_chart(plot_donut(baths), use_container_width=True)
    with col3:
        st.plotly_chart(plot_donut(stratum), use_container_width=True)


with tab3:
    st.markdown("## Donde están localizadas?")
    mapper = {
        "count": "Conteo de Propiedades",
        "price": "Precio promedio (m2)",
    }
    type = st.selectbox(
        "Qúe métrica quieres ver?",
        ["count", "price"],
        index=0,
        format_func=mapper.get,
    )
    choropleth = h3_choropleth_from_latlon(
        type,
        listings,
        "lat",
        "lon",
        9,
        zoom=11,
    )
    st.plotly_chart(choropleth, use_container_width=True)
