import streamlit as st

st.set_page_config(page_title="Portafolio | Oscar Chuquihuamani", layout="wide")

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (MENÚ) ---
st.sidebar.title("📌 Índice de Navegación")
st.sidebar.markdown("Haz clic en una sección para ir directamente:")
st.sidebar.markdown("- [1. Perfil Profesional](#perfil-profesional)")
st.sidebar.markdown("- [2. Formación Académica](#formacion-academica)")
st.sidebar.markdown("- [3. Experiencia Profesional](#experiencia-profesional)")
st.sidebar.markdown("- [4. Competencias y Fortalezas](#competencias)")
st.sidebar.markdown("- [5. Proyectos](#proyectos)")

st.title("Mi Portafolio Profesional")
st.divider()

# --- 1. PERFIL PROFESIONAL ---
st.header("Perfil Profesional", anchor="perfil-profesional")

col1, col2 = st.columns([1, 3]) 

with col1:
    try:
        st.image("foto.jpeg", use_container_width=True)
    except FileNotFoundError:
        st.info("Sube tu foto a la carpeta.")

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
st.info("🚧 Sección en construcción: Próximamente subiré los detalles de mis proyectos, bases de datos y análisis econométricos interactivos.")