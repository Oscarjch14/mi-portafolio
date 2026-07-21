import streamlit as st

st.set_page_config(page_title="Portafolio | Oscar Chuquihuamani", layout="wide")

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
<style>
    /* Igualar el color de fondo del panel lateral al de tu foto anime */
    [data-testid="stSidebar"] {
        background-color: #142c52 !important; 
    }
    
    /* Ocultar la barra de desplazamiento (scrollbar) para un look limpio */
    [data-testid="stSidebar"] {
        scrollbar-width: none; /* Para Firefox */
    }
    [data-testid="stSidebar"]::-webkit-scrollbar {
        display: none; /* Para Chrome, Safari y Edge */
    }
    
    /* Estilos de los enlaces del menú */
    [data-testid="stSidebar"] a {
        color: #E2C044; 
        text-decoration: none; 
        font-weight: 500;
        font-size: 16px;
    }
    [data-testid="stSidebar"] a:hover {
        color: #FFFFFF; 
        text-decoration: underline;
    }

    /* --- NUEVOS ESTILOS: TÍTULO Y MÁQUINA DE ESCRIBIR --- */
    
    /* Título Fluorescente Animado */
    .titulo-fluorescente {
        font-size: 3.5rem;
        font-weight: 900;
        /* Degradado con colores neón que resaltan en fondo oscuro */
        background: linear-gradient(90deg, #00f2fe, #4facfe, #ff0844, #ffb199, #00f2fe);
        background-size: 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: brillar 8s linear infinite;
        margin-bottom: 5px;
    }

    /* Animación del movimiento de los colores */
    @keyframes brillar {
        0% { background-position: 0% 50%; }
        100% { background-position: 400% 50%; }
    }

    /* Efecto Máquina de Escribir para el subtítulo */
    .maquina-escribir-container {
        display: inline-block;
        margin-bottom: 25px;
    }

    .maquina-escribir {
        color: #FFD700; /* Color Amarillo */
        font-family: 'Courier New', Courier, monospace; /* Fuente de código/escritura */
        font-size: 1.5rem;
        font-weight: 600;
        overflow: hidden;
        border-right: 0.15em solid #FFD700; /* El cursor amarillo que parpadea */
        white-space: nowrap;
        margin: 0;
        letter-spacing: 0.05em;
        /* Aumentamos los espacios a 48 y el tiempo a 4.5s para que entre todo suavemente */
        animation: 
            teclear 4.5s steps(48, end) infinite alternate,
            parpadear 0.8s step-end infinite;
    }

    @keyframes teclear {
        from { width: 0; }
        to { width: 48ch; } /* Ampliamos el margen para asegurar la palabra completa */
    }

    @keyframes parpadear {
        from, to { border-color: transparent; }
        50% { border-color: #FFD700; }
    }
    
    /* --- COLOR VERDE PARA EL BOTÓN DE DESCARGA --- */
    [data-testid="stDownloadButton"] button {
        background-color: #25D366 !important; /* Verde vibrante */
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        transition: 0.3s;
    }
    [data-testid="stDownloadButton"] button:hover {
        background-color: #128C7E !important; /* Verde más oscuro al pasar el mouse */
    }
</style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (MENÚ Y FOTO ANIME) ---
st.sidebar.title("📌 Índice de Navegación")

# Lista de enlaces actualizados con la nueva sección
st.sidebar.markdown("- [1. Perfil Profesional](#perfil-profesional)")
st.sidebar.markdown("- [2. Formación Académica](#formacion-academica)")
st.sidebar.markdown("- [3. Experiencia Profesional](#experiencia-profesional)")
st.sidebar.markdown("- [4. Competencias y Fortalezas](#competencias)")
st.sidebar.markdown("- [5. Proyectos](#proyectos)")
st.sidebar.markdown("- [6. Contáctame](#contactame)")

# Espacios en blanco para separar el menú de la imagen
st.sidebar.write("") 
st.sidebar.write("") 

# Achicamos la imagen usando 3 columnas en el sidebar
col_side1, col_side2, col_side3 = st.sidebar.columns([1, 3, 1])

with col_side2:
    try:
        st.image("foto_2.jpg", use_container_width=True)
    except FileNotFoundError:
        st.info("Sube tu foto anime como 'foto_2.jpg'.")

# --- CUERPO PRINCIPAL DE LA PÁGINA ---

# Inyectamos el título fluorescente y la máquina de escribir
st.markdown("""
    <div class="titulo-fluorescente">Mi Portafolio Profesional</div>
    <div class="maquina-escribir-container">
        <div class="maquina-escribir">¡Hola, soy Oscar, y bienvenido a mi página!</div>
    </div>
""", unsafe_allow_html=True)

st.divider()

# --- 1. PERFIL PROFESIONAL ---
st.header("Perfil Profesional", anchor="perfil-profesional")

col1, col2 = st.columns([1, 3]) 

with col1:
    try:
        st.image("foto.jpg", use_container_width=True)
    except FileNotFoundError:
        st.info("Sube tu foto principal a la carpeta.")

with col2:
    st.write("""
    Estudiante de Economía perteneciente al tercio superior, con enfoque en finanzas corporativas, análisis de datos y gestión de riesgos. Me caracterizo por una alta disciplina y capacidad para profundizar en problemas complejos hasta comprenderlos completamente. 
    
    Cuento con experiencia en la transformación y visualización de datos, así como en la elaboración de informes técnicos orientados a la evaluación de la salud financiera, rentabilidad corporativa y cumplimiento normativo. Busco aportar valor mediante el análisis cuantitativo riguroso y la toma de decisiones basada en la consistencia de datos financieros.
    """)
    
    try:
        with open("mi_cv.pdf", "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
        st.download_button(
            label="📄 Descargar mi CV Completo",
            data=pdf_bytes,
            file_name="CV_Oscar_Chuquihuamani.pdf",
            mime="application/pdf"
        )
    except FileNotFoundError:
        st.warning("⚠️ No se encontró el archivo 'mi_cv'.")

st.divider()

# --- 2. FORMACIÓN ACADÉMICA ---
st.header("📚 Formación Académica", anchor="formacion-academica")

col_edu1, col_edu2 = st.columns([4, 1])

with col_edu1:
    st.subheader("Universidad Nacional del Callao")
    st.write("**Economía** | *2021 - Actualidad*")
    st.write("- Perteneciente al Tercio Superior.")
    st.write("Durante mi formación académica he desarrollado una sólida base en el análisis del mercado bursátil y la investigación econométrica aplicada. Mis estudios me han permitido dominar la evaluación de la salud financiera de las corporaciones e interpretar normativas complejas, como las directrices de la OCDE para la tributación internacional, aportando rigor cuantitativo a la resolución de problemas económicos reales.")

with col_edu2:
    try:
        st.image("logo_unac.png", use_container_width=True)
    except FileNotFoundError:
        st.info("Logo UNAC (logo_unac.png)")

st.divider()

# --- 3. EXPERIENCIA PROFESIONAL ---
st.header("💼 Experiencia Profesional", anchor="experiencia-profesional")

# EY PERÚ
col_ey_logo, col_ey_text = st.columns([1, 6]) 
with col_ey_logo:
    try:
        st.image("logo_ey.png", use_container_width=True)
    except FileNotFoundError:
        st.info("Logo EY")
with col_ey_text:
    st.subheader("EY Perú (Ernst & Young) - Firma global “big four”")
    st.write("**Asistente Junior del Área de Precios de Transferencia** | *05/2026 - Actualidad*")
    st.write("- Desarrollo profesional e integración en la línea de consultoría fiscal de una de las firmas globales líderes del sector.")
    st.write("- Análisis cuantitativo de la salud financiera, márgenes operativos y rentabilidad de empresas para verificar la consistencia de sus datos frente a comparables del mercado.")
    st.write("- Participación activa en el análisis de funciones, activos y evaluación de riesgos operativos de grandes corporaciones para asegurar el cumplimiento normativo internacional (OCDE).")
    st.write("- Estructuración de reportes cruzando información financiera. Identificación, corrección y validación de discrepancias de cálculo entre grandes volúmenes de datos.")
    st.write("- Optimización en procesos de recopilación y análisis de datos con programas como Python y Power BI.")

# TESIS MOTIVACIÓN
col_tm_logo, col_tm_text = st.columns([1, 6])
with col_tm_logo:
    try:
        st.image("logo_tm.png", use_container_width=True)
    except FileNotFoundError:
        st.info("Logo TM")
with col_tm_text:
    st.subheader("Tesis Motivación - TM Consultores S.A.C.")
    st.write("**Investigador Principal** | *10/2025 - 02/2026*")
    st.write("- Elaboración de proyectos de investigación a nivel pregrado y postgrado, bajo los lineamientos técnicos y metodológicos de cada universidad.")
    st.write("- Atención directa con los clientes y capacitación.")
    st.write("- Investigador principal de la cartera de ciencias empresariales (economía, administración y contabilidad).")
    st.write("- Análisis, extracción y limpieza de bases de datos.")

# BANCO RIPLEY
col_rip_logo, col_rip_text = st.columns([1, 6])
with col_rip_logo:
    try:
        st.image("logo_ripley.png", use_container_width=True)
    except FileNotFoundError:
        st.info("Logo Ripley")
with col_rip_text:
    st.subheader("Banco Ripley S.A.")
    st.write("**Cajero Bancario** | *02/2025 - 06/2025*")
    st.write("- Gestión de operaciones financieras con alto nivel de precisión y atención directa al cliente.")

st.divider()

# --- 4. COMPETENCIAS Y FORTALEZAS ---
st.header("🛠️ Competencias y Fortalezas", anchor="competencias")

col_hab1, col_hab2, col_hab3 = st.columns(3)

with col_hab1:
    st.subheader("Análisis de Datos")
    st.write("- Python (Intermedio)")
    st.write("- Excel (Avanzado)")
    st.write("- Power BI (Intermedio)")
    st.write("- SQL (Intermedio)")

with col_hab2:
    st.subheader("Econometría")
    st.write("- EViews (Avanzado)")
    st.write("- Stata (Intermedio)")
    st.write("- SPSS (Intermedio)")

with col_hab3:
    st.subheader("Idiomas y Soft Skills")
    st.write("- **Idiomas:** Español (Nativo), Inglés, Francés.")
    st.write("- Pensamiento analítico.")
    st.write("- Resolución de problemas complejos.")

st.divider()

# --- 5. EXPERIENCIA EN PROYECTOS ---
st.header("📊 Proyectos de Análisis de Datos", anchor="proyectos")

# Contenedor de la Tarjeta del Proyecto
with st.container():
    # Creamos dos columnas: una para la imagen de portada y otra para la descripción
    col_proj1, col_proj2 = st.columns([1, 2.5])
    
    with col_proj1:
        # Aquí irá una imagen de portada de tu proyecto
        try:
            st.image("app_bvl.jpg", use_container_width=True)
        except FileNotFoundError:
            st.info("📸 Sube una captura de tu app y llámala 'app_bvl.jpg'")
            
    with col_proj2:
        st.subheader("Extractor Automático de Cotizaciones - BVL")
        st.write("Desarrollo de una aplicación de escritorio con **Python (Tkinter y YFinance)**. Esta herramienta automatiza la descarga de series de tiempo históricas de la Bolsa de Valores de Lima (BVL) y exporta los datos estructurados a Excel, optimizando el flujo de trabajo para su posterior modelado econométrico en software especializado como EViews o SPSS.")
        
        # El botón mágico que despliega el contenido
        with st.expander("🔍 Abrir detalles, código y resultados del proyecto"):
            
            # Sub-menú de pestañas dentro del proyecto
            tab1, tab2, tab3 = st.tabs(["💻 Código Script", "📸 Interfaz Gráfica", "📊 Excel Resultante"])
            
            with tab1:
                st.write("Script de extracción financiera:")
                # Aquí pegamos tu código exacto para que se vea con formato de programación
                st.code('''import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import pandas as pd
import os

# ==========================================
# 1. Variable, archivo y ruta
# ==========================================
def descargar_historico():
    Ticker = entrada_ticker.get().upper().strip() 
    Desde_la_fecha = entrada_inicio.get()
    Hasta_la_fecha = entrada_fin.get()
    
    if not Ticker or not Desde_la_fecha or not Hasta_la_fecha:
        messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")
        return

    boton_descargar.config(text="Descargando datos...", state="disabled")
    ventana.update()

    try:
        datos_empresa = yf.download(Ticker, start=Desde_la_fecha, end=Hasta_la_fecha)

        if datos_empresa.empty:
            messagebox.showerror("Error", "No se encontraron datos. Verifica el Ticker o las fechas.")
        else:
            carpeta_destino = r"C:\\Users\\HP\\Desktop\\ProyectosDePython\\aplicativo_bvl"
            
            if not os.path.exists(carpeta_destino):
                os.makedirs(carpeta_destino)
            
            ticker_limpio = Ticker.replace('.LM', '')
            nombre_archivo = f"Historico_{ticker_limpio}_{Desde_la_fecha}_al_{Hasta_la_fecha}.xlsx"
            ruta_completa = os.path.join(carpeta_destino, nombre_archivo)
            
            datos_empresa.to_excel(ruta_completa)
            messagebox.showinfo("¡Éxito!", f"La serie de tiempo se ha guardado en:\\n{ruta_completa}")
            
    except Exception as e:
        messagebox.showerror("Error del sistema", f"Ocurrió un problema: {e}")
        
    finally:
        boton_descargar.config(text="Descargar Histórico", state="normal")

# ==========================================
# 2. Dinseño de ventana flotante del script
# ==========================================
ventana = tk.Tk()
ventana.title("Extractor de Cotizaciones - BVL")
ventana.geometry("420x250")
ventana.configure(padx=20, pady=20)

tk.Label(ventana, text="Ingresa los parámetros de tu análisis:", font=("Arial", 11, "bold")).pack(pady=(0, 15))

marco_ticker = tk.Frame(ventana)
marco_ticker.pack(fill="x", pady=5)
tk.Label(marco_ticker, text="Ticker (Ej: ALICORC1.LM):", width=22, anchor="w").pack(side="left")
entrada_ticker = tk.Entry(marco_ticker)
entrada_ticker.pack(side="left", expand=True, fill="x")

marco_inicio = tk.Frame(ventana)
marco_inicio.pack(fill="x", pady=5)
tk.Label(marco_inicio, text="Desde (YYYY-MM-DD):", width=22, anchor="w").pack(side="left")
entrada_inicio = tk.Entry(marco_inicio)
entrada_inicio.insert(0, "2020-01-01")
entrada_inicio.pack(side="left", expand=True, fill="x")

marco_fin = tk.Frame(ventana)
marco_fin.pack(fill="x", pady=5)
tk.Label(marco_fin, text="Hasta (YYYY-MM-DD):", width=22, anchor="w").pack(side="left")
entrada_fin = tk.Entry(marco_fin)
entrada_fin.insert(0, "2023-12-31")
entrada_fin.pack(side="left", expand=True, fill="x")

boton_descargar = tk.Button(ventana, text="Descargar Histórico", bg="#0052cc", fg="white", font=("Arial", 10, "bold"), command=descargar_historico)
boton_descargar.pack(pady=20, fill="x")

ventana.mainloop()''', language='python')
                
            with tab2:
                st.write("Interfaz gráfica desarrollada con Tkinter:")
                try:
                    st.image("app_bvl.jpg", use_container_width=True)
                except FileNotFoundError:
                    st.info("📸 Sube una captura de tu app y llámala 'app_bvl.jpg'")
                    
            with tab3:
                st.write("Base de datos estructurada y lista para análisis:")
                try:
                    st.image("excel_bvl.jpg", use_container_width=True)
                except FileNotFoundError:
                    st.info("📸 Sube una captura del Excel generado y llámala 'excel_bvl.jpg'")

st.divider()

# --- 6. CONTÁCTAME ---
st.header("📬 Contáctame", anchor="contactame")

# Inyectamos la librería de FontAwesome para los íconos de redes y contacto
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">', unsafe_allow_html=True)

# Sección de datos en horizontal (row) y centrados
st.markdown("""
<div style="display: flex; flex-direction: row; justify-content: center; gap: 50px; flex-wrap: wrap; font-size: 18px; margin-top: 20px;">
<div style="display: flex; align-items: center; gap: 10px;">
<i class="fa-solid fa-phone" style="color: #25D366; font-size: 30px; width: 35px; text-align: center;"></i>
<span>+51 943 129 901</span>
</div>
<div style="display: flex; align-items: center; gap: 10px;">
<i class="fa-solid fa-envelope" style="color: #EA4335; font-size: 30px; width: 35px; text-align: center;"></i>
<span>oscarjch_14@hotmail.com</span>
</div>
<div style="display: flex; align-items: center; gap: 10px;">
<i class="fa-brands fa-linkedin" style="color: #0A66C2; font-size: 35px; width: 35px; text-align: center;"></i>
<a href="https://www.linkedin.com/in/oscar-jesus-chuquihuamani-chavez-6bb8962a0" target="_blank" style="color: #E2C044; text-decoration: none; font-weight: 500;">
Mi Perfil de LinkedIn
</a>
</div>
</div>
""", unsafe_allow_html=True)