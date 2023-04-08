import language
import pandas as pd
import plotly.express as px
import streamlit as st
from cities import City
from loaders.load_cities import load_cities
from loaders.load_geometries import load_geometries
from real_estate.finca_raiz import main, search
from shapely import wkt
from transformers.trim_outliers import trim_outliers

st.set_page_config(page_title="Eterna Primavera", page_icon="🏡", layout="wide")

# Utils run the function load_cities() should fix this issue
# Meanwhile keep below st.set_page
from plots import h3_choropleth_from_latlon, plot_donut
from utils import get_city_tag, get_fr_tag, get_name, import_css


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
def fetch_properties(city: City, offers: str, property_type: str) -> pd.DataFrame:
    city_tags = [get_city_tag(city), get_fr_tag(city)]

    df = sc.search(offer=offers, property_type=property_type, cities=city_tags)

    df["geometry"] = df["locations.location_point"].apply(wkt.loads)
    df["lat"] = df["geometry"].apply(lambda p: p.y)
    df["lon"] = df["geometry"].apply(lambda p: p.x)
    df["lat"] = df["lat"].where(df["lat"].between(4, 11), pd.NA)
    df["lon"] = df["lon"].where(df["lon"].between(-76, -73), pd.NA)
    df["area"] = pd.to_numeric(df["area"])

    df = df.pipe(parse_prices)
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


geometries = load_geometries()
cities = load_cities()


# Sidebar
with st.sidebar:
    valid_offers = [o for o in search.OFFERS if o != "lease"]

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
        valid_offers,
        index=0,
        format_func=language.ES["offer"].get,
    )

import_css("eterna-primavera/assets/2_analizador_style.css")

sc = main.FincaRaizClient(20)
stat_total_listings = fetch_stat_total_listings(city, offer, property_type)
listings = fetch_properties(city, offer, property_type)

# ------ TITULO
st.markdown("# Analizador de Propiedades")

with st.expander("Filtros avanzados"):
    # TODO: Read these from the data
    rooms = st.multiselect("Cuartos", [1, 2, 3, 4, 5, 6], default=[1, 2, 3, 4, 5, 6])
    baths = st.multiselect("Baños", [1, 2, 3, 4, 5, 6], default=[1, 2, 3, 4, 5, 6])
    stratum = st.multiselect("Estrato", ["Estrato 1", 2, 3, 4, 5, 6], default=["Estrato 1", 2, 3, 4, 5, 6])


# ------ METRICS
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Precio promedio", f"${listings['price'].mean():,.0f}")
with col2:
    st.metric("Área promedio", f"{listings['area'].mean():,.0f}m2")
with col3:
    st.metric("Total de propiedades", value=f"{stat_total_listings:,}")

# ------ TABS
tab1, tab2, tab3 = st.tabs(
    ["Análisis de Precios", "Características de las Propiedades", "Localización"]
)
with tab1:
    st.markdown(
        f"## Precios de {language.ES['property_type'][property_type].lower()}s en {get_name(city)}"
    )

    def simple_histogram():
        """Plot price histogram"""
        histogram = px.histogram(
            listings, x="price_m2", labels={"price_m2": "Precio m<sup>2</sup>"}
        )
        histogram.update_layout(bargap=0.05, height=500)
        histogram.update_xaxes(tickformat="$,.2s")
        return histogram

    st.plotly_chart(simple_histogram(), use_container_width=True)


with tab2:
    st.markdown("## Cuales son sus características?")

    rooms = listings["rooms.name"].value_counts().sort_index()
    baths = listings["baths.name"].value_counts().sort_index()
    stratum = listings["stratum.name"].value_counts().sort_index()

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
        type, listings, "lat", "lon", 9, zoom=11, 
    )
    st.plotly_chart(choropleth, use_container_width=True)
