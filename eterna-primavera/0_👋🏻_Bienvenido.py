import streamlit as st

st.set_page_config(
    page_title="Bienvenido a la Eterna Primavera",
    page_icon="👋",
)

st.markdown(
    """
    <h1 style="text-align: center; padding: 5px;">Eterna Primavera</h1>
    <h4 style="text-align: center; padding: 5px;">Un Análisis de Bienes Raíces en Medellín, Colombia</h4>
    <h4 style="text-align: center; padding-top: 5px; padding-bottom:20px;">🌬🏡🌳</h4>
    """,
    unsafe_allow_html=True
)
with st.expander("¿Por qué Medellín?"):
    st.markdown(
        """
        Por qué no?
        """
    )

with st.expander("Cómo puedo usar Eterna Primavera?"):
    st.markdown(
        """
        ## ¿Cómo puedo usar Eterna Primavera?
        Por qué no?
        """
    )
