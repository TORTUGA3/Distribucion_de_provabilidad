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
    st.subheader("Visualización de la Campana de Gauss")
    
    # Crear eje X (de -4 a 4 desviaciones estándar)
    x = np.linspace(-4, 4, 1000)
    y = stats.norm.pdf(x, 0, 1)

    fig_z, ax_z = plt.subplots(figsize=(10, 5))
    ax_z.plot(x, y, color='black', label='Distribución Normal Estándar')

    # Sombrear zonas de rechazo según el tipo de prueba
    if tipo_prueba == "Bilateral":
        ax_z.fill_between(x, y, where=(abs(x) > z_critico), color='red', alpha=0.3, label='Zona de Rechazo')
        ax_z.axvline(z_critico, color='red', linestyle='--')
        ax_z.axvline(-z_critico, color='red', linestyle='--')
    elif tipo_prueba == "Cola Derecha":
        ax_z.fill_between(x, y, where=(x > z_critico), color='red', alpha=0.3, label='Zona de Rechazo')
        ax_z.axvline(z_critico, color='red', linestyle='--')
    else: # Cola Izquierda
        ax_z.fill_between(x, y, where=(x < z_critico), color='red', alpha=0.3, label='Zona de Rechazo')
        ax_z.axvline(z_critico, color='red', linestyle='--')

    # Dibujar la posición de tu Z calculado (el punto azul)
    ax_z.axvline(z_stat, color='blue', linewidth=2, label=f'Tu Z calculado: {z_stat:.2f}')
    ax_z.scatter([z_stat], [0], color='blue', s=100, zorder=5)

    ax_z.set_title("Distribución Z y Regiones de Rechazo")
    ax_z.legend()
    st.pyplot(fig_z)

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
             Actúa como un profesor de estadística muy paciente y experto en explicar conceptos complejos a principiantes.
            
             Contexto del experimento:
             - Tenemos un promedio real de {media_muestral:.2f}.
             - Alguien propuso una teoría (Hipótesis Nula) de que el promedio debería ser {mu_h0:.2f}.
             - Usamos un nivel de tolerancia al error (Alpha) de {alpha}.
             - El resultado de nuestro cálculo (Estadístico Z) fue {z_stat:.4f}.
             - La probabilidad de que esto sea pura casualidad (P-value) es de {p_val:.4f}.
             - La decisión tomada es: {decision}.

             TAREA:
             1. Explica si la decisión es correcta usando una analogía sencilla.
             2. No uses lenguaje matemático pesado. Explica el 'P-value' como si fuera una medida de 'qué tan sorprendente' es el resultado.
             3. Dile ala persona si su decisión tiene sentido lógico basado en la diferencia entre el promedio real y el hipotético.
             4. no es nesesario mucho tenxto solo breves explicaciones por que  y siendo directo a la desicion
             """
            with st.spinner("Analizando..."):
                    response = model.generate_content(prompt_ia)
                    st.subheader("Interpretación de la IA:")
                    st.write(response.text)
        except Exception as e:
            st.error(f"Error: {e}")