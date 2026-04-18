import streamlit as st

st.title("Análisis Estadístico e IA - UPChiapas")
st.write("Bienvenido, Brandon. Selecciona un archivo CSV para comenzar.")

archivo = st.file_uploader("Cargar archivo CSV", type=["csv"])

if archivo:
    st.success("Archivo cargado con éxito")