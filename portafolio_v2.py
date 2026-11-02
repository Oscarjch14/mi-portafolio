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
.block-container { max-width: 1700px; padding: 4.9rem max(4vw, 76px) 7rem !important; overflow-x: clip; }

/* Quitar el hueco que Streamlit deja por los bloques <style> y por la barra fija
   (cada st.markdown ocupa una fila con separación aunque no se vea) */
[data-testid="stElementContainer"]:has(style), .element-container:has(style) { display: none !important; }
[data-testid="stElementContainer"]:has(.nav), .element-container:has(.nav) { height: 0 !important; min-height: 0 !important; margin-bottom: -1rem !important; overflow: visible !important; }

/* Scroll suave y margen para que la barra fija no tape los títulos */
[data-testid="stMain"], section.main { scroll-behavior: smooth; }
h1, h2, h3, [id] { scroll-margin-top: 90px; }

/* ================= APARECER AL HACER SCROLL =================
   Un pequeño script (al final del archivo) marca con .rv los bloques que aún están fuera de la
   pantalla y les pone .rv-in cuando aparecen al bajar. Aquí solo está el estilo del efecto. */
.rv { opacity: 0; transform: translateY(64px);
  transition: opacity .9s ease, transform .9s cubic-bezier(.2, .7, .2, 1); will-change: opacity, transform; }
.rv.rv-in { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) { .rv { opacity: 1; transform: none; transition: none; } }

/* El iframe invisible del script no debe dejar hueco */
[data-testid="stElementContainer"]:has(iframe[height="0"]), .element-container:has(iframe[height="0"]) {
  height: 0 !important; min-height: 0 !important; margin-bottom: -1rem !important; overflow: hidden !important; }

