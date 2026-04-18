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
from scipy import stats
import numpy as np

# --- PARTE 3: VISUALIZACIÓN ---
st.header("3. Visualización de Distribuciones")

if 'df' in st.session_state:
    df = st.session_state['df']
    var = st.session_state['variable']
    datos = df[var].dropna() # Limpiamos datos nulos por si acaso
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Histograma y KDE")
        fig_hist, ax_hist = plt.subplots()
        sns.histplot(datos, kde=True, ax=ax_hist, color="skyblue")
        st.pyplot(fig_hist)
        
    with col2:
        st.subheader("Boxplot (Outliers)")
        fig_box, ax_box = plt.subplots()
        sns.boxplot(y=datos, ax=ax_box, color="lightgreen")
        st.pyplot(fig_box)

    # Respuestas obligatorias
    st.info("Responde para tu reporte:")
    normal = st.radio("¿La distribución parece normal?", ["Sí", "No"])
    analisis = st.text_area("Análisis de sesgo y outliers:")

    # --- PARTE 4: PRUEBA DE HIPÓTESIS (CORREGIDA) ---
    st.header("4. Prueba de Hipótesis (Prueba Z)")

    # Parámetros que el usuario puede mover
    c1, c2, c3 = st.columns(3)
    with c1:
        # Aquí permitimos que el usuario escriba la hipótesis
        mu_h0 = st.number_input("Hipótesis Nula (μ0):", value=float(datos.mean()))
    with c2:
        tipo_prueba = st.selectbox("Tipo de prueba:", ["Bilateral", "Cola Derecha", "Cola Izquierda"])
    with c3:
        alpha = st.slider("Significancia (α):", 0.01, 0.10, 0.05, step=0.01)

    # CÁLCULOS EN TIEMPO REAL
    n = len(datos)
    media_muestral = datos.mean()
    # Para Prueba Z usamos desviación estándar poblacional conocida 
    # (o la de la muestra si n > 30 como pide tu tarea)
    sigma = datos.std() 
    
    # LA FÓRMULA MÁGICA
    z_stat = (media_muestral - mu_h0) / (sigma / np.sqrt(n))
    
    # Lógica de decisión
    # --- LOGICA DE DECISIÓN REFORZADA ---
    # Calculamos el Z crítico basado en alpha
    if tipo_prueba == "Bilateral":
        z_critico = stats.norm.ppf(1 - alpha/2)
        rechazo = abs(z_stat) > z_critico
    elif tipo_prueba == "Cola Derecha":
        z_critico = stats.norm.ppf(1 - alpha)
        rechazo = z_stat > z_critico
    else: # Cola Izquierda
        z_critico = stats.norm.ppf(alpha)
        rechazo = z_stat < z_critico

    st.subheader("Veredicto de la Prueba")
    
    if rechazo:
        st.error(f"DECISIÓN: RECHAZAR H0")
        st.write("Explicación: El estadístico Z cayó en la zona de rechazo (fuera de los límites permitidos).")
    else:
        st.success(f"DECISIÓN: NO RECHAZAR H0")
        st.write("Explicación: No hay suficiente evidencia para dudar de la hipótesis nula.")

    # GRÁFICA DE LA CAMPANA
    x = np.linspace(-4, 4, 100)
    y = stats.norm.pdf(x, 0, 1)
    fig_z, ax_z = plt.subplots()
    ax_z.plot(x, y, color='black')
    
    # Sombrear zona de rechazo
    if tipo_prueba == "Bilateral":
        ax_z.fill_between(x, y, where=(abs(x) > z_critico), color='red', alpha=0.3, label='Zona de Rechazo')
    elif tipo_prueba == "Cola Derecha":
        ax_z.fill_between(x, y, where=(x > z_critico), color='red', alpha=0.3, label='Zona de Rechazo')
    else:
        ax_z.fill_between(x, y, where=(x < z_critico), color='red', alpha=0.3, label='Zona de Rechazo')
        
    ax_z.axvline(z_stat, color='blue', linestyle='--', label=f'Tu Z: {z_stat:.2f}')
    ax_z.legend()
    st.pyplot(fig_z)