import streamlit as st
from cities import City, get_inhabitants, get_name
from loaders.load_cities import load_cities
from loaders.load_geometries import load_geometries
from plots import plot_highlighted_choropleth
from st_click_detector import click_detector
from utils import import_css

st.set_page_config(layout="wide")
geometries = load_geometries()
cities = load_cities()


def get_geometries_with_data():
    return geometries.merge(cities, left_on="MPIO_CDPMP", right_on="MPIO", how="left")


# TEMPORARY
YEAR = 2023

import_css("eterna-primavera/assets/1_sobre_style.css")
st.markdown("# Sobre Medellín")
st.markdown(
    """
    Medellín es la **segunda ciudad más grande de Colombia** y se ha consolidado
    como una de las metrópolis más vibrantes y atractivas de América Latina.
    En los últimos años, ha experimentado un notable auge en el **sector inmobiliario** 🏠 
    gracias a su alto nivel de oportunidades en términos de desarrollo
    de infraestructura y a su brillante atractivo turístico.

    Con un clima cálido todo el año, una rica historia y cultura, y una escena
    de vida nocturna y gastronómica en constante evolución, Medellín
    ha ganado reconocimiento internacional como un destino turístico y un **lugar atractivo
    para vivir**. Este auge ha llevado a una expansión en la oferta inmobiliaria,
    desde apartamentos de lujo y condominios hasta nuevas urbanizaciones
    y proyectos de viviendas sostenibles.
    """
)
st.markdown(
    """
    <img src="https://blog.pinbus.com/hubfs/joel-duncan-Iqa-WlbNjqs-unsplash.jpg" width="100%" style="border-radius: 10px; margin-bottom: 10px">
    """,
    unsafe_allow_html=True,
)


def clickable_city(city: City):
    return f'<a href="" id="{city}">{get_name(city, cities)}</a>'


content = f"""
    <p>El área metropolitana de Medellín está compuesta por <b>10 municipios</b> que se
    han ido incorporando a lo largo del tiempo. Estos municipios son:
    {clickable_city(City.caldas)},
    {clickable_city(City.la_estrella)},
    {clickable_city(City.sabaneta)},
    {clickable_city(City.envigado)},
    {clickable_city(City.itagui)},
    {clickable_city(City.medellin)},
    {clickable_city(City.bello)},
    {clickable_city(City.copacabana)},
    {clickable_city(City.girardota)} y
    {clickable_city(City.barbosa)}
    </p>
"""

clicked = click_detector(content)

st.info("Toca en el nombre de un municipio para ver su ubicación en el mapa.", icon="💡")
st.markdown(
    f"""
    <h4 style="padding-bottom: 0px;">{get_name(City(clicked), cities) if clicked else "Medellín y sus municipios"}</h4>
    <p><i>Total de habitantes: {get_inhabitants(City(clicked), YEAR, cities) if clicked else cities["population_2023"].sum():,}<i></p>
    """,
    unsafe_allow_html=True,
)



# PLOT: Highlightable cities
cities = load_cities()
plot = plot_highlighted_choropleth(
    get_geometries_with_data(), clicked, "MPIO_CDPMP", hover_data={"population_2023": True}
)
st.plotly_chart(plot, use_container_width=True)
