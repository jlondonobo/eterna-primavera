from enum import Enum

import pandas as pd
import streamlit as st


class City(str, Enum):
    medellin = "05001"
    bello = "05088"
    itagui = "05360"
    envigado = "05266"
    caldas = "05129"
    sabaneta = "05631"
    copacabana = "05212"
    la_estrella = "05380"
    girardota = "05308"
    barbosa = "05079"


@st.cache_data
def read_city_details():
    return (
        pd.read_csv(
            "eterna-primavera/aux_data/codigos_dane.csv", dtype={"CODIGO_MUNICIPIO": str}
        )
        .set_index("CODIGO_MUNICIPIO")
        .to_dict(orient="index")
    )


FR_ALTERNATIVE_CODES = {
    City.medellin: "5500006-medellín",
    City.bello: "5500005-bello",
    City.itagui: "5500002-itaguí",
    City.envigado: "5500001-envigado",
    City.caldas: "5500011-caldas",
    City.sabaneta: "5500016-sabaneta",
    City.copacabana: "5500008-copacabana",
    City.la_estrella: "5500003-la-estrella",
    City.girardota: "5500009-girardota",
    City.barbosa: "5500010-barbosa",
}


def get_city_tag(city: City) -> str:
    """Return FincaRaiz-city tag for a city given its DANE code."""
    return f"city-colombia-{city[:2]}-{city[2:]}"


def get_fr_tag(city: City) -> str:
    """Retrun propietary FincaRaiz tag for a place"""
    return f"colombia-antioquia-{FR_ALTERNATIVE_CODES[city]}"


def get_name(city: City) -> str:
    """Retrun canonical name of the city."""
    city_details = read_city_details()
    return city_details[city]["Nombre"]


def get_inhabitants(city: City) -> int:
    return 100000    return 100000