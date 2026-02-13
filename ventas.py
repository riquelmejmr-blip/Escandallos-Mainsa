import streamlit as st
import pandas as pd
import json
import re
import math
from copy import deepcopy

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="MAINSA ADMIN V44", layout="wide")

MERMA_RIGIDO_PCT = 0.02  # 2% adicional SOLO para consumo de hojas rígidas (compra)

# =========================================================
# MERMAS ESTÁNDAR (AUTO)
# Devuelve: (merma_proceso_hojas, merma_impresion_hojas)
# =========================================================
def calcular_mermas_estandar(n: int, es_digital: bool = False):
    if es_digital:
        return int(n * 0.02), 10  # (proceso, impresión)
    if n < 100:
        return 10, 150
    if n < 200:
        return 20, 175
    if n < 600:
        return 30, 200
    if n < 1000:
        return 40, 220
    if n < 2000:
        return 50, 250
    return int(n * 0.03), 300

# =========================================================
# CATÁLOGO FLEXICO
# =========================================================
PRODUCTOS_FLEXICO = {
    "172018": {"desc": "GANCHO EXTENSIBLE MAXI 0,5kg", "precio": 0.0397},
    "137018": {"desc": "PORTAETIQUETA GANCHO 28x30 mm", "precio": 0.0742},
    "142201": {"desc": "GANCHO PERFORANTE SIMPLE 200mm", "precio": 0.1480},
    "142203": {"desc": "GANCHO PERFORANTE SIMPLE 150mm", "precio": 0.1290},
    "142205": {"desc": "GANCHO PERFORANTE SIMPLE 100mm", "precio": 0.1080},
    "142206": {"desc": "GANCHO PERFORADOR SIMPLE 5 CM", "precio": 0.1530},
    "142412": {"desc": "GANCHO PERFORANTE DOBLE 100mm", "precio": 0.1260},
    "142413": {"desc": "GANCHO PERFORANTE DOBLE 150mm", "precio": 0.1280},
    "142414": {"desc": "PERFORANTE DOBLE 200mm GANCHO", "precio": 0.1710},
    "142415": {"desc": "PERFORANTE DOBLE 250mm GANCHO", "precio": 0.1800},
    "142422": {"desc": "GANCHO PERFO DOBLE NEGRO 100mm", "precio": 0.1020},
    "142424": {"desc": "GANCHO PERFO DOBLE NEGRO 200mm", "precio": 0.1880},
    "145104": {"desc": "TIRA CROSS MERCH METALICA", "precio": 3.1100},
    "145110": {"desc": "TIRA CROSS MERCH-740 MM", "precio": 0.3310},
    "145150": {"desc": "PINZA PARA CROSS-MERCHANDISING", "precio": 0.1072},
    "172594": {"desc": "ANILLA LLAVERO - 20 MM", "precio": 0.0600},
    "262041": {"desc": "SUJETADOR PERFIL PP 30-40mm", "precio": 0.0500},
    "752012": {"desc": "BISTUCADOR Ø12mm CIER14mm NEGR", "precio": 0.0400},
    "752013": {"desc": "BISTUCADOR Ø12mm CIER14mm TRSP", "precio": 0.0410},
    "752015": {"desc": "BISTUCADOR Ø12mm CIER7mm TRSP", "precio": 0.0370},
    "753007": {"desc": "SOP PORTACARTEL ADH TRSP 56X25", "precio": 0.1770},
    "792010": {"desc": "GANCHO SUSPENSION + HILO 1,2m", "precio": 0.1160},
    "792032": {"desc": "HILO NYLON- BOBINA 200M", "precio": 5.4800},
    "792071": {"desc": "TWISTER METAL 2 ADH 75mm", "precio": 0.0538},
    "792301": {"desc": "BASE DE PLAS EXPOSITOR TRSP", "precio": 0.1840},
    "792421": {"desc": "GANCHO S METAL 24MM DIAM 2MM", "precio": 0.0215},
    "792425": {"desc": "ESSE 32MM BOUCLE DIA 6 & 14MM", "precio": 0.0360},
    "792427": {"desc": "GANCHO S METAL30MM DIAM 2MM", "precio": 0.0267},
    "792432": {"desc": "GANCHO S 36 MM 014", "precio": 0.0300},
    "792436": {"desc": "GANCHO S METAL ASYMETRICO 45MM", "precio": 0.0394},
    "792437": {"desc": "GANCHO S METAL ASYMETRICO 40MM", "precio": 0.0428},
    "792451": {"desc": "GANCHO S METAL 59MM DIAM 2MM", "precio": 0.0365},
    "792452": {"desc": "GANCHO S METAL 65MM DIAM 2,5MM", "precio": 0.0540},
    "792542": {"desc": "TWISTER PET 75MM-2 ADHESIVOS", "precio": 0.0460},
    "792546": {"desc": "WOBBLER PET 150MM 2 ADH", "precio": 0.0411},
    "792550": {"desc": "WOBBLER PET 150MM 2 ADH REMOV", "precio": 0.0613},
    "792570": {"desc": "MEGA TWISTER METAL 2 ADH", "precio": 0.0897},
    "792571": {"desc": "TWISTER METAL 2 ADH", "precio": 0.0400},
    "792573": {"desc": "TWISTER METAL 3 ADH", "precio": 0.0543},
    "792582": {"desc": "TWISTER MET 75MM 2 ADH EN HOJA", "precio": 0.0600},
    "793075": {"desc": "TWISTER 2 ADH CLEAN", "precio": 0.0650},
    "793240": {"desc": "1100 ALMOH AUTOADH MACHO-19mm", "precio": 15.6000},
    "793242": {"desc": "1100 ALMOH AUTOADH HEMBRA-19mm", "precio": 15.6000},
    "793249": {"desc": "1500ALMOH AUTOAD HEMBR 13 NEGR", "precio": 11.8000},
    "793250": {"desc": "1500ALMOH AUTOAD MACH 13 NEGR", "precio": 11.8000},
    "793301": {"desc": "PLETINA PVC ADH 20X20mm", "precio": 0.0382},
    "793303": {"desc": "PLETINA PVC ADH 20X40mm", "precio": 0.0680},
    "796007": {"desc": "TORNILLO Ø15mm MAXI 9mm BLCO", "precio": 0.0299},
    "796043": {"desc": "TORNILLO Ø28mm MAXI 22mm BLCO", "precio": 0.0534},
    "796307": {"desc": "TORNILLO Ø 15mm MAXI 9mm NEGRO", "precio": 0.0300},
    "796309": {"desc": "TORNILLO Ø28mm MAXI 15mm NEGRO", "precio": 0.0320},
    "796343": {"desc": "TORNILLO Ø28mm MAXI 22mm NEGRO", "precio": 0.0525},
    "796407": {"desc": "TORNILLO Ø15mm MAXI 9mm TRSP", "precio": 0.0294},
    "796409": {"desc": "TORNILLO Ø28 mm MAXI15 mm TRSP", "precio": 0.0325},
    "796443": {"desc": "TORNILLO Ø 28mm MAXI 22mm TRSP", "precio": 0.0570},
    "796445": {"desc": "TORNILLO Ø 28mm MAXI 38mm TRSP", "precio": 0.0597},
    "797133": {"desc": "GRIPADOR 2 ENTRADAS EN L 25mm", "precio": 0.0579},
    "797148": {"desc": "GRIPADOR T13mm LG 76mm ADH", "precio": 0.0821},
    "797150": {"desc": "GRIPADOR T 28mm LG 25mm ADH", "precio": 0.0398},
    "797193": {"desc": "GRIPADOR 2 ENTRADAS EN J", "precio": 0.1080},
    "797786": {"desc": "PINZA MULTI ANGULO", "precio": 0.1460},
    "797885": {"desc": "BRIDA NYLON 300MM", "precio": 0.0434},
    "797910": {"desc": "PISTOLA", "precio": 10.5000},
    "797911": {"desc": "SET DE 5 AGUJERAS", "precio": 7.8000},
    "797915": {"desc": "ATADURAS NYLON 40MM", "precio": 0.0020},
    "797917": {"desc": "ATADURAS NYLON 65MM", "precio": 0.0024},
    "797921": {"desc": "ATADURAS EXTR ESTR 125mm", "precio": 0.0037},
    "841201": {"desc": "PESCANTE MULTIMAG", "precio": 1.8000},
    "841211": {"desc": "PESCANTE MULTIMAG PLUS", "precio": 1.9400},
    "950101": {"desc": "GANCHO FONDO PERF SIMPLE 50MM", "precio": 0.1384},
    "950235": {"desc": "CABLE ACIER ANTIRROBO PLACA", "precio": 2.6000},
    "950341": {"desc": "PORTA VISUAL BASE MADERA - A5", "precio": 5.5000},
    "950790": {"desc": "SUPER VENTOSA CON TORNILLON", "precio": 3.0100},
    "142002": {"desc": "GANCHO UNIVERSAL SIMPLE 100mm", "precio": 0.1101},
    "145101": {"desc": "TIRA CROSS MERCH DBLE FLJ 780", "precio": 0.4424},
    "145103": {"desc": "TIRA CROSS MERCH PNZA METL 790", "precio": 2.3700},
    "145111": {"desc": "TIRA CROSSMERCH 600 PE85X100mm", "precio": 0.2830},
    "163401": {"desc": "PINZA PORTA ETIQ ARTICUL TRSP", "precio": 0.3474},
    "172012": {"desc": "GANCHO SUSPENSION +HILO 1,2M", "precio": 0.1500},
    "172078": {"desc": "GANCHO DOBLE METALICO 300mm", "precio": 0.0690},
    "950221": {"desc": "BASE GIRATORIA Ø 150 MM", "precio": 1.9400},
}
OPCIONES_FLEXICO = [f"{k} - {v['desc']}" for k, v in PRODUCTOS_FLEXICO.items()]