/* Más aire entre el título "Proyectos" y las tarjetas */
[data-testid="stElementContainer"]:has(#proyectos), .element-container:has(#proyectos) { margin-bottom: 2rem !important; }

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
        '<div class="kicker">ECONOMÍA - FINANZAS - DATOS</div>'
        '<div class="hero-title">Analizando datos<br><span>Que mueven la economía.</span></div>'
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
    # 5. SOBRE MÍ  (quién soy + formación + lo que me mueve + mi paso por EY)
    #    Reemplaza a las antiguas secciones "Perfil Profesional" y "Formación Académica".
    #    Imágenes que usa (si falta alguna, simplemente no se muestra):
    #    foto.png · logo_unac.png · logo_ey.png · foto_2.png
    # =====================================================================
    st.header("Sobre mí", anchor="perfil-profesional")

    def _img(ruta, clase, alt=""):
        d = img_a_base64(ruta)
        return f'<img class="{clase}" src="{d}" alt="{alt}">' if d else ""

    st.markdown(
        """
<style>
.sm-kicker { color: var(--accent); letter-spacing: .25em; font-size: .8rem; font-weight: 700; margin-bottom: 6px; }
.sm-hola { font-size: 2.4rem; font-weight: 800; color: #fff; line-height: 1.15; margin: 0 0 14px; }
.sm-hola span { background: linear-gradient(90deg, var(--accent), var(--accent2)); -webkit-background-clip: text;
  background-clip: text; -webkit-text-fill-color: transparent; }
.sm-lead { font-size: 1.12rem; line-height: 1.75; margin: 0 0 10px; }
.sm-label { color: var(--accent2); font-weight: 700; letter-spacing: .08em; font-size: .85rem; margin: 18px 0 6px; }
.sm-chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0; }
.sm-chip { padding: 6px 14px; border-radius: 999px; font-size: .85rem; color: var(--accent2);
  border: 1px solid color-mix(in srgb, var(--accent) 45%, transparent); background: color-mix(in srgb, var(--accent) 8%, transparent); }

/* Foto con marco neón */
.sm-foto { position: relative; display: flex; align-items: flex-end; justify-content: center; min-height: 470px;
  padding-top: 30px; border-radius: 22px; overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--accent) 45%, transparent);
  background: linear-gradient(160deg, var(--panel), var(--bg));
  box-shadow: 0 0 40px color-mix(in srgb, var(--accent) 16%, transparent) inset, 0 0 28px color-mix(in srgb, var(--accent) 14%, transparent); }
.sm-glow { position: absolute; left: 50%; top: 58%; width: 110%; height: 75%; transform: translate(-50%, -50%);
  background: radial-gradient(circle, color-mix(in srgb, var(--accent) 32%, transparent), transparent 65%); filter: blur(26px); }
.sm-foto-img { position: relative; max-height: 430px; max-width: 92%; width: auto; border-radius: 0;
  filter: drop-shadow(0 0 3px var(--accent)) drop-shadow(0 0 14px var(--accent)); }
.sm-tag { position: absolute; left: 16px; top: 16px; padding: 7px 14px; border-radius: 999px; font-size: .82rem; font-weight: 700; color: #fff;
  background: color-mix(in srgb, var(--bg) 78%, transparent); border: 1px solid color-mix(in srgb, var(--accent) 55%, transparent); backdrop-filter: blur(6px); }

/* Tarjetas */
.sm-card { border: 1px solid color-mix(in srgb, var(--accent) 35%, transparent); border-radius: 18px;
  background: var(--panel); padding: 22px 24px; transition: .25s; }
.sm-card:hover { border-color: var(--accent); box-shadow: 0 0 22px color-mix(in srgb, var(--accent) 28%, transparent); }
.sm-grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
.sm-stats { grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); }
.sm-stat { text-align: center; padding: 18px 12px; }
.sm-stat b { display: block; font-size: 1.55rem; color: var(--accent); line-height: 1.2; }
.sm-stat span { font-size: .85rem; opacity: .8; }
.sm-sub { font-size: 1.35rem; font-weight: 700; color: #fff; margin: 6px 0 2px; }
.sm-ct { font-size: 1.2rem; font-weight: 800; color: #fff; margin-bottom: 4px; }
.sm-meta { color: var(--accent2); font-weight: 600; margin-bottom: 4px; }
.sm-card p { line-height: 1.7; margin: 8px 0 0; }
.sm-ico { font-size: 1.8rem; margin-bottom: 6px; }

/* Formación */
.sm-edu { display: flex; gap: 26px; align-items: flex-start; }
.sm-edu-logo { width: 110px; height: 110px; object-fit: contain; border-radius: 50%; background: #fff; padding: 6px; flex: none;
  box-shadow: 0 0 22px color-mix(in srgb, var(--accent) 40%, transparent); }

/* Mi paso por EY */
.sm-ey { position: relative; display: flex; gap: 24px; align-items: flex-end; padding: 28px 32px 0; overflow: hidden; }
.sm-ey-txt { flex: 1; padding-bottom: 28px; }
.sm-ey-logo { height: 38px; width: auto; background: #fff; padding: 5px 10px; border-radius: 10px; margin-bottom: 12px; display: block; }
.sm-ey-foto { height: 300px; width: auto; flex: none; filter: drop-shadow(0 0 3px var(--accent)) drop-shadow(0 0 14px var(--accent)); }
.sm-cta { display: flex; flex-wrap: wrap; gap: 14px; align-items: center; margin-top: 18px; }
.sm-pulse { display: inline-flex; align-items: center; gap: 9px; padding: 8px 16px; border-radius: 999px; font-size: .88rem; font-weight: 600;
  border: 1px solid color-mix(in srgb, var(--accent) 50%, transparent); background: color-mix(in srgb, var(--accent) 10%, transparent); }
.sm-pulse::before { content: ""; width: 9px; height: 9px; border-radius: 50%; background: var(--accent2); animation: pulso 1.8s infinite; }
@keyframes pulso { 0% { box-shadow: 0 0 0 0 var(--accent2); } 70% { box-shadow: 0 0 0 10px transparent; } 100% { box-shadow: 0 0 0 0 transparent; } }

@media (max-width: 768px) {
  .sm-hola { font-size: 1.9rem; }
  .sm-foto { min-height: 360px; }
  .sm-edu { flex-direction: column; }
  .sm-ey { flex-direction: column; align-items: flex-start; padding: 22px 20px; }
  .sm-ey-foto { display: none; }
}
</style>
""",
        unsafe_allow_html=True,
    )

    # ---------- Fila 1: foto + quién soy ----------
    col_foto, col_txt = st.columns([5, 7], gap="large")

    with col_foto:
        st.markdown(
            '<div class="sm-foto"><div class="sm-glow"></div>'
            + _img("foto.png", "sm-foto-img", "Óscar")
            + '<div class="sm-tag">Óscar · 24 años</div></div>',
            unsafe_allow_html=True,
        )

    with col_txt:
        st.markdown(
            '<div class="sm-kicker">QUIÉN SOY</div>'
            '<div class="sm-hola">Hola, soy <span>Óscar</span></div>'
            '<p class="sm-lead">Tengo 24 años y me apasionan las finanzas, la economía y el análisis de datos. '
            "Disfruto investigar los datos para entender cómo se mueve el mercado, seguir de cerca la bolsa y las inversiones, "
            "y meterme un poco en la programación para automatizar lo que se pueda.</p>"
            '<p class="sm-lead">Soy muy curioso y creo que uno nunca termina de aprender, así que siempre ando buscando algo nuevo '
            "y atento a las tecnologías y a los mercados.</p>"
            '<div class="sm-chips">'
            + "".join(
                f'<span class="sm-chip">{c}</span>'
                for c in ("Finanzas", "Economía", "Análisis de datos", "Bolsa e inversiones", "Programación", "Tecnología y mercados")
            )
            + "</div>"
            '<div class="sm-label">PERFIL PROFESIONAL</div>'
            "<p>Estudiante de Economía perteneciente al tercio superior, con enfoque en finanzas corporativas, análisis de datos y gestión de riesgos. "
            "Me caracterizo por una alta disciplina y capacidad para profundizar en problemas complejos hasta comprenderlos completamente.</p>"
            "<p>Cuento con experiencia en la transformación y visualización de datos, así como en la elaboración de informes técnicos orientados a la evaluación "
            "de la salud financiera, rentabilidad corporativa y cumplimiento normativo. Busco aportar valor mediante el análisis cuantitativo riguroso "
            "y la toma de decisiones basada en la consistencia de datos financieros.</p>",
            unsafe_allow_html=True,
        )

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

    # ---------- Fila 2: datos rápidos ----------
    st.markdown(
        '<div class="sm-grid sm-stats">'
        + "".join(
            f'<div class="sm-card sm-stat"><b>{a}</b><span>{b}</span></div>'
            for a, b in (
                ("24", "años"),
                ("Tercio superior", "Economía · UNAC"),
                ("2021 – 2026", "Formación universitaria"),
                ("Big Four", "EY Perú · 2026"),
            )
        )
        + "</div>",
        unsafe_allow_html=True,
    )

    # ---------- Fila 3: formación académica ----------
    st.markdown('<div class="sm-sub">🎓 Formación académica</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sm-card sm-edu">'
        + _img("logo_unac.png", "sm-edu-logo", "Universidad Nacional del Callao")
        + '<div><div class="sm-ct">Universidad Nacional del Callao</div>'
        '<div class="sm-meta">Economía · Agosto 2021 – Actualidad</div>'
        '<div class="sm-chips"><span class="sm-chip">Tercio Superior</span><span class="sm-chip">Egreso: 2026-II</span></div>'
        "<p>Estudiar Economía me enseñó a mirar los problemas con rigor: entender cómo se toman las decisiones, "
        "cómo se mueven los mercados y cómo los datos sostienen una conclusión.</p>"
        "<p>Durante mi formación he desarrollado una sólida base en el análisis del mercado bursátil y la investigación econométrica aplicada. "
        "Mis estudios me han permitido dominar la evaluación de la salud financiera de las corporaciones e interpretar normativas complejas, "
        "como las directrices de la OCDE para la tributación internacional, aportando rigor cuantitativo a la resolución de problemas económicos reales.</p>"
        "<p>Estoy por terminar el último semestre (2026-II) y egresar. El bachiller es el siguiente paso, "
        "y mi prioridad ahora es encontrar unas prácticas preprofesionales.</p>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    # ---------- Fila 4: lo que me mueve ----------
    st.markdown('<div class="sm-sub">✨ Lo que me mueve</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sm-grid">'
        + "".join(
            f'<div class="sm-card"><div class="sm-ico">{i}</div><div class="sm-ct">{t}</div><p>{d}</p></div>'
            for i, t, d in (
                ("📈", "Mercados e inversiones",
                 "Me gusta seguir la bolsa, investigar empresas y entender qué hay detrás de los precios y del comportamiento del mercado."),
                ("💻", "Datos y programación",
                 "Disfruto analizar, transformar y visualizar datos. Con Python y Power BI automatizo procesos y convierto la información en decisiones."),
                ("🌱", "Curiosidad constante",
                 "Aprendo de todo un poco. Estoy atento a las nuevas tecnologías y a los movimientos de los mercados, siempre con algo nuevo por conocer."),
            )
        )
        + "</div>",
        unsafe_allow_html=True,
    )

    # ---------- Fila 5: mi paso por EY + prácticas ----------
    st.markdown(
        '<div class="sm-card sm-ey"><div class="sm-ey-txt">'
        + _img("logo_ey.png", "sm-ey-logo", "EY")
        + '<div class="sm-ct">Mi paso por EY</div>'
        "<p>Trabajar en EY, una de las Big Four, me permitió conocer grandes profesionales, compañeros y amigos, y llevarme una muy buena experiencia. "
        "Siento que la persona que entró no es la misma que salió: hoy me siento mucho más preparado para afrontar cualquier reto.</p>"
        "<p>Esa experiencia real, sumada a la base teórica que aprendí en la universidad, es lo que hoy me diferencia al empezar mi etapa profesional.</p>"
        '<div class="sm-cta"><span class="sm-pulse">Buscando prácticas preprofesionales</span>'
        f'<a class="btn btn-solid" href="{url(pagina, "contactame")}" target="_self">Contáctame →</a></div>'
        "</div>"
        + _img("foto_2.png", "sm-ey-foto", "Óscar")
        + "</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # =====================================================================
    # 7. EXPERIENCIA PROFESIONAL  (tarjeta de cargo + tarjetas de funciones + logro)
    #    Usa logo_ey.png (si falta, simplemente no se muestra)
    # =====================================================================
    st.header("💼 Experiencia Profesional", anchor="experiencia-profesional")

    st.markdown(
        """
<style>
/* ---------- Experiencia ---------- */
.ex-head { display: flex; align-items: center; gap: 24px; flex-wrap: wrap; padding: 22px 28px;
  border-left: 5px solid var(--accent); }
.ex-logo { height: 70px; width: auto; background: #fff; padding: 8px 14px; border-radius: 14px; flex: none;
  box-shadow: 0 0 22px color-mix(in srgb, var(--accent) 35%, transparent); }
.ex-info { flex: 1 1 320px; }
.ex-info .sm-chips { margin: 8px 0 0; }
.ex-date { padding: 10px 18px; border-radius: 14px; font-weight: 700; white-space: nowrap;
  border: 1px solid color-mix(in srgb, var(--accent) 50%, transparent); background: color-mix(in srgb, var(--accent) 10%, transparent); }
.ex-date small { display: block; font-weight: 500; opacity: .75; }
.ex-grid { display: grid; gap: 16px; grid-template-columns: repeat(3, 1fr); }
.ex-grid .sm-card p { font-size: .98rem; }
.ex-logro { background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 24%, var(--panel)), var(--panel));
  border-color: var(--accent); box-shadow: 0 0 26px color-mix(in srgb, var(--accent) 22%, transparent); }
.ex-logro .sm-chips { margin-bottom: 0; }

/* ---------- Competencias ---------- */
.sk { margin: 14px 0 0; }
.sk-top { display: flex; justify-content: space-between; align-items: baseline; font-weight: 600; margin-bottom: 6px; }
.sk-top em { font-style: normal; font-size: .8rem; color: var(--accent2); }
.sk-bar { height: 9px; border-radius: 999px; background: color-mix(in srgb, var(--accent) 14%, transparent); overflow: hidden; }
.sk-fill { height: 100%; width: var(--w); border-radius: 999px; animation: llenar 1.3s ease-out both;
  background: linear-gradient(90deg, var(--accent), var(--accent2)); box-shadow: 0 0 10px color-mix(in srgb, var(--accent) 60%, transparent); }
/* con el efecto de aparecer al bajar, las barras se llenan cuando la tarjeta aparece */
.rv:not(.rv-in) .sk-fill { width: 0; animation: none; }
.rv.rv-in .sk-fill { animation: llenar 1.3s ease-out .4s both; }
@keyframes llenar { from { width: 0; } to { width: var(--w); } }
.sk-sub { color: var(--accent2); font-weight: 700; letter-spacing: .08em; font-size: .8rem; margin: 18px 0 2px; }

@media (max-width: 1000px) { .ex-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px)  { .ex-grid { grid-template-columns: 1fr; } .ex-head { padding: 18px; } }
</style>
""",
        unsafe_allow_html=True,
    )

    # ---------- Cargo ----------
    st.markdown(
        '<div class="sm-card ex-head">'
        + _img("logo_ey.png", "ex-logo", "EY")
        + '<div class="ex-info"><div class="sm-ct">EY Perú (Ernst &amp; Young)</div>'
        '<div class="sm-meta">Asistente Junior del Área de Precios de Transferencia</div>'
        '<div class="sm-chips"><span class="sm-chip">Firma global · Big Four</span>'
        '<span class="sm-chip">Consultoría fiscal</span></div></div>'
        '<div class="ex-date">📅 05/2026 – 31/10/2026<small>Experiencia finalizada</small></div>'
        "</div>",
        unsafe_allow_html=True,
    )

    # ---------- Funciones + logro ----------
    funciones = (
        ("🏢", "Consultoría fiscal",
         "Desarrollo profesional en la línea de consultoría fiscal de una de las firmas globales líderes del sector."),
        ("📊", "Análisis financiero",
         "Análisis cuantitativo de la salud financiera, márgenes operativos y rentabilidad de empresas para verificar la consistencia "
         "de sus datos frente a comparables del mercado."),
        ("⚖️", "Cumplimiento normativo",
         "Participación activa en el análisis de funciones, activos y evaluación de riesgos operativos de grandes corporaciones "
         "para asegurar el cumplimiento normativo internacional (OCDE)."),
        ("🧮", "Reportes y validación",
         "Estructuración de reportes cruzando información financiera. Identificación, corrección y validación de discrepancias "
         "de cálculo entre grandes volúmenes de datos."),
        ("💎", "Valuaciones",
         "Soporte y participación en la elaboración de informes de Valuaciones de activos."),
    )
    st.markdown(
        '<div class="ex-grid">'
        + "".join(
            f'<div class="sm-card"><div class="sm-ico">{i}</div><div class="sm-ct">{t}</div><p>{d}</p></div>'
            for i, t, d in funciones
        )
        + '<div class="sm-card ex-logro"><div class="sm-ico">🏆</div><div class="sm-ct">Logro</div>'
        "<p>Optimización en procesos de recopilación y análisis de Big data de páginas públicas como la SBS, SMV, SEC Edgar, "
        "entre otros, empleando programas como Python y Power BI.</p>"
        '<div class="sm-chips">'
        + "".join(f'<span class="sm-chip">{c}</span>' for c in ("SBS", "SMV", "SEC Edgar", "Python", "Power BI"))
        + "</div></div></div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # =====================================================================
    # 8. COMPETENCIAS Y FORTALEZAS  (tarjetas con barras de nivel)
    # =====================================================================
    st.header("🛠️ Competencias y Fortalezas", anchor="competencias")

    NIVELES = {"Avanzado": 85, "Intermedio": 60}  # ancho de la barra según el nivel

    def barras(items):
        return "".join(
            f'<div class="sk"><div class="sk-top"><span>{n}</span><em>{lv}</em></div>'
            f'<div class="sk-bar"><div class="sk-fill" style="--w:{NIVELES[lv]}%"></div></div></div>'
            for n, lv in items
        )

    def chips(items):
        return '<div class="sm-chips">' + "".join(f'<span class="sm-chip">{c}</span>' for c in items) + "</div>"

    st.markdown(
        '<div class="sm-grid">'
        '<div class="sm-card"><div class="sm-ico">📊</div><div class="sm-ct">Análisis de Datos</div>'
        + barras((("Python", "Intermedio"), ("Excel", "Avanzado"), ("Power BI", "Intermedio"), ("SQL", "Intermedio")))
        + "</div>"
        '<div class="sm-card"><div class="sm-ico">📈</div><div class="sm-ct">Econometría</div>'
        + barras((("EViews", "Avanzado"), ("Stata", "Intermedio"), ("SPSS", "Intermedio")))
        + "</div>"
        '<div class="sm-card"><div class="sm-ico">🌎</div><div class="sm-ct">Idiomas y Soft Skills</div>'
        '<div class="sk-sub">IDIOMAS</div>'
        + chips(("Español · Nativo", "Inglés", "Francés"))
        + '<div class="sk-sub">SOFT SKILLS</div>'
        + chips(("Pensamiento analítico", "Resolución de problemas complejos"))
        + "</div></div>",
        unsafe_allow_html=True,
    )

    st.divider()

else:  # pagina == "proyectos"
    # =====================================================================
    # 9. PROYECTOS  (tarjetas en cuadrícula + botón "Ver más" que abre una ventana)
    # =====================================================================
    import html as _html

    st.header("Proyectos", anchor="proyectos")

    # ---------- Estilos de las tarjetas ----------
    st.markdown(
        """
<style>
/* La COLUMNA que contiene .proj-card se convierte en la tarjeta */
[data-testid="stHorizontalBlock"]:has(.proj-card) { align-items: stretch !important; row-gap: 26px; }
[data-testid="stColumn"]:has(.proj-card), [data-testid="column"]:has(.proj-card) {
  background: var(--panel); border-radius: 18px; overflow: hidden; padding: 0 !important; transition: .25s;
  border: 1px solid color-mix(in srgb, var(--accent) 32%, transparent); }
[data-testid="stColumn"]:has(.proj-card):hover, [data-testid="column"]:has(.proj-card):hover {
  transform: translateY(-4px); border-color: var(--accent);
  box-shadow: 0 10px 34px color-mix(in srgb, var(--accent) 28%, transparent); }
[data-testid="stColumn"]:has(.proj-card) > [data-testid="stVerticalBlock"],
[data-testid="column"]:has(.proj-card) > [data-testid="stVerticalBlock"] { gap: 0 !important; height: 100%; }

/* Imagen */
.proj-img { position: relative; height: 210px; overflow: hidden; background: linear-gradient(135deg, var(--panel), var(--bg)); }
.proj-img img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .5s; }
.proj-card:hover .proj-img img { transform: scale(1.05); }
.proj-img::after { content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(180deg, transparent 55%, color-mix(in srgb, var(--panel) 85%, transparent)); }
.proj-ph { height: 100%; display: grid; place-items: center; font-size: 4rem; opacity: .6; }
.proj-tag { position: absolute; z-index: 2; top: 12px; left: 12px; font-size: .72rem; font-weight: 700; letter-spacing: .04em;
  padding: 4px 11px; border-radius: 999px; color: #fff; backdrop-filter: blur(6px);
  background: color-mix(in srgb, var(--bg) 70%, transparent); border: 1px solid color-mix(in srgb, var(--accent) 55%, transparent); }

/* Cuerpo */
.proj-body { padding: 16px 20px 6px; }
.proj-title { color: #fff; font-weight: 800; font-size: 1.18rem; line-height: 1.3; min-height: 3.1rem; margin-bottom: 8px; }
.proj-desc { font-size: .9rem; line-height: 1.55; opacity: .82; height: 6.2em; overflow: hidden;
  display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; }
.proj-chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 0 14px; min-height: 28px; }
.proj-chips span { font-size: .72rem; padding: 3px 10px; border-radius: 999px; color: var(--accent2);
  background: color-mix(in srgb, var(--accent) 12%, transparent); border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent); }
.proj-meta { display: flex; gap: 14px; flex-wrap: wrap; padding-top: 12px; font-size: .78rem; opacity: .75;
  border-top: 1px solid color-mix(in srgb, var(--accent) 22%, transparent); min-height: 44px; }
.proj-meta b { color: #fff; font-weight: 600; }

/* Botón "Ver más" */
[data-testid="stColumn"]:has(.proj-card) [data-testid="stButton"],
[data-testid="column"]:has(.proj-card) [data-testid="stButton"] { padding: 10px 20px 20px; }
[data-testid="stColumn"]:has(.proj-card) [data-testid="stButton"] button,
[data-testid="column"]:has(.proj-card) [data-testid="stButton"] button {
  width: 100%; border-radius: 12px; background: color-mix(in srgb, var(--accent) 10%, var(--bg));
  border: 1px solid color-mix(in srgb, var(--accent) 55%, transparent); transition: .25s; }
[data-testid="stColumn"]:has(.proj-card) [data-testid="stButton"] button p,
[data-testid="column"]:has(.proj-card) [data-testid="stButton"] button p { color: #fff !important; font-weight: 700; }
[data-testid="stColumn"]:has(.proj-card) [data-testid="stButton"] button:hover,
[data-testid="column"]:has(.proj-card) [data-testid="stButton"] button:hover {
  background: var(--accent); border-color: var(--accent); box-shadow: 0 0 18px color-mix(in srgb, var(--accent) 50%, transparent); }
[data-testid="stColumn"]:has(.proj-card) [data-testid="stButton"] button:hover p,
[data-testid="column"]:has(.proj-card) [data-testid="stButton"] button:hover p { color: #04110a !important; }
</style>
""",
        unsafe_allow_html=True,
    )

    # ---------- Datos de los proyectos (para agregar uno nuevo, copia un bloque) ----------
    PROYECTOS = [
        {
            "id": "bvl",
            "categoria": "Automatización",
            "titulo": "Extractor Automático de Cotizaciones - BVL",
            "resumen": "Aplicación de escritorio que descarga series de tiempo históricas de la Bolsa de Valores de Lima y las exporta a Excel, lista para modelado econométrico.",
            "imagenes": ["app_bvl.jpg"],
            "posicion": "center top",
            "emoji": "📈",
            "etiquetas": ["Python", "Tkinter", "YFinance"],
            "datos": [("🖥️", "App de escritorio"), ("📤", "Salida: Excel"), ("📊", "EViews / SPSS")],
        },
        {
            "id": "alicorp",
            "categoria": "Valorización",
            "titulo": "Valorización Financiera de Alicorp S.A.A.",
            "resumen": "Informe sobre la valoración corporativa de Alicorp: salud financiera, proyección de flujos de caja y determinación del valor intrínseco de la compañía.",
            "imagenes": ["portada_alicorp.jpg"],
            "posicion": "center",
            "emoji": "🏢",
            "etiquetas": ["Finanzas corporativas", "Flujos de caja", "Valor intrínseco"],
            "datos": [("📄", "Informe en PDF"), ("🏢", "Alicorp S.A.A."), ("📥", "Descargable")],
        },
        {
            "id": "eeff",
            "categoria": "Automatización",
            "titulo": "Extractor Automatizado de Estados Financieros",
            "resumen": "Script que extrae y estructura Balances Generales y Estados de Resultados desde múltiples reportes en PDF, reduciendo horas de procesamiento manual.",
            "imagenes": ["excel_estados_financieros.jpg"],
            "posicion": "center top",
            "emoji": "🧾",
            "etiquetas": ["PDF → Excel", "Estados financieros", "Análisis fundamental"],
            "datos": [("🔒", "Código reservado"), ("🚧", "En escalamiento"), ("📤", "Salida: Excel")],
        },
    ]

    @st.cache_data(show_spinner=False)
    def _img_tarjeta(*rutas):
        return img_a_base64(*rutas)

    def tarjeta_html(p):
        src = _img_tarjeta(*p["imagenes"])
        if src:
            imagen = f'<img src="{src}" style="object-position:{p["posicion"]}" alt="{_html.escape(p["titulo"])}">'
        else:
            imagen = f'<div class="proj-ph">{p["emoji"]}</div>'
        chips = "".join(f"<span>{_html.escape(e)}</span>" for e in p["etiquetas"])
        meta = "".join(f"<span>{ico} <b>{_html.escape(txt)}</b></span>" for ico, txt in p["datos"])
        return (
            '<div class="proj-card">'
            f'<div class="proj-img"><div class="proj-tag">{_html.escape(p["categoria"])}</div>{imagen}</div>'
            '<div class="proj-body">'
            f'<div class="proj-title">{_html.escape(p["titulo"])}</div>'
            f'<div class="proj-desc">{_html.escape(p["resumen"])}</div>'
            f'<div class="proj-chips">{chips}</div>'
            f'<div class="proj-meta">{meta}</div>'
            "</div></div>"
        )

    # ---------- Ventanas de detalle (se abren con "Ver más") ----------
    def ventana(titulo):
        deco = getattr(st, "dialog", None) or getattr(st, "experimental_dialog", None)
        if deco:
            return deco(titulo, width="large")

        def sin_dialogo(fn):  # Streamlit antiguo: se muestra debajo en vez de ventana flotante
            def interno():
                st.subheader(titulo)
                fn()
            return interno
        return sin_dialogo

    def mostrar_img(ruta, aviso, **kw):
        try:
            st.image(ruta, use_container_width=True, **kw)
        except FileNotFoundError:
            st.info(aviso)

    @ventana("Extractor Automático de Cotizaciones - BVL")
    def detalle_bvl():
        st.write("Desarrollo de una aplicación de escritorio con **Python (Tkinter y YFinance)**. Esta herramienta automatiza la descarga de series de tiempo históricas de la Bolsa de Valores de Lima (BVL) y exporta los datos estructurados a Excel, optimizando el flujo de trabajo para su posterior modelado econométrico en software especializado como EViews o SPSS.")
        tab1, tab2, tab3 = st.tabs(["💻 Código Script", "📸 Interfaz Gráfica", "📊 Excel Resultante"])
        with tab1:
            st.write("Script de extracción financiera:")
            st.code(CODIGO_BVL, language="python")
        with tab2:
            st.write("Interfaz gráfica desarrollada con Tkinter:")
            mostrar_img("app_bvl.jpg", "📸 Sube una captura de tu app y llámala 'app_bvl.jpg'")
        with tab3:
            st.write("Base de datos estructurada y lista para análisis:")
            mostrar_img("excel_bvl.jpg", "📸 Sube una captura del Excel generado y llámala 'excel_bvl.jpg'")

    @ventana("Valorización Financiera de Alicorp S.A.A.")
    def detalle_alicorp():
        mostrar_img("portada_alicorp.jpg", "📸 Sube la portada de tu informe y llámala 'portada_alicorp.jpg'")
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

    @ventana("Extractor Automatizado de Estados Financieros")
    def detalle_eeff():
        mostrar_img("excel_estados_financieros.jpg", "📸 Sube la captura de tu Excel y llámala 'excel_estados_financieros.jpg'",
                    caption="Output automatizado de datos estructurados")
        st.write("Desarrollo de un script diseñado para la extracción masiva y estructuración de Balances Generales y Estados de Resultados a partir de múltiples reportes financieros en PDF. Esta herramienta reduce drásticamente las horas-hombre de procesamiento manual, siendo un activo clave para agilizar el análisis fundamental, la construcción de modelos de valoración corporativa, estudios de empresas comparables y la evaluación de la salud financiera.")
        st.write("**Escalamiento del proyecto (Visión a futuro):**")
        st.write("Actualmente en proceso de integración con el motor de cotizaciones bursátiles para conformar un sistema integral de inteligencia financiera. Esto automatizará el cálculo de ratios financieros, KPIs sectoriales y la minería de datos cualitativos (composición accionaria, estructura corporativa y segmentación de ingresos).")
        st.info("🔒 **Confidencialidad:** El código fuente de este proyecto se mantiene en reserva debido a la sensibilidad de la información. Solo se mostrará en pantalla la estructura final de los datos procesados.")

    DETALLES = {"bvl": detalle_bvl, "alicorp": detalle_alicorp, "eeff": detalle_eeff}

    # ---------- Cuadrícula: 3 tarjetas por fila ----------
    POR_FILA = 3
    for i in range(0, len(PROYECTOS), POR_FILA):
        columnas = st.columns(POR_FILA, gap="large")
        for col, p in zip(columnas, PROYECTOS[i:i + POR_FILA]):
            with col:
                st.markdown(tarjeta_html(p), unsafe_allow_html=True)
                if st.button("Ver más →", key=f"vermas_{p['id']}", use_container_width=True):
                    DETALLES[p["id"]]()

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


# =====================================================================
# 11. EFECTO "APARECER AL BAJAR" (script invisible)
#     Los bloques que están fuera de la pantalla se ocultan y suben suavemente
#     cuando entran en ella. Lo que ya se ve al abrir la página no se toca.
# =====================================================================
try:
    import streamlit.components.v1 as components

    components.html(
        """
<script>
(function () {
  try {
    var P = window.parent, D = P.document;
    if (P.__rvObs) { P.__rvObs.io.disconnect(); P.__rvObs.mo.disconnect(); }

    var io = new P.IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('rv-in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.04, rootMargin: '0px 0px -70px 0px' });

    function raiz() {
      var b = D.querySelector('[data-testid="stMainBlockContainer"]') || D.querySelector('.block-container');
      return b ? b.querySelector('[data-testid="stVerticalBlock"]') : null;
    }
    function preparar() {
      var r = raiz(); if (!r) return;
      Array.prototype.forEach.call(r.children, function (el) {
        if (el.__rv || el.offsetHeight < 30) return;            // ya procesado o aún sin dibujar
        el.__rv = 1;
        if (el.querySelector('style, iframe, .nav, .hero')) return;   // barra, cuadro principal, scripts
        if (el.getBoundingClientRect().top < P.innerHeight - 70) return; // ya visible al cargar
        el.classList.add('rv');
        io.observe(el);
      });
    }

    preparar();
    var r0 = raiz();
    var mo = new P.MutationObserver(preparar);
    if (r0) mo.observe(r0, { childList: true });
    var n = 0, iv = setInterval(function () { preparar(); if (++n > 12) clearInterval(iv); }, 400);
    P.__rvObs = { io: io, mo: mo };
  } catch (e) {}
})();
</script>
""",
        height=0,
    )
except Exception:
    pass