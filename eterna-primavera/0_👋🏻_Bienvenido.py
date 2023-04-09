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
        <ol>
        <li> En el menú izquierdo, selecciona la opción <a href='/Analizador_de_Propiedades'>🏘 Analizador de Propiedades</a>.
        <li>Filtra la ciudad, tipo de propiedad y el tipo de oferta que deseas conocer.
        </ol>
    """,
    unsafe_allow_html=True
    )
with st.expander("¿Cuál es la oferta de Eterna Primavera?"):
    st.markdown(
        """
        **Tómate 5 minutos para explorar el Analizador de Propiedades y obtén**:
        
        ✅ Información puntual para ahorrar $ en tu próxima compra o arriendo de una propiedad en Medellín.
        
        ✅ Una mayor capacidad de negociación con imobiliarias, inquilinos y vendedores y compradores.
        
        ✅ Gráficos personalizados a la medida de tus necesidades.
        """
    )

with st.expander("¿De qué datos se alimenta Eterna Primavera?"):
    st.markdown(
        """
        - **Propiedades**: Creamos un dataset único para la ciudad de Medellín que actualizamos diariamente. Los datos provienen de una búsqueda exhaustiva de plataformas dedicadas a la intermediación del mercado inmobiliario, especializadas en Colombia.

        - **Ciudades**: Proveniente del departamento de estadística colombiano (DANE). Usamos los últimos datos publicados por la entidad para cada rubro.
        """
    )
