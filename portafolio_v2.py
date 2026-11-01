import base64
import os
import random

import streamlit as st

st.set_page_config(
    page_title="Portafolio | Oscar Chuquihuamani",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =====================================================================
# 0. TEMAS (aquí cambias o agregas colores fácilmente)
#    Colores tomados de tu imagen de referencia (temas 3 y 6)
# =====================================================================
TEMAS = {
    "verde": {
        "bg": "#0A0F0A",
        "panel": "#0E1A12",
        "accent": "#22C55E",
        "accent2": "#A3E635",
        "text": "#E2E8F0",
    },
    "azul": {
        "bg": "#050816",
        "panel": "#0A1428",
        "accent": "#0EA5E9",
        "accent2": "#38BDF8",
        "text": "#E2E8F0",
    },
}

# El tema viaja en la URL (?tema=azul). Los puntos de la barra superior son enlaces.
tema_url = st.query_params.get("tema", "verde")
tema_id = tema_url if tema_url in TEMAS else "verde"
T = TEMAS[tema_id]

# Páginas: "inicio" (hero + sobre mí + formación + experiencia) y "proyectos"
pagina = st.query_params.get("pagina", "inicio")
if pagina not in ("inicio", "proyectos"):
    pagina = "inicio"


def url(pag, ancla="", tema=None):
    """Enlace interno que conserva tema y página. Se usa en TODOS los enlaces."""
    u = f"?tema={tema or tema_id}&amp;pagina={pag}"
    return u + (f"#{ancla}" if ancla else "")

# =====================================================================
# 1. HELPERS: imagen incrustada y gráfico de velas generado por código
# =====================================================================
def img_a_base64(*rutas):
    """Devuelve un data-URI con la primera imagen que exista (o None)."""
    for ruta in rutas:
        if os.path.exists(ruta):
            ext = os.path.splitext(ruta)[1].lower().replace(".", "")
            mime = {"png": "png", "webp": "webp"}.get(ext, "jpeg")
            with open(ruta, "rb") as f:
                datos = base64.b64encode(f.read()).decode()
            return f"data:image/{mime};base64,{datos}"
    return None


@st.cache_data(show_spinner=False)
def cv_data_uri(ruta="mi_cv.pdf"):
    """El CV como enlace de descarga directa (para el botón de la barra superior).
    Si el archivo no existe o pesa mucho, devuelve None y el botón lleva a la sección Sobre mí."""
    if os.path.exists(ruta) and os.path.getsize(ruta) < 4_000_000:
        with open(ruta, "rb") as f:
            return "data:application/pdf;base64," + base64.b64encode(f.read()).decode()
    return None


def curva(pts):
    """Curva suave (Catmull-Rom -> Bézier) que pasa por todos los puntos."""
    d = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for i in range(len(pts) - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}")
    return " ".join(d)


def velas_svg(n=48, seed=11, w=1200, h=480, margen=5):
    """Gráfico de velas japonesas 100% generado por código.
    Es ancho (1200x480) para que sirva de FONDO de toda la sección hero.
    Usa var(--accent), así cambia de color solo con el tema.
    Dibuja dos líneas envolventes: una por ENCIMA y otra por DEBAJO de las velas,
    siguiendo su recorrido pero sin tocarlas (margen en unidades de precio)."""
    rnd = random.Random(seed)
    precio = 100.0
    velas = []
    for _ in range(n):
        o = precio
        c = o + rnd.uniform(-9, 11) + 1.6  # tendencia alcista
        hi = max(o, c) + rnd.uniform(1, 6)
        lo = min(o, c) - rnd.uniform(1, 6)
        velas.append((o, hi, lo, c))
        precio = c
    vmin = min(v[2] for v in velas)
    vmax = max(v[1] for v in velas)

    # Envolventes: máximo/mínimo móvil (ventana ±4) + margen, suavizado (ventana ±2).
    # Con esas ventanas, la línea siempre queda al menos "margen" por fuera de cada vela cercana.
    def movil(xs, f, r):
        return [f(xs[max(0, i - r): i + r + 1]) for i in range(len(xs))]

    def promedio(xs, r):
        out = []
        for i in range(len(xs)):
            t = xs[max(0, i - r): i + r + 1]
            out.append(sum(t) / len(t))
        return out

    sup = promedio([m + margen for m in movil([v[1] for v in velas], max, 4)], 2)
    inf = promedio([m - margen for m in movil([v[2] for v in velas], min, 4)], 2)

    def y(v):
        return h - 40 - (v - vmin) / (vmax - vmin) * (h - 100)

    paso = w / n
    partes = [f'<svg class="velas" viewBox="0 0 {w} {h}" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">']
    for k in range(1, 6):  # rejilla horizontal
        yy = k * h / 6
        partes.append(f'<line x1="0" x2="{w}" y1="{yy:.0f}" y2="{yy:.0f}" stroke="var(--accent)" stroke-opacity="0.10"/>')
    puntos = []
    for i, (o, hi, lo, c) in enumerate(velas):
        x = i * paso + paso / 2
        sube = c >= o
        relleno = "var(--accent)" if sube else "none"
        op = "0.75" if sube else "1"
        delay = f"{i * 0.04:.2f}s"
        partes.append(
            f'<g class="vela" style="animation-delay:{delay}">'
            f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{y(hi):.1f}" y2="{y(lo):.1f}" stroke="var(--accent)" stroke-width="1.6" vector-effect="non-scaling-stroke"/>'
            f'<rect x="{x - paso * 0.3:.1f}" y="{min(y(o), y(c)):.1f}" width="{paso * 0.6:.1f}" '
            f'height="{max(abs(y(o) - y(c)), 2):.1f}" fill="{relleno}" fill-opacity="{op}" stroke="var(--accent)" stroke-width="1.4" vector-effect="non-scaling-stroke"/>'
            f"</g>"
        )
        puntos.append(f"{x:.1f},{y(c):.1f}")
    # Las líneas usan la clase "linea": se revelan de izquierda a derecha al mismo ritmo que las velas
    estilo = 'fill="none" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"'
    xs = [i * paso + paso / 2 for i in range(n)]
    partes.append(f'<polyline class="linea" points="{" ".join(puntos)}" stroke="var(--accent)" stroke-width="1.4" stroke-opacity="0.5" {estilo}/>')
    partes.append(f'<path class="linea" d="{curva([(x, y(v)) for x, v in zip(xs, sup)])}" stroke="var(--accent2)" stroke-width="2.2" stroke-opacity="0.9" {estilo}/>')
    partes.append(f'<path class="linea" d="{curva([(x, y(v)) for x, v in zip(xs, inf)])}" stroke="var(--accent2)" stroke-width="2.2" stroke-opacity="0.9" {estilo}/>')
    partes.append("</svg>")
    return "".join(partes)


# =====================================================================
# 2. CSS (variables según el tema + estilos estáticos)
# =====================================================================
st.markdown(
    f"""<style>
:root {{
  --bg: {T['bg']}; --panel: {T['panel']}; --accent: {T['accent']};
  --accent2: {T['accent2']}; --text: {T['text']};
}}
</style>""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
.stApp { background: radial-gradient(1200px 600px at 80% -10%, color-mix(in srgb, var(--accent) 14%, transparent), transparent), var(--bg) !important; }
.stApp, .stApp p, .stApp li, .stApp label { color: var(--text) !important; }
h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
h2 { border-left: 4px solid var(--accent); padding-left: 12px !important; }
hr { border-color: color-mix(in srgb, var(--accent) 25%, transparent) !important; }

/* Ocultar barra lateral y cabecera de Streamlit (ya no usamos índice lateral) */
[data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"],
header[data-testid="stHeader"] { display: none !important; }
.block-container { max-width: 1700px; padding: 4.9rem max(4vw, 76px) 1rem !important; overflow-x: hidden; }

/* Quitar el hueco que Streamlit deja por los bloques <style> y por la barra fija
   (cada st.markdown ocupa una fila con separación aunque no se vea) */
[data-testid="stElementContainer"]:has(style), .element-container:has(style) { display: none !important; }
[data-testid="stElementContainer"]:has(.nav), .element-container:has(.nav) { height: 0 !important; min-height: 0 !important; margin-bottom: -1rem !important; overflow: visible !important; }

/* Scroll suave y margen para que la barra fija no tape los títulos */
[data-testid="stMain"], section.main { scroll-behavior: smooth; }
h1, h2, h3, [id] { scroll-margin-top: 90px; }

/* ================= BARRA SUPERIOR ================= */
.nav { position: fixed; top: 0; left: 0; right: 0; z-index: 1000; height: 64px;
  display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 0 4vw;
  /* barra teñida con el color del tema (antes era casi negra) */
  background: color-mix(in srgb, var(--accent) 14%, var(--bg)); backdrop-filter: blur(10px);
  border-bottom: 1px solid color-mix(in srgb, var(--accent) 55%, transparent);
  box-shadow: 0 4px 24px color-mix(in srgb, var(--accent) 22%, transparent); }
.nav-logo { display: flex; align-items: center; gap: 12px; text-decoration: none !important; }
.nav-logo svg { width: 46px; height: 38px; filter: drop-shadow(0 0 6px var(--accent)); }
.nav-logo .txt { display: flex; flex-direction: column; line-height: 1.1; }
.nav-logo b { color: #fff; font-size: 1.15rem; letter-spacing: .08em; }
.nav-logo small { color: var(--accent); font-size: .6rem; letter-spacing: .2em; }
.nav-links { display: flex; gap: 28px; margin: 0 auto 0 3vw; }
.nav-links a { color: var(--text) !important; text-decoration: none !important; font-size: .95rem; font-weight: 500; transition: .2s; }
.nav-links a.activo { color: var(--accent) !important; }
.nav-links a:hover { color: var(--accent) !important; text-shadow: 0 0 12px var(--accent); }
/* Botón Descargar CV (arriba a la derecha), del color del tema */
.nav-cv { background: var(--accent); color: #04110a !important; font-weight: 700; font-size: .92rem; padding: 9px 22px;
  border-radius: 999px; text-decoration: none !important; white-space: nowrap; transition: .25s;
  box-shadow: 0 0 18px color-mix(in srgb, var(--accent) 55%, transparent); }
.nav-cv:hover { filter: brightness(1.15); transform: translateY(-1px); }

/* Selector de tema: cápsula fija en el costado derecho, a media altura */
.tema-pill { position: fixed; z-index: 1001; right: 22px; top: 50%; transform: translateY(-50%);
  display: flex; flex-direction: column; gap: 10px; padding: 8px; border-radius: 999px;
  background: color-mix(in srgb, var(--bg) 82%, transparent); backdrop-filter: blur(8px);
  border: 1px solid color-mix(in srgb, var(--accent) 40%, transparent);
  box-shadow: 0 0 22px color-mix(in srgb, var(--accent) 25%, transparent); }
.dot { width: 30px; height: 30px; border-radius: 50%; display: block; text-decoration: none !important; transition: .2s; }
.dot:hover { transform: scale(1.12); }
.dot-verde { background: linear-gradient(135deg, #22C55E, #A3E635); }
.dot-azul  { background: linear-gradient(135deg, #0EA5E9, #38BDF8); }
.dot.activo { outline: 2px solid #fff; outline-offset: 2px; }

/* Imágenes con borde neón sutil */
[data-testid="stImage"] img { border-radius: 12px; }

/* Botón de descarga con el color del tema */
[data-testid="stDownloadButton"] button {
  background: var(--accent) !important; color: #04110a !important; border: none !important;
  font-weight: 700 !important; transition: .3s; box-shadow: 0 0 18px color-mix(in srgb, var(--accent) 50%, transparent);
}
[data-testid="stDownloadButton"] button:hover { filter: brightness(1.15); transform: translateY(-1px); }
[data-testid="stDownloadButton"] button p { color: #04110a !important; }

/* Tarjetas de proyecto (expander) */
[data-testid="stExpander"] { border: 1px solid color-mix(in srgb, var(--accent) 40%, transparent) !important; border-radius: 12px; background: var(--panel); }

/* ================= HERO ================= */
/* Toda la sección es el escenario: las velas son el FONDO y la foto va encima, más pequeña */
.hero { position: relative; display: flex; justify-content: space-between; align-items: stretch; gap: 20px;
  /* el alto se adapta a la pantalla: así caben el cuadro principal y las 3 tarjetas sin hacer scroll */
  height: clamp(430px, calc(100vh - 190px), 680px); padding: 40px 64px 0; border-radius: 22px; overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--accent) 45%, transparent);
  background: linear-gradient(160deg, var(--panel), var(--bg));
  box-shadow: 0 0 40px color-mix(in srgb, var(--accent) 18%, transparent) inset, 0 0 30px color-mix(in srgb, var(--accent) 14%, transparent); }
.velas { position: absolute; inset: 0; width: 100%; height: 100%; opacity: .55; z-index: 0;
  /* se desvanece a la izquierda para que el texto se lea bien */
  -webkit-mask-image: linear-gradient(90deg, transparent 5%, rgba(0,0,0,.35) 40%, #000 70%);
  mask-image: linear-gradient(90deg, transparent 5%, rgba(0,0,0,.35) 40%, #000 70%); }
.vela { transform-box: fill-box; transform-origin: bottom; animation: crecer .7s ease-out both; }
@keyframes crecer { from { transform: scaleY(0); opacity: 0; } to { transform: scaleY(1); opacity: 1; } }

.hero-text { position: relative; z-index: 2; flex: 1 1 420px; align-self: center; padding-bottom: 40px; }
.kicker { color: var(--accent); letter-spacing: .25em; font-size: .85rem; font-weight: 700; margin-bottom: 10px; }
.hero-title { font-size: 4rem; font-weight: 900; line-height: 1.1; color: #fff; margin-bottom: 14px; }
.hero-title span {
  background: linear-gradient(90deg, var(--accent), var(--accent2), var(--accent));
  background-size: 300%; -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; animation: brillar 6s linear infinite;
}
@keyframes brillar { 0% { background-position: 0% 50%; } 100% { background-position: 300% 50%; } }
.hero-sub { font-size: 1.15rem; line-height: 1.6; max-width: 620px; opacity: .9; }
.typing { display: inline-block; max-width: 100%; margin: 6px 0 18px; }
.typing div {
  color: var(--accent2); font-family: 'Courier New', monospace; font-size: 1.5rem; font-weight: 600;
  overflow: hidden; white-space: nowrap; border-right: .15em solid var(--accent2);
  animation: teclear 4.5s steps(40, end) infinite alternate, parpadear .8s step-end infinite;
}
@keyframes teclear { from { width: 0; } to { width: 40ch; } }
@keyframes parpadear { from, to { border-color: transparent; } 50% { border-color: var(--accent2); } }
.hero-btns { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 22px; }
.btn { padding: 11px 24px; border-radius: 999px; font-weight: 700; text-decoration: none !important; transition: .25s; }
.btn-solid { background: var(--accent); color: #04110a !important; box-shadow: 0 0 22px color-mix(in srgb, var(--accent) 60%, transparent); }
.btn-solid:hover { transform: translateY(-2px); filter: brightness(1.15); }
.btn-ghost { border: 1.5px solid var(--accent); color: var(--accent) !important; }
.btn-ghost:hover { background: color-mix(in srgb, var(--accent) 18%, transparent); }

/* Foto: más pequeña, pegada al borde inferior, con resplandor neón */
.hero-photo { position: relative; z-index: 2; flex: 0 0 400px; height: calc(100% - 95px); max-height: 530px; align-self: flex-end;
  margin-right: clamp(150px, 13vw, 260px); }
.glow { position: absolute; left: 50%; top: 55%; width: 120%; height: 80%; transform: translate(-50%, -50%);
  background: radial-gradient(circle, color-mix(in srgb, var(--accent) 35%, transparent), transparent 65%); filter: blur(24px); }
.persona { position: absolute; left: 50%; bottom: 0; height: 100%; transform: translateX(-50%);
  /* contorno neón: drop-shadow sigue la silueta de la persona */
  filter: drop-shadow(0 0 2px var(--accent)) drop-shadow(0 0 6px var(--accent)) drop-shadow(0 0 16px var(--accent)); }
.badge { position: absolute; z-index: 3; right: 28px; top: 50%; transform: translateY(-50%); color: #fff;
  padding: 14px 18px; border-radius: 14px; font-size: .88rem; line-height: 1.75; white-space: nowrap;
  background: color-mix(in srgb, var(--bg) 80%, transparent); border: 1px solid color-mix(in srgb, var(--accent) 50%, transparent); backdrop-filter: blur(6px); }
.badge b { color: var(--accent); }
.badge .t { display: block; font-weight: 800; font-size: 1.02rem; letter-spacing: .02em; margin-bottom: 2px; }

/* Tarjetas "Explora mis áreas" */
.areas { display: flex; flex-wrap: wrap; gap: 14px; margin: 16px 0 0; }
.area { flex: 1 1 200px; padding: 14px 18px; border-radius: 14px; background: var(--panel);
  border: 1px solid color-mix(in srgb, var(--accent) 35%, transparent); text-decoration: none !important; transition: .25s; }
.area:hover { transform: translateY(-3px); border-color: var(--accent); box-shadow: 0 0 20px color-mix(in srgb, var(--accent) 35%, transparent); }
.area b { color: #fff; display: block; } .area small { opacity: .75; }

/* Las líneas (cierre, MM30, MM50) se dibujan de izquierda a derecha junto con las velas */
.linea { animation: revelar 1.9s linear .35s both; }
@keyframes revelar {
  from { clip-path: inset(-20px 100% -20px 0); }
  to   { clip-path: inset(-20px -20px -20px 0); }
}

/* Iconos de contacto dentro del cuadro principal (solo iconos, sin números) */
.hero-contacto { display: flex; gap: 12px; margin-top: 20px; }
.hero-contacto a { width: 42px; height: 42px; border-radius: 50%; display: grid; place-items: center; transition: .25s;
  color: var(--accent) !important; text-decoration: none !important;
  border: 1.5px solid color-mix(in srgb, var(--accent) 60%, transparent);
  background: color-mix(in srgb, var(--accent) 8%, transparent); }
.hero-contacto a:hover { background: var(--accent); color: #04110a !important; transform: translateY(-2px);
  box-shadow: 0 0 18px color-mix(in srgb, var(--accent) 55%, transparent); }
.hero-contacto svg { width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }

/* Pantallas medianas: sin cuadro lateral para que no se apriete el texto */
@media (min-width: 769px) and (max-width: 1150px) {
  .badge { display: none; }
  .hero-photo { margin-right: 0; flex-basis: 340px; }
}


/* Pantallas bajas (laptops): letra un poco más compacta para que todo quepa sin scroll */
@media (min-width: 769px) and (max-height: 760px) {
  .hero-title { font-size: 3.3rem; margin-bottom: 8px; }
  .typing { margin: 2px 0 10px; }
  .typing div { font-size: 1.25rem; }
  .hero-sub { font-size: 1.02rem; }
  .hero-btns { margin-top: 14px; }
  .hero-contacto { margin-top: 12px; }
}

/* ================= MÓVIL ================= */
@media (max-width: 768px) {
  .nav { padding: 0 14px; gap: 10px; }
  .nav-logo small { display: none; }
  .nav-links { gap: 14px; }
  .nav-links a { font-size: .78rem; }
  .hero { flex-direction: column; padding: 28px 20px 0; height: auto; }
  .block-container { padding-left: 14px !important; padding-right: 14px !important; }
  .nav-cv { display: none; }
  .nav-links { margin: 0 0 0 auto; }
  .tema-pill { top: auto; bottom: 16px; right: 14px; transform: none; flex-direction: row; }
  .hero-photo { margin-right: 0; }
  .badge { position: relative; right: auto; top: auto; transform: none; align-self: center; margin: 14px 0 20px; }
  .hero-photo { flex: none; width: 100%; height: 300px; }
  .hero-title { font-size: 2.2rem; }
  .typing div { font-size: .9rem; }
  .hero { padding: 28px 20px 0; min-height: 0; }
}
@media (max-width: 480px) {
  .hero-title { font-size: 1.8rem; }
  .typing div { font-size: .7rem; }
  .nav-logo b { font-size: .9rem; }
}
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================================
# 3. BARRA SUPERIOR (Inicio · Sobre mí · Experiencia profesional · Proyectos + puntos de tema)
# =====================================================================
def clase_dot(t):
    return "dot dot-" + t + (" activo" if t == tema_id else "")


# Logo "OS": la O usa --accent y la S usa --accent2, así cambia con el tema
LOGO_SVG = (
    '<svg viewBox="0 0 48 40" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<ellipse cx="16" cy="20" rx="11.5" ry="14.5" fill="none" stroke="var(--accent)" stroke-width="3.4"/>'
    '<path d="M43 10.5C39 6 28 6.5 28 14C28 20.5 41 19.5 41 26.5C41 34 30 34 25.5 29.5" fill="none" '
    'stroke="var(--accent2)" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)

act_inicio = " activo" if pagina == "inicio" else ""
act_proy = " activo" if pagina == "proyectos" else ""

cv_uri = cv_data_uri()
if cv_uri:
    boton_cv = f'<a class="nav-cv" href="{cv_uri}" download="CV_Oscar_Chuquihuamani.pdf">Descargar CV ↗</a>'
else:  # sin mi_cv.pdf: lleva a la sección Sobre mí
    boton_cv = f'<a class="nav-cv" href="{url("inicio", "perfil-profesional")}" target="_self">Descargar CV ↗</a>'

nav_html = (
    '<div class="nav">'
    f'<a class="nav-logo" href="{url("inicio", "inicio")}" target="_self">{LOGO_SVG}'
    '<span class="txt"><b>OSCAR</b><small>ECONOMÍA &amp; DATA</small></span></a>'
    '<div class="nav-links">'
    f'<a class="{act_inicio.strip()}" href="{url("inicio", "inicio")}" target="_self">Inicio</a>'
    f'<a href="{url("inicio", "perfil-profesional")}" target="_self">Sobre mí</a>'
    f'<a href="{url("inicio", "experiencia-profesional")}" target="_self">Experiencia profesional</a>'
    f'<a class="{act_proy.strip()}" href="{url("proyectos", "proyectos")}" target="_self">Proyectos</a>'
    "</div>"
    + boton_cv
    + "</div>"
    # selector de tema: hermano de .nav (no hijo) para que quede fijo en el costado
    '<div class="tema-pill">'
    f'<a class="{clase_dot("verde")}" href="{url(pagina, "", "verde")}" target="_self" title="Verde neón"></a>'
    f'<a class="{clase_dot("azul")}" href="{url(pagina, "", "azul")}" target="_self" title="Azul noche"></a>'
    "</div>"
)
st.markdown(nav_html, unsafe_allow_html=True)

CODIGO_BVL = '''import tkinter as tk
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

ventana.mainloop()'''


if pagina == "inicio":
    # =====================================================================
    # 4. HERO (velas de fondo + foto más pequeña con contorno neón)
    # =====================================================================
    URL_PROY = url("proyectos", "proyectos")
    URL_PERFIL = url("inicio", "perfil-profesional")
    URL_EXP = url("inicio", "experiencia-profesional")

    # Iconos de contacto (solo iconos; los datos van dentro del enlace, no visibles)
    TELEFONO, CORREO = "51943129901", "oscarjch_14@hotmail.com"
    LINKEDIN = "https://www.linkedin.com/in/oscar-jesus-chuquihuamani-chavez-6bb8962a0"
    CONTACTO_HTML = (
        '<div class="hero-contacto">'
        f'<a href="tel:+{TELEFONO}" title="Llamar">'
        '<svg viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg></a>'
        f'<a href="https://wa.me/{TELEFONO}" target="_blank" rel="noopener" title="WhatsApp">'
        '<svg viewBox="0 0 24 24"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg></a>'
        f'<a href="mailto:{CORREO}" title="Correo">'
        '<svg viewBox="0 0 24 24"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg></a>'
        f'<a href="{LINKEDIN}" target="_blank" rel="noopener" title="LinkedIn">'
        '<svg viewBox="0 0 24 24"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg></a>'
        "</div>"
    )

    foto = img_a_base64("foto_hero.png", "foto_hero.webp")  # PNG transparente
    if foto:
        persona_html = f'<img class="persona" src="{foto}" alt="Oscar Chuquihuamani">'
    else:
        persona_html = '<div style="position:absolute;inset:0;display:grid;place-items:center;text-align:center;padding:20px;">Genera "foto_hero.png" con quitar_fondo.py</div>'

    hero_html = (
        '<div id="inicio" class="hero">'
        + velas_svg()
        + '<div class="hero-text">'
        '<div class="kicker">ECONOMÍA · FINANZAS · DATOS</div>'
        '<div class="hero-title">Analizando datos.<br><span>Entendiendo la economía.</span></div>'
        '<div class="typing"><div>¡Hola, soy Oscar, y bienvenido!</div></div>'
        '<p class="hero-sub">Economista con enfoque en finanzas corporativas, análisis de datos y gestión de riesgos. '
        "Convierto la información en decisiones.</p>"
        '<div class="hero-btns">'
        f'<a class="btn btn-solid" href="{URL_PROY}" target="_self">Explorar proyectos →</a>'
        f'<a class="btn btn-ghost" href="{URL_PERFIL}" target="_self">Descargar CV ↓</a>'
        "</div>"
        + CONTACTO_HTML
        + "</div>"
        '<div class="hero-photo"><div class="glow"></div>'
        + persona_html
        + "</div>"
        '<div class="badge"><span class="t">Economista</span><b>UNAC</b> · Tercio Superior<br><b>Big Four</b> · EY Perú<br><b>Finanzas</b> · Valuación<br><b>Python</b> · Power BI · SQL</div>'
        "</div>"
        '<div class="areas">'
        f'<a class="area" href="{URL_PERFIL}" target="_self"><b>👤 Sobre mí</b><small>Perfil y formación</small></a>'
        f'<a class="area" href="{URL_EXP}" target="_self"><b>💼 Experiencia</b><small>Mi trayectoria profesional</small></a>'
        f'<a class="area" href="{URL_PROY}" target="_self"><b>📊 Proyectos</b><small>Análisis, dashboards y más</small></a>'
        "</div>"
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    st.divider()

    st.divider()

    # =====================================================================
    # 5. PERFIL PROFESIONAL
    # =====================================================================
    st.header("Perfil Profesional", anchor="perfil-profesional")

    col1, col2 = st.columns([1, 3])

    with col1:
        try:
            st.image("foto.png", use_container_width=True)
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
                mime="application/pdf",
            )
        except FileNotFoundError:
            st.warning("⚠️ No se encontró el archivo 'mi_cv'.")

    st.divider()

    # =====================================================================
    # 6. FORMACIÓN ACADÉMICA
    # =====================================================================
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

    # =====================================================================
    # 7. EXPERIENCIA PROFESIONAL
    # =====================================================================
    st.header("💼 Experiencia Profesional", anchor="experiencia-profesional")

    col_ey_logo, col_ey_text = st.columns([1, 6])
    with col_ey_logo:
        try:
            st.image("logo_ey.png", use_container_width=True)
        except FileNotFoundError:
            st.info("Logo EY")
    with col_ey_text:
        st.subheader("EY Perú (Ernst & Young) - Firma global “big four”")
        st.write("**Asistente Junior del Área de Precios de Transferencia** | *05/2026 - 31/10/2026*")
        st.write("- Desarrollo profesional en la línea de consultoría fiscal de una de las firmas globales líderes del sector.")
        st.write("- Análisis cuantitativo de la salud financiera, márgenes operativos y rentabilidad de empresas para verificar la consistencia de sus datos frente a comparables del mercado.")
        st.write("- Participación activa en el análisis de funciones, activos y evaluación de riesgos operativos de grandes corporaciones para asegurar el cumplimiento normativo internacional (OCDE).")
        st.write("- Estructuración de reportes cruzando información financiera. Identificación, corrección y validación de discrepancias de cálculo entre grandes volúmenes de datos.")
        st.write("- Soporte y participación en la elaboración de informes de Valuaciones de activos.")
        st.write("- LOGROS: Optimización en procesos de recopilación y análisis de Big data de páginas públicas como la SBS, SMV, SEC Edgar, entre otros, empleando programas como Python y Power BI.")

    st.divider()

    # =====================================================================
    # 8. COMPETENCIAS Y FORTALEZAS
    # =====================================================================
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


else:  # pagina == "proyectos"
    # =====================================================================
    # 9. PROYECTOS
    # =====================================================================
    st.header("📊 Proyectos de Análisis de Datos", anchor="proyectos")

    with st.container():
        col_proj1, col_proj2 = st.columns([1, 2.5])

        with col_proj1:
            try:
                st.image("app_bvl.jpg", use_container_width=True)
            except FileNotFoundError:
                st.info("📸 Sube una captura de tu app y llámala 'app_bvl.jpg'")

        with col_proj2:
            st.subheader("Extractor Automático de Cotizaciones - BVL")
            st.write("Desarrollo de una aplicación de escritorio con **Python (Tkinter y YFinance)**. Esta herramienta automatiza la descarga de series de tiempo históricas de la Bolsa de Valores de Lima (BVL) y exporta los datos estructurados a Excel, optimizando el flujo de trabajo para su posterior modelado econométrico en software especializado como EViews o SPSS.")

            with st.expander("🔍 Abrir detalles, código y resultados del proyecto"):
                tab1, tab2, tab3 = st.tabs(["💻 Código Script", "📸 Interfaz Gráfica", "📊 Excel Resultante"])

                with tab1:
                    st.write("Script de extracción financiera:")
                    st.code(CODIGO_BVL, language='python')

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

    st.markdown("<br><hr style='border-top: 1px dashed var(--accent); margin: 20px 0;'><br>", unsafe_allow_html=True)

    # --- VALORIZACIÓN DE ALICORP ---
    with st.container():
        col_ali1, col_ali2 = st.columns([1, 2.5])

        with col_ali1:
            try:
                st.image("portada_alicorp.jpg", use_container_width=True)
            except FileNotFoundError:
                st.info("📸 Sube una captura de la portada de tu informe y llámala 'portada_alicorp.jpg'")

        with col_ali2:
            st.subheader("Valorización Financiera de Alicorp S.A.A.")
            st.write("Informe detallado sobre la valoración corporativa de Alicorp. Este documento abarca el análisis de la salud financiera, proyección de flujos de caja y determinación del valor intrínseco de la compañía, aplicando metodologías rigurosas de finanzas corporativas para la toma de decisiones en el mercado bursátil.")

            nombre_archivo_pdf = "Informe de Valorización de Alicorp - Elaborado por Oscar Chuquihuamani.pdf"

            try:
                with open(nombre_archivo_pdf, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                st.download_button(
                    label="📄 Descargar Informe de Valorización (Solo lectura)",
                    data=pdf_bytes,
                    file_name="Valorizacion_Alicorp_Oscar_Chuquihuamani.pdf",
                    mime="application/pdf",
                    key="btn_descarga_alicorp",
                )
            except FileNotFoundError:
                st.warning(f"⚠️ No se encontró el archivo '{nombre_archivo_pdf}'. Verifica que el nombre sea exacto.")

    st.markdown("<br><hr style='border-top: 1px dashed var(--accent); margin: 20px 0;'><br>", unsafe_allow_html=True)

    # --- EXTRACTOR DE ESTADOS FINANCIEROS ---
    with st.container():
        col_eeff1, col_eeff2 = st.columns([1.2, 2])

        with col_eeff1:
            try:
                st.image("excel_estados_financieros.jpg", use_container_width=True, caption="Output automatizado de datos estructurados")
            except FileNotFoundError:
                st.info("📸 Sube la captura de cómo queda tu Excel y llámala 'excel_estados_financieros.jpg'")

        with col_eeff2:
            st.subheader("Extractor Automatizado de Estados Financieros")

            st.write("Desarrollo de un script diseñado para la extracción masiva y estructuración de Balances Generales y Estados de Resultados a partir de múltiples reportes financieros en PDF. Esta herramienta reduce drásticamente las horas-hombre de procesamiento manual, siendo un activo clave para agilizar el análisis fundamental, la construcción de modelos de valoración corporativa, estudios de empresas comparables y la evaluación de la salud financiera.")

            st.write("**Escalamiento del proyecto (Visión a futuro):**")
            st.write("Actualmente en proceso de integración con el motor de cotizaciones bursátiles para conformar un sistema integral de inteligencia financiera. Esto automatizará el cálculo de ratios financieros, KPIs sectoriales y la minería de datos cualitativos (composición accionaria, estructura corporativa y segmentación de ingresos).")

            st.info("🔒 **Confidencialidad:** El código fuente de este proyecto se mantiene en reserva debido a la sensibilidad de la información. Solo se mostrará en pantalla la estructura final de los datos procesados.")

    st.divider()


# =====================================================================
# 10. CONTÁCTAME
# =====================================================================
st.header("📬 Contáctame", anchor="contactame")

st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">', unsafe_allow_html=True)

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
<a href="https://www.linkedin.com/in/oscar-jesus-chuquihuamani-chavez-6bb8962a0" target="_blank" style="color: var(--accent2); text-decoration: none; font-weight: 500;">
Mi Perfil de LinkedIn
</a>
</div>
</div>
""", unsafe_allow_html=True)