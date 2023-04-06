import constants
import language
import pandas as pd
import plotly.express as px
import streamlit as st
from cities import City, get_city_tag, get_fr_tag, get_name
from real_estate.finca_raiz import main, search
from shapely import wkt

st.set_page_config(
    page_title="Eterna Primavera",
    page_icon="🏡",
    layout="wide"
)


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
df = fetch_properties(city, offer, property_type)

st.markdown("# 🏘 Analizador de Propiedades")

col1, col2, col3 = st.columns(3)

col1.metric("Precio promedio", f"${df['price'].mean():,.0f}")
col2.metric("Área promedio", f"{df['area'].mean():,.0f}m2")
col3.metric("Total de propiedades", value=f"{total_properies:,}")


st.markdown('''
<style>
/*center metric label*/
[data-testid="stHorizontalBlock"]{
    outline: 1px solid black;
    padding: 20px 50px;
    margin-top: 20px;
    border-radius: 10px;

}

[data-testid="metric-container"]{
    text-align: center;
}

/*center metric value*/
[data-testid="stMetricLabel"]{
    display: block;
}
</style>
''', unsafe_allow_html=True)



plotly_chart = px.histogram(df, x="price_m2", title="Precio m<sup>2</sup>")
plotly_chart.update_layout(bargap=0.05)
plotly_chart.update_xaxes(tickformat="$,.2s")

st.plotly_chart(plotly_chart)


# st.write("## Demo de caracterísitcas")
# st.write(f"_{len(df)} propiedades_")
# st.dataframe(df.filter(constants.DISPLAY_COLUMNS))

# st.write("### Localización")
# st.map(data=df.dropna(subset=["lat", "lon"]), zoom=5)

# st.plotly_chart(px.histogram(df, x="price_m2", title="Precio m<sup>2</sup>"))
# st.plotly_chart(px.histogram(df, x="rooms.name", title="Numero de cuartos"))
# st.plotly_chart(px.histogram(df, x="baths.name", title="Numero de baños"))

# strat = px.histogram(df, x="stratum.name", title="Estrato")
# strat.update_xaxes(
#     categoryorder="array",
#     categoryarray=[
#         "Estrato 1",
#         "Estrato 2",
#         "Estrato 3",
#         "Estrato 4",
#         "Estrato 5",
#         "Estrato 6",
#     ],
# )
# st.plotly_chart(strat)
