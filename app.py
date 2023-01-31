import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from real_estate.finca_raiz import main, search
from yaml import SafeLoader

COLUMNS_TO_SHOW = [
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

with open('credentials.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')
if authentication_status:
    st.write("# Human Rela Estate - Colombia 🏠🇨🇴")

    text_input = st.text_input("Search with a keyword", "La Estrella, Antioquia")

    st.sidebar.write("## Select your options")
    property_types = st.sidebar.multiselect(
        "Select property types",
        search.PROPERTY_TYPES,
        default="apartment",
        format_func=format_option,
    )
    offers = st.sidebar.multiselect(
        "Select type of offer",
        search.OFFERS,
        default="rent",
        format_func=format_option,
    )

    sc = main.FincaRaizClient(1000)

    total_properies = sc.total_listings(
        text_input, offer=offers, property_type=property_types
    )
    st.metric("Total properties under this search", f"{total_properies:,}")

    if len(property_types) == 1 and len(offers) == 1:
        df = sc.search(text_input, offer=offers, property_type=property_types)
        df["price_m2"] = pd.to_numeric(df["price_m2"])
        min = df["price_m2"].quantile(0.05)
        max = df["price_m2"].quantile(0.95)
        df["price_m2"] = df["price_m2"].where(
            (df["price_m2"] > min) & (df["price_m2"] < max), pd.NA
        )
        
        
        st.write("## Properties characteristics demo")
        st.write(f"_{len(df)} properties_")
        st.dataframe(df.filter(COLUMNS_TO_SHOW))
        

        st.plotly_chart(px.histogram(df, x="price_m2", title="Price per m2"))
        st.plotly_chart(px.histogram(df, x="rooms.name", title="Number of rooms"))
        st.plotly_chart(px.histogram(df, x="baths.name", title="Number of bathrooms"))
        
        strat = px.histogram(df, x="stratum.name", title="Stratum")
        strat.update_xaxes(categoryorder="array", categoryarray=["Estrato 1", "Estrato 2", "Estrato 3", "Estrato 4", "Estrato 5", "Estrato 6"])
        st.plotly_chart(strat)

elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')