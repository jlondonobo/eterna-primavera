import pandas as pd
import plotly.express as px
import streamlit as st
from cities import City
from constants import EXCHANGE_RATE
from loaders.load_cities import load_cities
from loaders.load_geometries import load_geometries
from loaders.load_listings import load_listings

st.set_page_config(page_title="Analizador de Propiedades", page_icon="🏡", layout="wide")

# Utils run the function load_cities() should fix this issue
# Meanwhile keep below st.set_page
from plots import h3_choropleth_from_latlon, plot_donut
from utils import filter_listings, get_name, import_css

listings = load_listings()
geometries = load_geometries()
cities = load_cities()

CENTERS = {
    "05001": (6.251265320983825, -75.57696852800319),
    "05088": (6.33732, -75.55795),
    "05360": (6.18461, -75.59913),
    "05266": (6.17591, -75.59174),
    "05129": (6.09, -75.638),
    "05631": (6.15153, -75.61657),
    "05212": (6.357621, -75.505078),
    "05380": (6.15769, -75.64317),
    "05308": (6.3792, -75.4453),
    "05079": (6.439, -75.333),
}


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
st.markdown(f"##### ✨ {property_type}s en {offer} en {get_name(city)} ✨")

with st.expander("Filtros Avanzados"):
    rooms = st.multiselect(
        "Habitaciones", ["1", "2", "3", "4", "5+"], ["1", "2", "3", "4", "5+"]
    )
    bathrooms = st.multiselect("Baños", ["1", "2", "3", "4+"], ["1", "2", "3", "4+"])
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
    text = "Precio" if offer == "Venta" else "Arriendo"
    st.metric(f"{text} promedio ({currency})", f"${listings['price'].mean():,.0f}")
with col2:
    st.metric("Área promedio", f"{listings['area'].mean():,.0f}m2")
with col3:
    st.metric("Total de propiedades", value=f"{len(listings):,}")

# ------ TABS
tab1, tab2, tab3 = st.tabs(
    ["Análisis de Precios", "Características de las Propiedades", "Localización"]
)
with tab1:
    measure = st.radio(
        "Medida",
        ["Metro cuadrado", "Precio Total"],
        index=0,
        horizontal=True,
    )

    st.markdown(
        f"""
        <h3 style="padding-bottom: 0px;">Precios de {property_type.lower()}s en {get_name(city)}</h3>
        <p>{measure} ({currency})</p>
        """,
        unsafe_allow_html=True,
    )

    column = "price_m2" if measure == "Metro cuadrado" else "price"

    def simple_histogram():
        """Plot price histogram"""
        mean_price = listings[column].mean()
        simple_name = "metro cuadrado" if measure == "Metro cuadrado" else "Propiedad"

        histogram = px.histogram(listings, x=column, labels={column: measure})
        histogram.update_layout(bargap=0.05, height=500)
        histogram.update_xaxes(tickprefix="$")
        histogram.update_yaxes(title_text="Número de propiedades")
        histogram.add_vline(
            mean_price,
            line_width=3,
            line_dash="dash",
            line_color="#EC5A53",
            annotation=dict(    
                text=f"Precio promedio {simple_name} ({currency})<br><b>${mean_price:,.0f}<b>",
                y=1.1,
                showarrow=False,
                font=dict(color="white"),
                align="center",
                bordercolor="white",
                borderpad=1,
                borderwidth=1,
            ),
        )
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
        center={"lat": CENTERS[city][0], "lon": CENTERS[city][1]}
    )
    st.plotly_chart(choropleth, use_container_width=True)
