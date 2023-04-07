import language
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from cities import City, get_city_tag, get_fr_tag, get_name
from real_estate.finca_raiz import main, search
from shapely import wkt
from utils import import_css, plot_h3_listings

st.set_page_config(page_title="Eterna Primavera", page_icon="🏡", layout="wide")


def trim_outliers(s: pd.Series, min: float = 0.05, max: float = 0.95) -> pd.Series:
    """Returns a series with outliers turned into NA."""
    return s.where((s > s.quantile(min)) & (s < s.quantile(max)), pd.NA)


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
total_properies = fetch_stat_total_listings(city, offer, property_type)
df = fetch_properties(city, offer, property_type)

st.markdown("# Analizador de Propiedades")

col1, col2, col3 = st.columns(3)

col1.metric("Precio promedio", f"${df['price'].mean():,.0f}")
col2.metric("Área promedio", f"{df['area'].mean():,.0f}m2")
col3.metric("Total de propiedades", value=f"{total_properies:,}")

tab1, tab2, tab3 = st.tabs(
    ["Análisis de Precios", "Características de las Propiedades", "Localización"]
)
with tab1:
    st.markdown(
        f"## Precios de {language.ES['property_type'][property_type].lower()}s en {get_name(city)}"
    )

    plotly_chart = px.histogram(
        df, x="price_m2", labels={"price_m2": "Precio m<sup>2</sup>"}
    )
    plotly_chart.update_layout(bargap=0.05, height=500)
    plotly_chart.update_xaxes(tickformat="$,.2s")

    st.plotly_chart(plotly_chart, use_container_width=True)


with tab2:

    def compute_donut(s: pd.Series) -> go.Figure:
        mapper = {
            "rooms.name": "No. Habitaciones",
            "baths.name": "No. Baños",
            "stratum.name": "Estrato",
        }
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=s.index,
                    values=s.values,
                    hole=0.5,
                    textinfo="label+percent",
                    sort=False,
                    direction="clockwise",
                )
            ]
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=False,
            title=dict(
                text=mapper[s.name],
                x=0.5,
                xanchor="center",
            ),
            height=300,
        )
        return fig

    st.markdown("## Cuales son sus características?")

    rooms = df["rooms.name"].value_counts().sort_index()
    baths = df["baths.name"].value_counts().sort_index()
    stratum = df["stratum.name"].value_counts().sort_index()

    def get_most_common_config(s: pd.Series) -> str:
        """Return most common type of Room, Bath or Stratum from value counts."""
        return str(s.idxmax())

    st.markdown(
        f"La mayoría de propiedades de esta búsqueda tienen **{get_most_common_config(rooms)} habitaciones**, **{get_most_common_config(baths)} baños** y son **{get_most_common_config(stratum).lower()}**."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(compute_donut(rooms), use_container_width=True)
    with col2:
        st.plotly_chart(compute_donut(baths), use_container_width=True)
    with col3:
        st.plotly_chart(compute_donut(stratum), use_container_width=True)


with tab3:
    st.markdown("## Donde están localizadas?")
    st.plotly_chart(plot_h3_listings(df, "lat", "lon", 9), use_container_width=True)