# =========================================================
# BASE DE PRECIOS
# =========================================================
PRECIOS_BASE = {
    "cartoncillo": {
        "Ninguno": {"precio_kg": 0.0, "gramaje": 0},
        "Reverso Gris": {"precio_kg": 0.93, "gramaje": 220},
        "Zenith": {"precio_kg": 1.55, "gramaje": 350},
        "Reverso Madera": {"precio_kg": 0.95, "gramaje": 400},
        "Folding Kraft": {"precio_kg": 1.90, "gramaje": 340},
        "Folding Blanco": {"precio_kg": 1.82, "gramaje": 350},
    },
    "planchas": {
        "Ninguna": {"C/C": 0.0, "peg": 0.0},
        "Microcanal / Canal 3": {"C/C": 0.659, "B/C": 0.672, "B/B": 0.758, "peg": 0.217},
        "Doble Micro / Doble Doble": {"C/C": 1.046, "B/C": 1.1, "B/B": 1.276, "peg": 0.263},
        "AC (Cuero/Cuero)": {"C/C": 2.505, "peg": 0.217},
    },
    "rigidos": {
        "Ninguno": {"precio_ud": 0.0, "w": 0, "h": 0},

        # PVC 1000x700
        "PVC TRANSPARENTE 300 MICRAS": {"precio_ud": 1.80, "w": 1000, "h": 700},
        "PVC TRANSPARENTE 500 MICRAS": {"precio_ud": 2.99, "w": 1000, "h": 700},
        "PVC TRANSPARENTE 700 MICRAS": {"precio_ud": 4.22, "w": 1000, "h": 700},
        "PVC BLANCO MATE 300 MICRAS": {"precio_ud": 1.76, "w": 1000, "h": 700},
        "PVC BLANCO MATE 500 MICRAS": {"precio_ud": 2.94, "w": 1000, "h": 700},
        "PVC BLANCO MATE 700 MICRAS": {"precio_ud": 4.11, "w": 1000, "h": 700},

        # APET 1000x700
        "APET 300 MICRAS": {"precio_ud": 1.35, "w": 1000, "h": 700},
        "APET 500 MICRAS": {"precio_ud": 2.25, "w": 1000, "h": 700},

        # PET G 1250x2050
        "PET G 0,5mm": {"precio_ud": 8.87, "w": 1250, "h": 2050},
        "PET G 0,7mm": {"precio_ud": 11.22, "w": 1250, "h": 2050},
        "PET G 1mm": {"precio_ud": 13.61, "w": 1250, "h": 2050},

        # Polipropileno compacto 1000x700
        "POLIPROPILENO COMPACTO BLANCO/ NATURAL 300 MICRAS": {"precio_ud": 1.00, "w": 1000, "h": 700},
        "POLIPROPILENO COMPACTO BLANCO/ NATURAL 500 MICRAS": {"precio_ud": 1.67, "w": 1000, "h": 700},
        "POLIPROPILENO COMPACTO BLANCO/ NATURAL 800 MICRAS": {"precio_ud": 2.67, "w": 1000, "h": 700},

        # Compacto 1050x750
        "COMPACTO 1,5 MM": {"precio_ud": 1.80, "w": 1050, "h": 750},
        "COMPACTO 2 MM": {"precio_ud": 2.15, "w": 1050, "h": 750},
        "COMPACTO 3 MM": {"precio_ud": 3.00, "w": 1050, "h": 750},

        # Polipropileno celular 3050x2050
        "POLIPROPILENO CELULAR 3,5 MM": {"precio_ud": 15.00, "w": 3050, "h": 2050},
    },
    "peliculado": {
        "Sin Peliculado": 0.0,
        "Polipropileno": 0.26,
        "Poliéster brillo": 0.38,
        "Poliéster mate": 0.64,
    },
    "laminado_digital": 3.5,
    "extras_base": {
        "CINTA D/CARA": 0.26, "CINTA LOHMAN": 0.49, "CINTA GEL": 1.2,
        "GOMA TERMINALES": 0.079, "IMAN 20x2mm": 1.145, "TUBOS": 1.06,
        "REMACHES": 0.049, "VELCRO": 0.43, "PUNTO ADHESIVO": 0.08
    },
    "troquelado": {
        "Pequeño (< 1000x700)": {"arranque": 48.19, "tiro": 0.06},
        "Mediano (Estándar)": {"arranque": 80.77, "tiro": 0.09},
        "Grande (> 1000x700)": {"arranque": 107.80, "tiro": 0.135},
    },
    "plotter": {"precio_hoja": 2.03},
}

