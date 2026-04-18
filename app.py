import streamlit as st
import pandas as pd

st.title("📊 App de Análisis Estadístico - UPChiapas")

# 1. Módulo de Carga de Datos
st.header("1. Carga de Datos")
archivo = st.file_uploader("Sube tu archivo CSV", type=["csv"])

if archivo is not None:
    df = pd.read_csv(archivo)
    st.write("Vista previa de los datos:")
    st.dataframe(df.head())

    # 2. Selección de Variable
    st.header("2. Selección de Variable")
    columnas_numericas = df.select_dtypes(include=['number']).columns.tolist()
    
    if columnas_numericas:
        variable = st.selectbox("Selecciona la variable para el análisis:", columnas_numericas)
        st.write(f"Has seleccionado: **{variable}**")
        
        # Guardamos el dataframe en la sesión para usarlo en los siguientes módulos
        st.session_state['df'] = df
        st.session_state['variable'] = variable
    else:
        st.error("El archivo no contiene columnas numéricas.")
import matplotlib.pyplot as plt
import seaborn as sns

# ... (debajo de donde seleccionaste la variable) ...

st.header("3. Visualización de Distribuciones")

if 'df' in st.session_state:
    df = st.session_state['df']
    var = st.session_state['variable']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Histograma y KDE")
        fig_hist, ax_hist = plt.subplots()
        sns.histplot(df[var], kde=True, ax=ax_hist, color="skyblue")
        st.pyplot(fig_hist)
        
    with col2:
        st.subheader("Boxplot (Outliers)")
        fig_box, ax_box = plt.subplots()
        sns.boxplot(y=df[var], ax=ax_box, color="lightgreen")
        st.pyplot(fig_box)

    # Sección de respuestas obligatorias
    st.subheader("Análisis de la Distribución")
    col_a, col_b = st.columns(2)
    with col_a:
        normal = st.radio("¿La distribución parece normal?", ["Sí", "No", "Inconcluso"])
    with col_b:
        sesgo = st.text_input("¿Hay sesgo o outliers? Explica brevemente:")
        