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
  # --- PARTE 4: PRUEBA DE HIPÓTESIS ---
    st.header("4. Prueba de Hipótesis (Prueba Z)")

    c1, c2, c3 = st.columns(3)
    with c1:
        mu_h0 = st.number_input("Hipótesis Nula (μ0):", value=float(datos.mean()))
    with c2:
        tipo_prueba = st.selectbox("Tipo de prueba:", ["Bilateral", "Cola Derecha", "Cola Izquierda"])
    with c3:
        alpha = st.slider("Significancia (α):", 0.01, 0.10, 0.05, step=0.01)

    # Cálculos base
    n = len(datos)
    media_muestral = datos.mean()
    sigma = datos.std() 
    z_stat = (media_muestral - mu_h0) / (sigma / np.sqrt(n))

    # --- INICIALIZACIÓN CRÍTICA ---
    # Esto evita el error de "not defined"
    p_val = 0.0
    z_critico = 0.0
    rechazo = False

    if tipo_prueba == "Bilateral":
        p_val = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        z_critico = stats.norm.ppf(1 - alpha/2)
        rechazo = abs(z_stat) > z_critico
    elif tipo_prueba == "Cola Derecha":
        p_val = 1 - stats.norm.cdf(z_stat)
        z_critico = stats.norm.ppf(1 - alpha)
        rechazo = z_stat > z_critico
    else: # Cola Izquierda
        p_val = stats.norm.cdf(z_stat)
        z_critico = stats.norm.ppf(alpha)
        rechazo = z_stat < z_critico

    # Definimos la variable decision para que la use Gemini
    decision = "RECHAZAR H0" if rechazo else "NO RECHAZAR H0"

    st.subheader("Veredicto de la Prueba")
    if rechazo:
        st.error(f"DECISIÓN: {decision}")
    else:
        st.success(f"DECISIÓN: {decision}")

    # (Aquí va tu código de la Gráfica de la Campana que ya tienes)
    # ... 

    # --- PARTE 5: MÓDULO DE IA (GEMINI) ---
    import google.generativeai as genai
    st.header("5. Asistente de IA (Google Gemini)")
    api_key = st.text_input("Introduce tu Google Gemini API Key:", type="password")

    if api_key:
        genai.configure(api_key=api_key)
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            if st.button("Consultar a la IA"):
                # Ahora p_val y decision ya existen garantizadamente
                prompt_ia = f"""
                Actúa como un experto en estadística.
                Resultados de la prueba Z:
                - Media muestral: {media_muestral:.4f}
                - mu0: {mu_h0:.4f}
                - Z calculado: {z_stat:.4f}
                - P-value: {p_val:.4f}
                - Alpha: {alpha}
                - Decisión: {decision}
                
                ¿Es correcta la decisión? Explica brevemente.
                """
                with st.spinner("Analizando..."):
                    response = model.generate_content(prompt_ia)
                    st.subheader("Interpretación de la IA:")
                    st.write(response.text)
        except Exception as e:
            st.error(f"Error: {e}")