FORMATOS_STD = {
    "Personalizado": (0, 0),
    "1600x1200": (1600, 1200),
    "1600x1100": (1600, 1100),
    "1400x1000": (1400, 1000),
    "1300x900": (1300, 900),
    "1200x800": (1200, 800),
    "1100x800": (1100, 800),
    "1000x700": (1000, 700),
    "900x650": (900, 650),
    "800x550": (800, 550),
    "700x500": (700, 500),
}

# =========================================================
# HELPERS
# =========================================================
def parse_cantidades(texto: str) -> list[int]:
    if not texto:
        return []
    out: list[int] = []
    for x in texto.split(","):
        x = x.strip()
        if x.isdigit():
            v = int(x)
            if v > 0:
                out.append(v)
    return out

def f_offset(nb: float) -> float:
    return 60 if nb < 100 else (120 if nb > 500 else 60 + 0.15 * (nb - 100))

def categoria_troquel(h: float, w: float) -> str:
    if (h > 1000 or w > 700):
        return "Grande (> 1000x700)"
    if (h < 1000 and w < 700):
        return "Pequeño (< 1000x700)"
    return "Mediano (Estándar)"

def crear_forma_vacia(index: int) -> dict:
    return {
        "nombre": f"Forma {index + 1}",
        "pliegos": 1.0,
        "w": 0, "h": 0,

        "pf": "Ninguno", "gf": 0,
        "pd": "Ninguno", "gd": 0,

        "tipo_base": "Ondulado/Cartón",
        "pl": "Ninguna", "ap": "B/C",
        "pl_dif": False, "pl_h": 0, "pl_w": 0,

        "mat_rigido": "Ninguno",

        "im": "No", "nt": 0, "ba": False,
        "im_d": "No", "nt_d": 0, "ba_d": False,

        "pel": "Sin Peliculado", "pel_d": "Sin Peliculado",
        "ld": False, "ld_d": False,

        "cor": "Troquelado",
        "cobrar_arreglo": True,
        "pv_troquel": 0.0,
    }

# =========================================================
# SESSION STATE INIT
# =========================================================
if "db_precios" not in st.session_state:
    st.session_state.db_precios = deepcopy(PRECIOS_BASE)
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "piezas_dict" not in st.session_state:
    st.session_state.piezas_dict = {0: crear_forma_vacia(0)}
if "lista_extras_grabados" not in st.session_state:
    st.session_state.lista_extras_grabados = []
if "costes_embalaje_manual" not in st.session_state:
    st.session_state.costes_embalaje_manual = {}
if "mermas_imp_manual" not in st.session_state:
    st.session_state.mermas_imp_manual = {}
if "mermas_proc_manual" not in st.session_state:
    st.session_state.mermas_proc_manual = {}
if "emb_tipo" not in st.session_state:
    st.session_state.emb_tipo = "Manual"
if "emb_dims" not in st.session_state:
    st.session_state.emb_dims = {"L": 0, "W": 0, "H": 0}
if "brf" not in st.session_state:
    st.session_state.brf = ""
if "cli" not in st.session_state:
    st.session_state.cli = ""
if "desc" not in st.session_state:
    st.session_state.desc = ""

db = st.session_state.db_precios

# =========================================================
# UI STYLE + TITLE
# =========================================================
st.markdown(
    """<style>
    .comercial-box { background-color: white; padding: 30px; border: 2px solid #1E88E5; border-radius: 10px; color: #333; }
    .comercial-header { color: #1E88E5; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 5px; }
    .comercial-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 1.1em; }
    .comercial-table th { background-color: #1E88E5; color: white; padding: 10px; }
    .comercial-table td { padding: 10px; border: 1px solid #ddd; text-align: center; }
    </style>""",
    unsafe_allow_html=True
)
st.title("🛡️ PANEL ADMIN - ESCANDALLO")

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("⚙️ Configuración")
    pwd = st.text_input("🔑 Contraseña Admin", type="password")
    st.session_state.is_admin = (pwd == "mainsa2024")

    if st.session_state.is_admin:
        st.success("Modo Admin Activo")
    else:
        if pwd:
            st.error("Contraseña incorrecta")

    st.divider()

    with st.expander("🤖 Importar Datos", expanded=False):
        uploaded = st.file_uploader("Subir JSON", type=["json"])
        if uploaded:
            try:
                di = json.load(uploaded)
                if "brf" in di: st.session_state.brf = di["brf"]
                if "cli" in di: st.session_state.cli = di["cli"]
                if "desc" in di: st.session_state.desc = di["desc"]
                if "piezas" in di: st.session_state.piezas_dict = {int(k): v for k, v in di["piezas"].items()}
                if "extras" in di: st.session_state.lista_extras_grabados = di["extras"]
                if "costes_emb" in di: st.session_state.costes_embalaje_manual = di["costes_emb"]
                if "emb_tipo" in di: st.session_state.emb_tipo = di["emb_tipo"]
                if "mermas_imp" in di: st.session_state.mermas_imp_manual = di["mermas_imp"]
                if "mermas_proc" in di: st.session_state.mermas_proc_manual = di["mermas_proc"]
                st.rerun()
            except Exception as e:
                st.error(f"Error importando JSON: {e}")

    st.session_state.brf = st.text_input("Nº Briefing", value=st.session_state.brf)
    st.session_state.cli = st.text_input("Cliente", value=st.session_state.cli)
    st.session_state.desc = st.text_input("Descripción", value=st.session_state.desc)

    st.divider()
    cants_str = st.text_input("Cantidades (ej: 500, 1000)", value="0")
    lista_cants = parse_cantidades(cants_str)

    unidad_t = st.radio("Manipulación:", ["Segundos", "Minutos"], horizontal=True)
    t_input = st.number_input("Tiempo/ud", value=0.0)
    seg_man_total = t_input * 60 if unidad_t == "Minutos" else t_input

    if st.session_state.is_admin:
        st.divider()
        st.markdown("### 💰 Finanzas")
        dif_ud = st.selectbox("Dificultad (€/ud)", [0.02, 0.061, 0.091], index=2)
        imp_fijo_pvp = st.number_input("Fijo PVP (€)", value=500.0)
        margen = st.number_input("Multiplicador", step=0.1, value=2.2)
    else:
        dif_ud, imp_fijo_pvp, margen = 0.091, 500.0, 2.2

    modo_comercial = st.checkbox("🌟 VISTA OFERTA", value=False)

    st.divider()
    st.header("💾 Guardar")
    safe_brf = re.sub(r'[\\/*?:"<>|]', "", (st.session_state.brf or "Ref")).replace(" ", "_")
    safe_cli = re.sub(r'[\\/*?:"<>|]', "", (st.session_state.cli or "Cli")).replace(" ", "_")
    nombre_archivo = f"{safe_brf}_{safe_cli}.json"

    datos_exp = {
        "brf": st.session_state.brf,
        "cli": st.session_state.cli,
        "desc": st.session_state.desc,
        "piezas": st.session_state.piezas_dict,
        "extras": st.session_state.lista_extras_grabados,
        "costes_emb": st.session_state.costes_embalaje_manual,
        "emb_tipo": st.session_state.emb_tipo,
        "mermas_imp": st.session_state.mermas_imp_manual,
        "mermas_proc": st.session_state.mermas_proc_manual,
    }

    st.download_button(
        f"Descargar {nombre_archivo}",
        json.dumps(datos_exp, indent=4, ensure_ascii=False),
        nombre_archivo
    )

