import streamlit as st

st.set_page_config(
    page_title="Bienvenido a la Eterna Primavera",
    page_icon="👋",
    layout="wide",
)

st.markdown(
    """
    <h1 style="text-align: center; padding: 5px;">Eterna Primavera</h1>
    <h4 style="text-align: center; padding: 5px;">Un Analizador de Bienes Raíces en Medellín, Colombia</h4>
    <h4 style="text-align: center; padding-top: 5px; padding-bottom:20px;">🌬🏡🌳</h4>
    <p style="text-align: center; padding-top: 5px; padding-bottom:20px;"><i>Toma decisiones inteligentes usando datos</i></p>
    """,
    unsafe_allow_html=True,
)
with st.expander("¿Que és Eterna Primavera?"):
    st.markdown(
        """
        - **Eterna Primavera** 🌬🏡🌳 es una herramienta diseñada para ayudarte a tomar **decisiones inteligentes** al arrendar, vender, o comprar una propiedad en Medellín.
        
        - Su nombre proviene del apodo de la ciudad: *“Medellín, La ciudad de la Eterna Primavera”* 🇨🇴.
        """
    )

with st.expander("¿Cómo puedo usar Eterna Primavera?"):
    st.markdown(
        """
        1. En el menú izquierdo, selecciona la opción **🏘 Analizador de Propiedades**.
        2. Filtra la ciudad, tipo de propiedad y el tipo de oferta que deseas conocer.
    """
    )
with st.expander("¿Cuál es la oferta de Eterna Primavera?"):
    st.markdown(
        """
        **Quiero comprar o vender una propiedad**
        - Conoce el valor exacto del metro cuadrado que otros vendedores están solicitando.
        - Explora inmuebles con tus mismas características y hazle seguimiento al mercado día a día.

        **Quiero arrendar un inmueble**

        - Explora cuales barrios ofrecen mejores precios para el tipo de alojamiento que estás buscando.
        - Conoce cuál es el precio justo para tu canon de arrendamiento, según lo que otros propietarios están pagando por inmuebles similares al que buscas.
        """
    )

with st.expander("¿Qué datos usamos?"):
    st.markdown(
        """
        **Propiedades**
        
        Proviene de plataformas dedicadas a la intermediación del mercado inmobiliario, especializadas en propiedades de Colombia. Eterna Primavera actualiza sus datos cada día.

        **Ciudades**

        Proveniente del departamento de estadística colombiano (DANE). Usamos los últimos datos publicados por la entidad para cada rubro.
        """
    )
