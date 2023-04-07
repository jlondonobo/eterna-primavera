from enum import Enum


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