# =========================================================
# AUTO-RELLENO DE MERMAS (AQUÍ ESTÁ EL CAMBIO)
# - Se calcula una vez por cantidad en base a la tabla.
# - El modo digital se aplica si EXISTE alguna cara en digital en cualquier pieza.
# - Solo rellena si NO hay valor ya guardado para esa cantidad (no pisa lo manual).
# - Hay un botón para forzar “Recalcular mermas estándar”.
# =========================================================
def hay_digital_en_proyecto() -> bool:
    for p in st.session_state.piezas_dict.values():
        if p.get("im") == "Digital" or p.get("im_d") == "Digital":
            return True
    return False

def autorrellenar_mermas(lista_cants: list[int], force: bool = False):
    es_dig = hay_digital_en_proyecto()
    for q in lista_cants:
        if force or (q not in st.session_state.mermas_proc_manual):
            mp, mi = calcular_mermas_estandar(q, es_digital=es_dig)  # (proceso, impresión)
            st.session_state.mermas_proc_manual[q] = mp
        if force or (q not in st.session_state.mermas_imp_manual):
            mp, mi = calcular_mermas_estandar(q, es_digital=es_dig)
            st.session_state.mermas_imp_manual[q] = mi

# relleno automático “silencioso” cada vez que haya cantidades
if lista_cants:
    autorrellenar_mermas(lista_cants, force=False)

# =========================================================
# TABS
# =========================================================
if st.session_state.is_admin:
    tab_calculadora, tab_costes, tab_debug = st.tabs(["🧮 Calculadora", "💰 Base de Datos", "🔍 Desglose"])
else:
    tab_calculadora, = st.tabs(["🧮 Calculadora Técnica"])
    tab_costes, tab_debug = None, None

# =========================================================
# TAB BASE DE DATOS (ADMIN)
# =========================================================
if tab_costes:
    with tab_costes:
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            with st.expander("📄 Cartoncillo (€/Kg)", expanded=True):
                for k, v in db["cartoncillo"].items():
                    if k != "Ninguno":
                        db["cartoncillo"][k]["precio_kg"] = st.number_input(
                            f"{k} (€/kg)", value=float(v["precio_kg"]), key=f"cost_cart_{k}"
                        )

            with st.expander("🧱 Ondulado y Rígidos (€/hoja)", expanded=True):
                st.markdown("##### Ondulado (Base variable)")
                for k, v in db["planchas"].items():
                    if k != "Ninguna":
                        st.markdown(f"**{k}**")
                        cols = st.columns(len(v))
                        for idx, (sk, sv) in enumerate(v.items()):
                            db["planchas"][k][sk] = cols[idx].number_input(
                                sk, value=float(sv), key=f"cost_pl_{k}_{sk}"
                            )

                st.markdown("---")
                st.markdown("##### Rígidos (HOJA FIJA por material)")
                for k, v in db["rigidos"].items():
                    if k != "Ninguno":
                        db["rigidos"][k]["precio_ud"] = st.number_input(
                            f"{k} ({v['w']}x{v['h']})", value=float(v["precio_ud"]), key=f"cost_rig_{k}"
                        )

        with col_c2:
            with st.expander("✨ Acabados", expanded=True):
                for k, v in db["peliculado"].items():
                    if k != "Sin Peliculado":
                        db["peliculado"][k] = st.number_input(f"{k}", value=float(v), key=f"cost_pel_{k}")
                db["laminado_digital"] = st.number_input("Laminado Digital", value=float(db.get("laminado_digital", 3.5)))

            with st.expander("🔪 Troquelado", expanded=True):
                for k, v in db["troquelado"].items():
                    st.markdown(f"**{k}**")
                    c_arr, c_tir = st.columns(2)
                    db["troquelado"][k]["arranque"] = c_arr.number_input("Arranque (€)", value=float(v["arranque"]), key=f"trq_arr_{k}")
                    db["troquelado"][k]["tiro"] = c_tir.number_input("Tiro (€/hoja)", value=float(v["tiro"]), format="%.4f", key=f"trq_tir_{k}")

            with st.expander("✂️ Plotter", expanded=True):
                db["plotter"]["precio_hoja"] = st.number_input("Corte Plotter (€/hoja)", value=float(db["plotter"]["precio_hoja"]), key="plt_price")

# =========================================================
# TAB CALCULADORA
# =========================================================
with tab_calculadora:
    if not modo_comercial:
        st.header("1. Definición Técnica")

        c_btns = st.columns([1, 4])
        if c_btns[0].button("➕ Forma"):
            nid = max(st.session_state.piezas_dict.keys()) + 1 if st.session_state.piezas_dict else 0
            st.session_state.piezas_dict[nid] = crear_forma_vacia(nid)
            st.rerun()

        if c_btns[1].button("🗑 Reiniciar"):
            st.session_state.piezas_dict = {0: crear_forma_vacia(0)}
            st.session_state.lista_extras_grabados = []
            st.session_state.mermas_imp_manual = {}
            st.session_state.mermas_proc_manual = {}
            st.rerun()

        def callback_medida_estandar(pid: int):
            fmt = st.session_state.get(f"std_{pid}", "Personalizado")
            if fmt != "Personalizado":
                nh, nw = FORMATOS_STD[fmt]
                st.session_state[f"h_{pid}"] = nh
                st.session_state[f"w_{pid}"] = nw
                if not st.session_state.get(f"pldif_{pid}", False):
                    st.session_state[f"plh_{pid}"] = nh
                    st.session_state[f"plw_{pid}"] = nw

        def callback_cambio_frontal(pid: int):
            new_mat = st.session_state.get(f"pf_{pid}", "Ninguno")
            if new_mat != "Ninguno":
                st.session_state[f"gf_{pid}"] = db["cartoncillo"][new_mat]["gramaje"]
                st.session_state[f"im_{pid}"] = "Offset"
                st.session_state[f"nt_{pid}"] = 4
            else:
                st.session_state[f"im_{pid}"] = "No"
                st.session_state[f"nt_{pid}"] = 0

        def callback_cambio_dorso(pid: int):
            new_mat = st.session_state.get(f"pd_{pid}", "Ninguno")
            if new_mat != "Ninguno":
                st.session_state[f"gd_{pid}"] = db["cartoncillo"][new_mat]["gramaje"]

        def callback_rigido_set_medidas(pid: int):
            mat = st.session_state.get(f"mrig_{pid}", "Ninguno")
            if mat and mat != "Ninguno" and mat in db["rigidos"]:
                mw = int(db["rigidos"][mat].get("w", 0))
                mh = int(db["rigidos"][mat].get("h", 0))
                if mw > 0 and mh > 0:
                    st.session_state[f"w_{pid}"] = mw
                    st.session_state[f"h_{pid}"] = mh

        for p_id, p in list(st.session_state.piezas_dict.items()):
            with st.expander(f"🛠 {p.get('nombre','Forma')} - {p.get('h',0)}x{p.get('w',0)} mm", expanded=True):
                col1, col2, col3 = st.columns(3)

                with col1:
                    p["nombre"] = st.text_input("Etiqueta", p.get("nombre", f"Forma {p_id+1}"), key=f"n_{p_id}")
                    p["pliegos"] = st.number_input("Pliegos/Ud", 0.0, 100.0, float(p.get("pliegos", 1.0)), format="%.4f", key=f"p_{p_id}")

                    st.selectbox("Medidas Estándar", list(FORMATOS_STD.keys()), key=f"std_{p_id}",
                                 on_change=callback_medida_estandar, args=(p_id,))

                    c_h, c_w = st.columns(2)
                    p["h"] = c_h.number_input("Largo Papel (mm)", 0, 5000, value=int(p.get("h", 0)), key=f"h_{p_id}")
                    p["w"] = c_w.number_input("Ancho Papel (mm)", 0, 5000, value=int(p.get("w", 0)), key=f"w_{p_id}")

                    opts_im = ["Offset", "Digital", "No"]
                    val_im = p.get("im", "No")
                    p["im"] = st.selectbox("Sistema Cara", opts_im, index=(opts_im.index(val_im) if val_im in opts_im else 2), key=f"im_{p_id}")

                    if p["im"] == "Offset":
                        p["nt"] = st.number_input("Tintas F.", 0, 6, int(p.get("nt", 4)), key=f"nt_{p_id}")
                        p["ba"] = st.checkbox("Barniz F.", value=bool(p.get("ba", False)), key=f"ba_{p_id}")
                        p["ld"] = False
                    elif p["im"] == "Digital":
                        p["ld"] = st.checkbox("Laminado Digital F.", value=bool(p.get("ld", False)), key=f"ld_{p_id}")
                        p["nt"], p["ba"] = 0, False
                    else:
                        p["nt"], p["ba"], p["ld"] = 0, False, False

                    opts_pel = list(db["peliculado"].keys())
                    val_pel = p.get("pel", "Sin Peliculado")
                    p["pel"] = st.selectbox("Peliculado Cara", opts_pel, index=(opts_pel.index(val_pel) if val_pel in opts_pel else 0), key=f"pel_{p_id}")

                with col2:
                    opts_pf = list(db["cartoncillo"].keys())
                    val_pf = p.get("pf", "Ninguno")
                    p["pf"] = st.selectbox("C. Frontal", opts_pf, index=(opts_pf.index(val_pf) if val_pf in opts_pf else 0),
                                           key=f"pf_{p_id}", on_change=callback_cambio_frontal, args=(p_id,))
                    p["gf"] = st.number_input("Gramaje F.", value=int(p.get("gf", 0)), key=f"gf_{p_id}")

                    st.divider()

                    opts_base = ["Ondulado/Cartón", "Material Rígido"]
                    val_tb = p.get("tipo_base", "Ondulado/Cartón")
                    p["tipo_base"] = st.selectbox("Tipo Soporte", opts_base, index=(opts_base.index(val_tb) if val_tb in opts_base else 0), key=f"tb_{p_id}")

                    if p["tipo_base"] == "Ondulado/Cartón":
                        opts_pl = list(db["planchas"].keys())
                        val_pl = p.get("pl", "Ninguna")
                        p["pl"] = st.selectbox("Plancha Base", opts_pl, index=(opts_pl.index(val_pl) if val_pl in opts_pl else 0), key=f"pl_{p_id}")

                        if p["pl"] != "Ninguna":
                            p["pl_dif"] = st.checkbox("📏 Medida Plancha Diferente", value=bool(p.get("pl_dif", False)), key=f"pldif_{p_id}")
                            if p["pl_dif"]:
                                c_ph, c_pw = st.columns(2)
                                p["pl_h"] = c_ph.number_input("Alto Plancha", 0, 5000, value=int(p.get("pl_h", p["h"])), key=f"plh_{p_id}")
                                p["pl_w"] = c_pw.number_input("Ancho Plancha", 0, 5000, value=int(p.get("pl_w", p["w"])), key=f"plw_{p_id}")
                            else:
                                p["pl_h"] = p["h"]
                                p["pl_w"] = p["w"]
                        else:
                            p["pl_dif"], p["pl_h"], p["pl_w"] = False, 0, 0

                        opts_ap = ["C/C", "B/C", "B/B"]
                        val_ap = p.get("ap", "B/C")
                        p["ap"] = st.selectbox("Calidad Ondulado", opts_ap, index=(opts_ap.index(val_ap) if val_ap in opts_ap else 1), key=f"ap_{p_id}")
                    else:
                        opts_rig = list(db["rigidos"].keys())
                        val_rig = p.get("mat_rigido", "Ninguno")
                        p["mat_rigido"] = st.selectbox(
                            "Material Rígido",
                            opts_rig,
                            index=(opts_rig.index(val_rig) if val_rig in opts_rig else 0),
                            key=f"mrig_{p_id}",
                            on_change=callback_rigido_set_medidas,
                            args=(p_id,)
                        )

                        if p["mat_rigido"] != "Ninguno":
                            im_r = db["rigidos"][p["mat_rigido"]]
                            mw, mh = int(im_r["w"]), int(im_r["h"])
                            st.info(f"Hoja fija: {mw}x{mh} mm | Precio: {float(im_r['precio_ud']):.2f}€ / hoja")

                    st.divider()

                    opts_pd = list(db["cartoncillo"].keys())
                    val_pd = p.get("pd", "Ninguno")
                    p["pd"] = st.selectbox("C. Dorso", opts_pd, index=(opts_pd.index(val_pd) if val_pd in opts_pd else 0),
                                           key=f"pd_{p_id}", on_change=callback_cambio_dorso, args=(p_id,))
                    if p["pd"] != "Ninguno":
                        p["gd"] = st.number_input("Gramaje D.", value=int(p.get("gd", 0)), key=f"gd_{p_id}")
                    else:
                        p["gd"] = 0

                with col3:
                    opts_cor = ["Troquelado", "Plotter"]
                    val_cor = p.get("cor", "Troquelado")
                    p["cor"] = st.selectbox("Corte", opts_cor, index=(opts_cor.index(val_cor) if val_cor in opts_cor else 0), key=f"cor_{p_id}")

                    if p["cor"] == "Troquelado":
                        p["cobrar_arreglo"] = st.checkbox("¿Cobrar Arreglo?", value=bool(p.get("cobrar_arreglo", True)), key=f"arr_{p_id}")
                        p["pv_troquel"] = st.number_input("Precio Venta Troquel (€)", value=float(p.get("pv_troquel", 0.0)), key=f"pvt_{p_id}")
                    else:
                        p["cobrar_arreglo"] = False

                    if p.get("pd", "Ninguno") != "Ninguno":
                        opts_imd = ["Offset", "Digital", "No"]
                        val_imd = p.get("im_d", "No")
                        p["im_d"] = st.selectbox("Sistema Dorso", opts_imd, index=(opts_imd.index(val_imd) if val_imd in opts_imd else 2), key=f"imd_{p_id}")
                        if p["im_d"] == "Offset":
                            p["nt_d"] = st.number_input("Tintas D.", 0, 6, int(p.get("nt_d", 0)), key=f"ntd_{p_id}")
                            p["ba_d"] = st.checkbox("Barniz D.", value=bool(p.get("ba_d", False)), key=f"bad_{p_id}")
                            p["ld_d"] = False
                        elif p["im_d"] == "Digital":
                            p["ld_d"] = st.checkbox("Laminado Digital D.", value=bool(p.get("ld_d", False)), key=f"ldd_{p_id}")
                            p["nt_d"], p["ba_d"] = 0, False
                        else:
                            p["nt_d"], p["ba_d"], p["ld_d"] = 0, False, False

                        opts_pel_d = list(db["peliculado"].keys())
                        val_peld = p.get("pel_d", "Sin Peliculado")
                        p["pel_d"] = st.selectbox("Peliculado Dorso", opts_pel_d, index=(opts_pel_d.index(val_peld) if val_peld in opts_pel_d else 0), key=f"peld_{p_id}")
                    else:
                        p["im_d"], p["nt_d"], p["ba_d"], p["ld_d"], p["pel_d"] = "No", 0, False, False, "Sin Peliculado"

                    if st.button("🗑 Borrar Forma", key=f"del_{p_id}"):
                        if len(st.session_state.piezas_dict) > 1:
                            del st.session_state.piezas_dict[p_id]
                            st.rerun()
                        else:
                            st.warning("Debe existir al menos una forma.")

                st.session_state.piezas_dict[p_id] = p

        # ------------------ EXTRAS ------------------
        st.divider()
        st.subheader("📦 2. Almacén de Accesorios")
        c_add_main, c_add_flex = st.columns(2)

        with c_add_main:
            st.markdown("**Extras Mainsa**")
            opts_extra = ["---"] + list(db["extras_base"].keys())
            ex_sel = st.selectbox("Añadir extra estándar:", opts_extra, key="sel_extra_mainsa")
            if st.button("➕ Añadir Mainsa", key="btn_add_mainsa") and ex_sel != "---":
                st.session_state.lista_extras_grabados.append({"nombre": ex_sel, "coste": float(db["extras_base"][ex_sel]), "cantidad": 1.0})
                st.rerun()

        with c_add_flex:
            st.markdown("**Catálogo FLEXICO**")
            flx_sel = st.selectbox("Buscar Ref/Desc:", ["---"] + OPCIONES_FLEXICO, key="sel_extra_flexico")
            if st.button("➕ Añadir Flexico", key="btn_add_flexico") and flx_sel != "---":
                cod = flx_sel.split(" - ")[0]
                prod = PRODUCTOS_FLEXICO[cod]
                st.session_state.lista_extras_grabados.append({"nombre": f"FLEXICO: {prod['desc']}", "coste": float(prod["precio"]), "cantidad": 1.0})
                st.rerun()

        for i, ex in enumerate(st.session_state.lista_extras_grabados):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            c1.write(f"**{ex['nombre']}**")
            if st.session_state.is_admin:
                ex["coste"] = c2.number_input("€/ud compra", value=float(ex["coste"]), key=f"exc_{i}", format="%.4f")
            else:
                c2.write(f"{float(ex['coste']):.4f}€")
            ex["cantidad"] = c3.number_input("Cant/Ud prod", value=float(ex["cantidad"]), key=f"exq_{i}")
            if c4.button("🗑", key=f"exd_{i}"):
                st.session_state.lista_extras_grabados.pop(i)
                st.rerun()

        # ------------------ EMBALAJE ------------------
        st.divider()
        st.subheader("📦 3. Embalaje")
        tipos_emb = ["Manual", "Embalaje Guaina (Automático)", "Embalaje en Plano (Pendiente)", "Embalaje en Volumen (Pendiente)"]
        idx_emb = tipos_emb.index(st.session_state.emb_tipo) if st.session_state.emb_tipo in tipos_emb else 0
        st.session_state.emb_tipo = st.selectbox("Selecciona el tipo de embalaje:", tipos_emb, index=idx_emb)

        if lista_cants:
            if st.session_state.emb_tipo == "Embalaje Guaina (Automático)":
                d1, d2, d3 = st.columns(3)
                L = d1.number_input("Largo mm", value=float(st.session_state.emb_dims["L"]))
                W = d2.number_input("Ancho mm", value=float(st.session_state.emb_dims["W"]))
                H = d3.number_input("Alto mm", value=float(st.session_state.emb_dims["H"]))
                st.session_state.emb_dims = {"L": L, "W": W, "H": H}

                sup_m2 = ((2 * (L + W) * H) + (L * W)) / 1_000_000 if (L > 0 and W > 0 and H > 0) else 0.0
                cols = st.columns(len(lista_cants))
                for idx, q in enumerate(lista_cants):
                    coste_auto = (sup_m2 * 0.70) + (30 / q) if q > 0 else 0.0
                    st.session_state.costes_embalaje_manual[q] = float(coste_auto)
                    if st.session_state.is_admin:
                        cols[idx].metric(f"{q} uds", f"{coste_auto:.3f}€")
                    else:
                        cols[idx].write(f"**{q} uds**: Calculado")
            else:
                cols = st.columns(len(lista_cants))
                for idx, q in enumerate(lista_cants):
                    if st.session_state.is_admin:
                        st.session_state.costes_embalaje_manual[q] = cols[idx].number_input(
                            f"Coste {q} uds", value=float(st.session_state.costes_embalaje_manual.get(q, 0.0)), key=f"em_{q}"
                        )
                    else:
                        cols[idx].write(f"**{q} uds**: Manual")
        else:
            st.warning("Define cantidades primero.")

        # ------------------ MERMAS (ahora con autorrelleno y botón) ------------------
        st.divider()
        st.subheader("⚙️ 4. Gestión de Mermas (AUTO + editable)")

        if lista_cants:
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.caption("Autorrelleno según tabla estándar")
                if st.button("♻️ Recalcular mermas estándar (pisar todo)"):
                    autorrellenar_mermas(lista_cants, force=True)
                    st.rerun()

            with col_b:
                es_dig = hay_digital_en_proyecto()
                st.info(f"Modo de tabla aplicado: {'DIGITAL' if es_dig else 'OFFSET/GENERAL'} (si hay alguna cara Digital en el proyecto => DIGITAL)")

            for q in lista_cants:
                c1, c2, c3 = st.columns([1, 2, 2])
                c1.markdown(f"**{q} uds**")

                # IMPORTANTE: ya están autorrellenadas arriba, aquí solo se editan
                st.session_state.mermas_imp_manual[q] = c2.number_input(
                    "Merma impresión (hojas)",
                    value=int(st.session_state.mermas_imp_manual.get(q, 0)),
                    key=f"mi_{q}"
                )
                st.session_state.mermas_proc_manual[q] = c3.number_input(
                    "Merma proceso (hojas)",
                    value=int(st.session_state.mermas_proc_manual.get(q, 0)),
                    key=f"mp_{q}"
                )
        else:
            st.warning("Define cantidades primero.")

    # =========================================================
    # MOTOR DE CÁLCULO
    # =========================================================
    def calcular_para_cantidad(q_n: int) -> dict:
        piezas = st.session_state.piezas_dict
        extras = st.session_state.lista_extras_grabados

        merma_imp = float(st.session_state.mermas_imp_manual.get(q_n, 0))
        merma_proc = float(st.session_state.mermas_proc_manual.get(q_n, 0))

        coste_emb_unit_compra = float(st.session_state.costes_embalaje_manual.get(q_n, 0.0))
        pv_emb_total = coste_emb_unit_compra * 1.4 * q_n
        tot_pv_trq = sum(float(pz.get("pv_troquel", 0.0)) for pz in piezas.values())

        coste_total_piezas = 0.0
        det_f = []
        debug_log = []

        tech_hojas_papel = 0.0
        tech_planchas_rigidas = 0

        def _fmt(x, nd=4):
            try:
                return f"{float(x):.{nd}f}"
            except Exception:
                return str(x)

        def _fmt_eur(x):
            try:
                return f"{float(x):.2f}€"
            except Exception:
                return f"{x}€"

        def dbg_title(txt):
            debug_log.append("<hr style='margin:10px 0'>")
            debug_log.append(f"<h4 style='margin:4px 0'>🧩 {txt}</h4>")

        def dbg_step(label, formula, calc, result=None):
            if result is None:
                debug_log.append(
                    f"<div style='font-family:monospace; line-height:1.35; margin:2px 0;'>"
                    f"<b>{label}</b><br>"
                    f"  • Fórmula: {formula}<br>"
                    f"  • Cálculo: {calc}"
                    f"</div>"
                )
            else:
                debug_log.append(
                    f"<div style='font-family:monospace; line-height:1.35; margin:2px 0;'>"
                    f"<b>{label}</b><br>"
                    f"  • Fórmula: {formula}<br>"
                    f"  • Cálculo: {calc}<br>"
                    f"  • Resultado: <b>{result}</b>"
                    f"</div>"
                )

        for pid, p in piezas.items():
            c_cf = c_cd = c_pl = c_peg = c_imp = c_pel = c_trq = c_plot = 0.0

            pliegos = float(p.get("pliegos", 1.0))
            nb = q_n * pliegos
            hp_produccion = nb + merma_proc

            hp_papel_f = hp_produccion + merma_imp if p.get("im", "No") != "No" else hp_produccion
            hp_papel_d = hp_produccion + merma_imp if p.get("im_d", "No") != "No" else hp_produccion

            w = float(p.get("w", 0))
            h = float(p.get("h", 0))
            m2_papel = (w * h) / 1_000_000 if (w > 0 and h > 0) else 0.0

            tech_hojas_papel += hp_papel_f

            dbg_title(f"PIEZA: {p.get('nombre','(sin nombre)')}")
            dbg_step("Datos mermas", "merma_imp, merma_proc", f"merma_imp={_fmt(merma_imp,0)} hojas | merma_proc={_fmt(merma_proc,0)} hojas")

            # SOPORTE RÍGIDO
            if p.get("tipo_base") == "Material Rígido" and p.get("mat_rigido") != "Ninguno":
                im_r = db["rigidos"].get(p["mat_rigido"])
                if im_r:
                    mw = int(im_r.get("w", 0))
                    mh = int(im_r.get("h", 0))
                    pw = int(p.get("w", 0))
                    ph = int(p.get("h", 0))
                    precio_pl = float(im_r.get("precio_ud", 0.0))

                    fit1 = (mw // pw) * (mh // ph) if pw and ph else 0
                    fit2 = (mw // ph) * (mh // pw) if pw and ph else 0
                    by = max(fit1, fit2)

                    if by > 0:
                        hojas_base = float(hp_produccion)
                        hojas_con_merma = hojas_base * (1.0 + MERMA_RIGIDO_PCT)
                        n_pl = int(math.ceil(hojas_con_merma / float(by)))
                        c_pl = n_pl * precio_pl
                        tech_planchas_rigidas += n_pl

                        dbg_step("Rígido: hojas a comprar", "ceil((hp_produccion*(1+merma%))/by)", f"ceil(({_fmt(hp_produccion,2)}*(1+{_fmt(MERMA_RIGIDO_PCT,4)}))/{by})={n_pl}", f"{n_pl} hojas")
                        dbg_step("Rígido: coste", "c_pl=n_pl*€/hoja", f"{n_pl}*{_fmt(precio_pl,2)}={_fmt(c_pl,2)}", _fmt_eur(c_pl))
                    else:
                        dbg_step("Rígido: ERROR", "by debe ser >=1", f"Hoja {mw}x{mh} vs pieza {pw}x{ph} => by={by}", "NO CABE")

            # SOPORTE ONDULADO
            else:
                if p.get("pl_dif", False) and float(p.get("pl_h", 0)) > 0 and float(p.get("pl_w", 0)) > 0:
                    m2_plancha = (float(p["pl_w"]) * float(p["pl_h"])) / 1_000_000
                else:
                    m2_plancha = m2_papel

                if p.get("pl") != "Ninguna" and m2_plancha > 0:
                    precio_m2 = float(db["planchas"][p["pl"]][p.get("ap", "B/C")])
                    c_pl = hp_produccion * m2_plancha * precio_m2

                    peg_m2 = float(db["planchas"][p["pl"]]["peg"])
                    if p.get("pf") != "Ninguno":
                        c_peg = hp_produccion * m2_plancha * peg_m2

            # PAPEL
            pf = p.get("pf", "Ninguno")
            gf = float(p.get("gf", 0))
            if pf != "Ninguno" and m2_papel > 0:
                precio_kg_pf = float(db["cartoncillo"][pf]["precio_kg"])
                c_cf = hp_papel_f * m2_papel * (gf / 1000.0) * precio_kg_pf

            pd_ = p.get("pd", "Ninguno")
            gd = float(p.get("gd", 0))
            if pd_ != "Ninguno" and m2_papel > 0:
                precio_kg_pd = float(db["cartoncillo"][pd_]["precio_kg"])
                c_cd = hp_papel_d * m2_papel * (gd / 1000.0) * precio_kg_pd

            # IMPRESIÓN
            c_imp_f = 0.0
            if p.get("im") == "Digital":
                c_imp_f = hp_papel_f * m2_papel * 6.5
            elif p.get("im") == "Offset":
                base = f_offset(nb)
                nt = int(p.get("nt", 0))
                barn = 1 if p.get("ba", False) else 0
                c_imp_f = base * (nt + barn)

            c_imp_d = 0.0
            if p.get("im_d") == "Digital":
                c_imp_d = hp_papel_d * m2_papel * 6.5
            elif p.get("im_d") == "Offset":
                base = f_offset(nb)
                nt = int(p.get("nt_d", 0))
                barn = 1 if p.get("ba_d", False) else 0
                c_imp_d = base * (nt + barn)

            c_imp = c_imp_f + c_imp_d

            # PELICULADO
            pel_f = p.get("pel", "Sin Peliculado")
            pel_d = p.get("pel_d", "Sin Peliculado")
            c_pel_f = 0.0 if pel_f == "Sin Peliculado" else (hp_produccion * m2_papel * float(db["peliculado"][pel_f]))
            c_pel_d = 0.0 if pel_d == "Sin Peliculado" else (hp_produccion * m2_papel * float(db["peliculado"][pel_d]))
            c_pel = c_pel_f + c_pel_d

            # CORTE
            cat = categoria_troquel(h, w)
            if p.get("cor") == "Troquelado":
                arr = float(db["troquelado"][cat]["arranque"]) if p.get("cobrar_arreglo", True) else 0.0
                tiro = float(db["troquelado"][cat]["tiro"])
                c_trq = arr + (hp_produccion * tiro)
            else:
                precio_hoja = float(db["plotter"]["precio_hoja"])
                c_plot = hp_produccion * precio_hoja

            sub = c_cf + c_cd + c_pl + c_imp + c_peg + c_pel + c_trq + c_plot
            coste_total_piezas += sub

            total_mat = c_cf + c_cd + c_pl
            total_narba = c_peg + c_pel + c_trq + c_plot

            det_f.append({
                "Pieza": p.get("nombre", f"Forma {pid+1}"),
                "Mat. Papel": (c_cf + c_cd),
                "Mat. Soporte": c_pl,
                "Total Mat": total_mat,
                "Imp. Total": c_imp,
                "Total Narba": total_narba,
                "Subtotal": sub,
            })

        # EXTRAS
        c_ext = sum(float(e.get("coste", 0)) * float(e.get("cantidad", 0)) * q_n for e in extras)

        # MO
        c_mo = ((float(seg_man_total) / 3600.0) * 18.0 * q_n) + (q_n * float(dif_ud))

        # Taller
        taller = coste_total_piezas + c_ext + c_mo

        # PVP
        pvp_total = (taller * float(margen)) + float(imp_fijo_pvp) + pv_emb_total + tot_pv_trq
        unitario = (pvp_total / q_n) if q_n > 0 else 0.0

        return {
            "q": q_n,
            "pvp_total": pvp_total,
            "unitario": unitario,
            "tech": {
                "Hojas Papel": tech_hojas_papel,
                "Hojas Rígidas (compradas)": tech_planchas_rigidas,
                "Embalaje_u": coste_emb_unit_compra,
            },
            "detalle": det_f,
            "debug": debug_log,
            "taller": taller,
        }

    # Ejecutar cálculo
    res_final = []
    res_tecnico = []
    desc_full = {}

    if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
        for q_n in lista_cants:
            r = calcular_para_cantidad(q_n)
            res_final.append({
                "Cantidad": q_n,
                "Precio Venta Total": f"{r['pvp_total']:.2f}€",
                "Unitario (Todo Incluido)": f"{r['unitario']:.3f}€",
            })
            res_tecnico.append({
                "Cantidad": q_n,
                "Hojas Papel": f"{r['tech']['Hojas Papel']:.0f}",
                "Hojas Rígidas": f"{r['tech']['Hojas Rígidas (compradas)']}",
                "Embalaje": f"{r['tech']['Embalaje_u']:.2f}€/u",
            })
            desc_full[q_n] = {"det": r["detalle"], "debug": r["debug"], "taller": r["taller"]}

    # Salida visual
    if st.session_state.is_admin:
        if modo_comercial and res_final:
            desc_html = """<div style='text-align: left; margin-bottom: 20px; color: #444;'>
            <h4 style='color: #1E88E5; margin-bottom: 5px;'>📋 Especificaciones del Proyecto</h4>
            <ul style='list-style-type: none; padding-left: 0;'>"""
            for p in st.session_state.piezas_dict.values():
                if p.get("tipo_base") == "Material Rígido":
                    base_info = f"Rígido: {p.get('mat_rigido','Ninguno')}"
                else:
                    base_info = f"Base: {p.get('pl','Ninguna')} ({p.get('ap','B/C')})"
                desc_html += f"<li>🔹 <b>{p.get('nombre','')}</b>: {p.get('h',0)}x{p.get('w',0)}mm | {base_info}</li>"
            desc_html += "</ul></div>"

            rows_html = ""
            for r in res_final:
                rows_html += f"<tr><td>{r['Cantidad']}</td><td>{r['Precio Venta Total']}</td><td>{r['Unitario (Todo Incluido)']}</td></tr>"

            st.markdown(
                f"""<div class="comercial-box">
                    <h2 class="comercial-header">OFERTA: {st.session_state.cli}</h2>
                    {desc_html}
                    <table class="comercial-table">
                        <tr><th>Cant</th><th>TOTAL</th><th>UNITARIO</th></tr>
                        {rows_html}
                    </table>
                </div>""",
                unsafe_allow_html=True
            )
        else:
            if res_final:
                st.header(f"📊 Resumen de Venta: {st.session_state.cli}")
                df_simple = pd.DataFrame(res_final)[["Cantidad", "Precio Venta Total", "Unitario (Todo Incluido)"]]
                st.dataframe(df_simple, use_container_width=True)

                for q, info in desc_full.items():
                    with st.expander(f"🔍 Auditoría Taller {q} uds"):
                        df_raw = pd.DataFrame(info["det"])
                        st.table(df_raw.style.format("{:.2f}€", subset=[c for c in df_raw.columns if c != "Pieza"]))
                        st.metric("COSTO TALLER", f"{info['taller']:.2f}€")
    else:
        if res_tecnico:
            st.success("✅ Cálculo Realizado")
            st.table(pd.DataFrame(res_tecnico))

# =========================================================
# TAB DEBUG (ADMIN)
# =========================================================
if tab_debug:
    with tab_debug:
        if lista_cants and desc_full:
            st.subheader("🔍 Desglose")
            sq = st.selectbox("Ver detalle para cantidad:", lista_cants)
            for l in desc_full[sq]["debug"]:
                st.markdown(l, unsafe_allow_html=True)
        else:
            st.info("No hay desglose aún. Define cantidades y piezas.")
