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

        "PVC TRANSPARENTE 300 MICRAS": {"precio_ud": 1.80, "w": 1000, "h": 700},
        "PVC TRANSPARENTE 500 MICRAS": {"precio_ud": 2.99, "w": 1000, "h": 700},
        "PVC TRANSPARENTE 700 MICRAS": {"precio_ud": 4.22, "w": 1000, "h": 700},
        "PVC BLANCO MATE 300 MICRAS": {"precio_ud": 1.76, "w": 1000, "h": 700},
        "PVC BLANCO MATE 500 MICRAS": {"precio_ud": 2.94, "w": 1000, "h": 700},
        "PVC BLANCO MATE 700 MICRAS": {"precio_ud": 4.11, "w": 1000, "h": 700},

        "APET 300 MICRAS": {"precio_ud": 1.35, "w": 1000, "h": 700},
        "APET 500 MICRAS": {"precio_ud": 2.25, "w": 1000, "h": 700},

        "PET G 0,5mm": {"precio_ud": 8.87, "w": 1250, "h": 2050},
        "PET G 0,7mm": {"precio_ud": 11.22, "w": 1250, "h": 2050},
        "PET G 1mm": {"precio_ud": 13.61, "w": 1250, "h": 2050},

        "POLIPROPILENO COMPACTO BLANCO/ NATURAL 300 MICRAS": {"precio_ud": 1.00, "w": 1000, "h": 700},
        "POLIPROPILENO COMPACTO BLANCO/ NATURAL 500 MICRAS": {"precio_ud": 1.67, "w": 1000, "h": 700},
        "POLIPROPILENO COMPACTO BLANCO/ NATURAL 800 MICRAS": {"precio_ud": 2.67, "w": 1000, "h": 700},

        "COMPACTO 1,5 MM": {"precio_ud": 1.80, "w": 1050, "h": 750},
        "COMPACTO 2 MM": {"precio_ud": 2.15, "w": 1050, "h": 750},
        "COMPACTO 3 MM": {"precio_ud": 3.00, "w": 1050, "h": 750},

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
# EMBALAJE EN PLANO (COMPRA) - FORMULA
# P ≈ ((152 + 20*S)/Q) + 0.15 + (1.02*S)
# S = (L*W) + 2*H*(L+W)
# =========================================================
def coste_embalaje_plano_unitario(L_mm: float, W_mm: float, H_mm: float, Q: int):
    if Q <= 0:
        return 0.0, 0.0
    if L_mm <= 0 or W_mm <= 0 or H_mm <= 0:
        return 0.0, 0.0

    L = L_mm / 1000.0
    W = W_mm / 1000.0
    H = H_mm / 1000.0

    S = (L * W) + 2.0 * H * (L + W)  # m²
    P = ((152.0 + (20.0 * S)) / float(Q)) + 0.15 + (1.02 * S)
    return float(P), float(S)

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
    st.session_state.emb_dims = {"L": 0.0, "W": 0.0, "H": 0.0}
if "brf" not in st.session_state:
    st.session_state.brf = ""
if "cli" not in st.session_state:
    st.session_state.cli = ""
if "desc" not in st.session_state:
    st.session_state.desc = ""
if "cants_str_saved" not in st.session_state:
    st.session_state.cants_str_saved = "0"

db = st.session_state.db_precios

# =========================================================
# UI STYLE + TITLE
# =========================================================
st.markdown(
    """<style>
    .offer-wrap { background:#fff; border:2px solid #1E88E5; border-radius:14px; padding:22px; color:#222; }
    .offer-title { font-size:28px; font-weight:800; color:#1E88E5; margin:0; }
    .offer-sub { font-size:14px; color:#555; margin-top:2px; margin-bottom:16px; }
    .sec { margin-top:14px; }
    .sec h3 { margin:0 0 10px 0; font-size:18px; color:#1E88E5; }
    .grid { display:grid; grid-template-columns: 1fr 1fr; gap:10px; }
    .card { border:1px solid #e6e6e6; border-radius:12px; padding:12px; background:#fafafa; }
    .k { color:#666; font-size:12px; margin-bottom:2px; }
    .v { font-size:14px; font-weight:600; }
    .tbl { width:100%; border-collapse:collapse; margin-top:10px; font-size:14px; }
    .tbl th { background:#1E88E5; color:#fff; padding:10px; text-align:center; }
    .tbl td { border:1px solid #e6e6e6; padding:10px; text-align:center; }
    .tbl .rowh { text-align:left; font-weight:700; background:#f5f7ff; }
    .muted { color:#666; font-size:12px; }
    </style>""",
    unsafe_allow_html=True
)
st.title("🛡️ PANEL ADMIN - ESCANDALLO")

# =========================================================
# IMPORT/EXPORT COMPLETO (JSON)
# =========================================================
def normalizar_import(di: dict):
    if "brf" in di: st.session_state.brf = di["brf"]
    if "cli" in di: st.session_state.cli = di["cli"]
    if "desc" in di: st.session_state.desc = di["desc"]

    if "cants_str" in di and isinstance(di["cants_str"], str):
        st.session_state.cants_str_saved = di["cants_str"]

    if "db_precios" in di and isinstance(di["db_precios"], dict):
        st.session_state.db_precios = di["db_precios"]

    if "piezas" in di and isinstance(di["piezas"], dict):
        st.session_state.piezas_dict = {int(k): v for k, v in di["piezas"].items()}

    if "extras" in di and isinstance(di["extras"], list):
        st.session_state.lista_extras_grabados = di["extras"]

    if "costes_emb" in di and isinstance(di["costes_emb"], dict):
        st.session_state.costes_embalaje_manual = {int(k): float(v) for k, v in di["costes_emb"].items()}
    if "emb_tipo" in di:
        st.session_state.emb_tipo = di["emb_tipo"]
    if "emb_dims" in di and isinstance(di["emb_dims"], dict):
        st.session_state.emb_dims = di["emb_dims"]

    if "mermas_imp" in di and isinstance(di["mermas_imp"], dict):
        st.session_state.mermas_imp_manual = {int(k): int(v) for k, v in di["mermas_imp"].items()}
    if "mermas_proc" in di and isinstance(di["mermas_proc"], dict):
        st.session_state.mermas_proc_manual = {int(k): int(v) for k, v in di["mermas_proc"].items()}

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

    with st.expander("🤖 Importar Datos (JSON completo)", expanded=False):
        uploaded = st.file_uploader("Subir JSON", type=["json"])
        if uploaded:
            try:
                di = json.load(uploaded)
                normalizar_import(di)
                st.success("Importación completa OK")
                st.rerun()
            except Exception as e:
                st.error(f"Error importando JSON: {e}")

    st.session_state.brf = st.text_input("Nº Briefing", value=st.session_state.brf)
    st.session_state.cli = st.text_input("Cliente", value=st.session_state.cli)
    st.session_state.desc = st.text_input("Descripción", value=st.session_state.desc)

    st.divider()
    cants_str = st.text_input("Cantidades (ej: 500, 1000)", value=st.session_state.cants_str_saved)
    st.session_state.cants_str_saved = cants_str
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

    # VISTA OFERTA (para pantallazo)
    modo_comercial = st.checkbox("🌟 VISTA OFERTA", value=False)

    st.divider()
    st.header("💾 Guardar (JSON completo)")

    safe_brf = re.sub(r'[\\/*?:"<>|]', "", (st.session_state.brf or "Ref")).replace(" ", "_")
    safe_cli = re.sub(r'[\\/*?:"<>|]', "", (st.session_state.cli or "Cli")).replace(" ", "_")
    nombre_archivo = f"{safe_brf}_{safe_cli}.json"

    datos_exp = {
        "brf": st.session_state.brf,
        "cli": st.session_state.cli,
        "desc": st.session_state.desc,

        "cants_str": st.session_state.cants_str_saved,
        "piezas": st.session_state.piezas_dict,
        "extras": st.session_state.lista_extras_grabados,

        "db_precios": st.session_state.db_precios,

        "costes_emb": st.session_state.costes_embalaje_manual,
        "emb_tipo": st.session_state.emb_tipo,
        "emb_dims": st.session_state.emb_dims,

        "mermas_imp": st.session_state.mermas_imp_manual,
        "mermas_proc": st.session_state.mermas_proc_manual,
    }

    st.download_button(
        f"Descargar {nombre_archivo}",
        json.dumps(datos_exp, indent=4, ensure_ascii=False),
        nombre_archivo
    )

# =========================================================
# AUTO-RELLENO DE MERMAS (NO pisa personalizadas)
# =========================================================
def hay_digital_en_proyecto() -> bool:
    for p in st.session_state.piezas_dict.values():
        if p.get("im") == "Digital" or p.get("im_d") == "Digital":
            return True
    return False

def autorrellenar_mermas(lista_cants: list[int], force: bool = False):
    es_dig = hay_digital_en_proyecto()
    for q in lista_cants:
        mp, mi = calcular_mermas_estandar(q, es_digital=es_dig)  # (proceso, impresión)
        if force or (q not in st.session_state.mermas_proc_manual):
            st.session_state.mermas_proc_manual[q] = mp
        if force or (q not in st.session_state.mermas_imp_manual):
            st.session_state.mermas_imp_manual[q] = mi

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
                            f"{k} ({v['w']}x{v['h']})",
                            value=float(v["precio_ud"]),
                            key=f"cost_rig_{k}"
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
            st.session_state.costes_embalaje_manual = {}
            st.session_state.emb_dims = {"L": 0.0, "W": 0.0, "H": 0.0}
            st.session_state.emb_tipo = "Manual"
            st.session_state.db_precios = deepcopy(PRECIOS_BASE)
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

        def callback_rigido_set_medidas(pid: int):
            mat = st.session_state.get(f"mrig_{pid}", "Ninguno")
            if mat and mat != "Ninguno" and mat in db["rigidos"]:
                mw = int(db["rigidos"][mat].get("w", 0))
                mh = int(db["rigidos"][mat].get("h", 0))
                if mw > 0 and mh > 0:
                    st.session_state[f"w_{pid}"] = mw
                    st.session_state[f"h_{pid}"] = mh

        # ---- FORMAS UI ----
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
                            st.info(f"Hoja fija: {int(im_r['w'])}x{int(im_r['h'])} mm | Precio: {float(im_r['precio_ud']):.2f}€ / hoja")

                with col3:
                    opts_cor = ["Troquelado", "Plotter"]
                    val_cor = p.get("cor", "Troquelado")
                    p["cor"] = st.selectbox("Corte", opts_cor, index=(opts_cor.index(val_cor) if val_cor in opts_cor else 0), key=f"cor_{p_id}")

                    if p["cor"] == "Troquelado":
                        p["cobrar_arreglo"] = st.checkbox("¿Cobrar Arreglo?", value=bool(p.get("cobrar_arreglo", True)), key=f"arr_{p_id}")
                        p["pv_troquel"] = st.number_input("Precio Venta Troquel (€)", value=float(p.get("pv_troquel", 0.0)), key=f"pvt_{p_id}")
                    else:
                        p["cobrar_arreglo"] = False

                    if st.button("🗑 Borrar Forma", key=f"del_{p_id}"):
                        if len(st.session_state.piezas_dict) > 1:
                            del st.session_state.piezas_dict[p_id]
                            st.rerun()
                        else:
                            st.warning("Debe existir al menos una forma.")

                st.session_state.piezas_dict[p_id] = p

        # --- EXTRAS ---
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

        # --- EMBALAJE ---
        st.divider()
        st.subheader("📦 3. Embalaje")

        tipos_emb = ["Manual", "Embalaje Guaina (Automático)", "Embalaje en Plano", "Embalaje en Volumen (Pendiente)"]
        idx_emb = tipos_emb.index(st.session_state.emb_tipo) if st.session_state.emb_tipo in tipos_emb else 0
        st.session_state.emb_tipo = st.selectbox("Selecciona el tipo de embalaje:", tipos_emb, index=idx_emb)

        if lista_cants:
            if st.session_state.emb_tipo in ["Embalaje Guaina (Automático)", "Embalaje en Plano"]:
                d1, d2, d3 = st.columns(3)
                L = d1.number_input("Largo mm", value=float(st.session_state.emb_dims["L"]))
                W = d2.number_input("Ancho mm", value=float(st.session_state.emb_dims["W"]))
                H = d3.number_input("Alto mm", value=float(st.session_state.emb_dims["H"]))
                st.session_state.emb_dims = {"L": float(L), "W": float(W), "H": float(H)}

            cols = st.columns(len(lista_cants))
            for idx, q in enumerate(lista_cants):
                if q <= 0:
                    continue

                if st.session_state.emb_tipo == "Embalaje Guaina (Automático)":
                    Lmm, Wmm, Hmm = float(st.session_state.emb_dims["L"]), float(st.session_state.emb_dims["W"]), float(st.session_state.emb_dims["H"])
                    sup_m2 = ((2 * (Lmm + Wmm) * Hmm) + (Lmm * Wmm)) / 1_000_000 if (Lmm > 0 and Wmm > 0 and Hmm > 0) else 0.0
                    coste_unit_compra = (sup_m2 * 0.70) + (30 / q) if sup_m2 > 0 else (30 / q)
                    st.session_state.costes_embalaje_manual[q] = float(coste_unit_compra)

                    if st.session_state.is_admin:
                        cols[idx].metric(f"{q} uds", f"{coste_unit_compra:.3f}€")
                    else:
                        cols[idx].write(f"**{q} uds**: Calculado")

                elif st.session_state.emb_tipo == "Embalaje en Plano":
                    Lmm, Wmm, Hmm = float(st.session_state.emb_dims["L"]), float(st.session_state.emb_dims["W"]), float(st.session_state.emb_dims["H"])
                    coste_unit_compra, S = coste_embalaje_plano_unitario(Lmm, Wmm, Hmm, q)
                    st.session_state.costes_embalaje_manual[q] = float(coste_unit_compra)

                    if st.session_state.is_admin:
                        cols[idx].metric(f"{q} uds", f"{coste_unit_compra:.3f}€")
                        if S > 0:
                            cols[idx].caption(f"S={S:.3f} m²")
                    else:
                        cols[idx].write(f"**{q} uds**: Calculado")

                elif st.session_state.emb_tipo == "Manual":
                    if st.session_state.is_admin:
                        st.session_state.costes_embalaje_manual[q] = cols[idx].number_input(
                            f"Coste {q} uds", value=float(st.session_state.costes_embalaje_manual.get(q, 0.0)), key=f"em_{q}"
                        )
                    else:
                        cols[idx].write(f"**{q} uds**: Manual")
                else:
                    cols[idx].write("Pendiente")

        else:
            st.warning("Define cantidades primero.")

        # --- MERMAS ---
        st.divider()
        st.subheader("⚙️ 4. Gestión de Mermas (AUTO + editable)")
        if lista_cants:
            if st.button("♻️ Recalcular mermas estándar (pisar todo)"):
                autorrellenar_mermas(lista_cants, force=True)
                st.rerun()

            for q in lista_cants:
                c1, c2, c3 = st.columns([1, 2, 2])
                c1.markdown(f"**{q} uds**")
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
# MOTOR DE CÁLCULO (AUDITORÍA + OFERTA)
# =========================================================
def calcular_costes_con_auditoria(q_n: int) -> dict:
    piezas = st.session_state.piezas_dict
    extras = st.session_state.lista_extras_grabados

    merma_imp = float(st.session_state.mermas_imp_manual.get(q_n, 0))
    merma_proc = float(st.session_state.mermas_proc_manual.get(q_n, 0))

    detalle = []
    debug = []

    aud = {
        "MATERIAL_CARTONCILLO": 0.0,
        "MATERIAL_BASE_ONDULADO": 0.0,
        "MATERIAL_BASE_RIGIDO": 0.0,
        "IMPRESION": 0.0,
        "ACABADO_PELICULADO": 0.0,
        "ACABADO_CONTRACOLADO": 0.0,
        "CORTE_TROQUEL": 0.0,
        "CORTE_PLOTTER": 0.0,
        "EXTRAS_ACCESORIOS": 0.0,
        "MANO_DE_OBRA": 0.0,
    }

    for _, p in piezas.items():
        nombre = p.get("nombre", "Pieza")

        pliegos = float(p.get("pliegos", 1.0))
        nb = q_n * pliegos

        hp_produccion = nb + merma_proc
        hp_papel_f = hp_produccion + merma_imp if p.get("im", "No") != "No" else hp_produccion
        hp_papel_d = hp_produccion + merma_imp if p.get("im_d", "No") != "No" else hp_produccion

        w = float(p.get("w", 0))
        h = float(p.get("h", 0))
        m2_papel = (w * h) / 1_000_000 if (w > 0 and h > 0) else 0.0

        # Costes pieza
        c_carton = 0.0
        c_ond = 0.0
        c_rig = 0.0
        c_peg = 0.0
        c_imp = 0.0
        c_pel = 0.0
        c_trq = 0.0
        c_plot = 0.0

        # BASE
        if p.get("tipo_base") == "Material Rígido" and p.get("mat_rigido") != "Ninguno":
            im_r = db["rigidos"].get(p["mat_rigido"])
            if im_r:
                mw = int(im_r.get("w", 0))
                mh = int(im_r.get("h", 0))
                pw = int(p.get("w", 0))
                ph = int(p.get("h", 0))
                precio_hoja = float(im_r.get("precio_ud", 0.0))

                fit1 = (mw // pw) * (mh // ph) if pw and ph else 0
                fit2 = (mw // ph) * (mh // pw) if pw and ph else 0
                by = max(fit1, fit2)

                if by > 0:
                    hojas_base = float(hp_produccion)
                    hojas_con_merma = hojas_base * (1.0 + MERMA_RIGIDO_PCT)
                    n_hojas = int(math.ceil(hojas_con_merma / float(by)))
                    c_rig = n_hojas * precio_hoja
        else:
            # Ondulado
            if p.get("pl_dif", False) and float(p.get("pl_h", 0)) > 0 and float(p.get("pl_w", 0)) > 0:
                m2_plancha = (float(p["pl_w"]) * float(p["pl_h"])) / 1_000_000
            else:
                m2_plancha = m2_papel

            if p.get("pl") != "Ninguna" and m2_plancha > 0:
                precio_m2 = float(db["planchas"][p["pl"]][p.get("ap", "B/C")])
                c_ond = hp_produccion * m2_plancha * precio_m2
                if p.get("pf") != "Ninguno":
                    peg_m2 = float(db["planchas"][p["pl"]]["peg"])
                    c_peg = hp_produccion * m2_plancha * peg_m2

        # CARTONCILLO
        pf = p.get("pf", "Ninguno")
        gf = float(p.get("gf", 0))
        if pf != "Ninguno" and m2_papel > 0 and gf > 0:
            precio_kg_pf = float(db["cartoncillo"][pf]["precio_kg"])
            c_cf = hp_papel_f * m2_papel * (gf / 1000.0) * precio_kg_pf
            c_carton += c_cf

        pd_ = p.get("pd", "Ninguno")
        gd = float(p.get("gd", 0))
        if pd_ != "Ninguno" and m2_papel > 0 and gd > 0:
            precio_kg_pd = float(db["cartoncillo"][pd_]["precio_kg"])
            c_cd = hp_papel_d * m2_papel * (gd / 1000.0) * precio_kg_pd
            c_carton += c_cd

        # IMPRESIÓN
        c_imp_f = 0.0
        if p.get("im") == "Digital" and m2_papel > 0:
            c_imp_f = hp_papel_f * m2_papel * 6.5
        elif p.get("im") == "Offset":
            base = f_offset(nb)
            nt = int(p.get("nt", 0))
            barn = 1 if p.get("ba", False) else 0
            c_imp_f = base * (nt + barn)

        c_imp_d = 0.0
        if p.get("im_d") == "Digital" and m2_papel > 0:
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
        c_pel_f = 0.0
        if pel_f != "Sin Peliculado" and m2_papel > 0:
            c_pel_f = hp_produccion * m2_papel * float(db["peliculado"][pel_f])
        c_pel_d = 0.0
        if pel_d != "Sin Peliculado" and m2_papel > 0:
            c_pel_d = hp_produccion * m2_papel * float(db["peliculado"][pel_d])
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

        sub = c_carton + c_ond + c_rig + c_peg + c_imp + c_pel + c_trq + c_plot

        detalle.append({
            "Pieza": nombre,
            "Mat. Cartoncillo": c_carton,
            "Mat. Base Ondulado": c_ond,
            "Mat. Base Rígido": c_rig,
            "Acab. Contracolado": c_peg,
            "Impresión": c_imp,
            "Acab. Peliculado": c_pel,
            "Corte Troquel (taller)": c_trq,
            "Corte Plotter (taller)": c_plot,
            "Subtotal Pieza": sub,
        })

        aud["MATERIAL_CARTONCILLO"] += c_carton
        aud["MATERIAL_BASE_ONDULADO"] += c_ond
        aud["MATERIAL_BASE_RIGIDO"] += c_rig
        aud["ACABADO_CONTRACOLADO"] += c_peg
        aud["IMPRESION"] += c_imp
        aud["ACABADO_PELICULADO"] += c_pel
        aud["CORTE_TROQUEL"] += c_trq
        aud["CORTE_PLOTTER"] += c_plot

    # EXTRAS (taller)
    c_ext = sum(float(e.get("coste", 0)) * float(e.get("cantidad", 0)) * q_n for e in extras)
    aud["EXTRAS_ACCESORIOS"] = c_ext

    # MANO DE OBRA (taller)
    c_mo = ((float(seg_man_total) / 3600.0) * 18.0 * q_n) + (q_n * float(dif_ud))
    aud["MANO_DE_OBRA"] = c_mo

    # EMBALAJE (venta)
    coste_emb_unit_compra = float(st.session_state.costes_embalaje_manual.get(q_n, 0.0))
    pv_emb_total = coste_emb_unit_compra * 1.4 * q_n

    # TROQUEL (venta)
    tot_pv_trq = sum(float(pz.get("pv_troquel", 0.0)) for pz in st.session_state.piezas_dict.values())

    coste_piezas_taller = sum(x["Subtotal Pieza"] for x in detalle)
    taller_total = coste_piezas_taller + c_ext + c_mo

    pvp_total = (taller_total * float(margen)) + float(imp_fijo_pvp) + pv_emb_total + tot_pv_trq

    return {
        "detalle_por_pieza": detalle,
        "auditoria_partidas": aud,
        "c_ext": c_ext,
        "c_mo": c_mo,
        "coste_emb_unit_compra": coste_emb_unit_compra,
        "pv_emb_total": pv_emb_total,
        "tot_pv_trq": tot_pv_trq,
        "coste_piezas_taller": coste_piezas_taller,
        "taller_total": taller_total,
        "pvp_total": pvp_total,
    }

# =========================================================
# RESULTADOS (normal + oferta)
# =========================================================
res_admin = []
res_operario = []
desc_full = {}
oferta_precios = {}  # q -> dict de precios unitarios/total

if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
    for q_n in lista_cants:
        out = calcular_costes_con_auditoria(q_n)
        desc_full[q_n] = out

        # 1) Precio venta del material producido (unitario)
        #    Incluye TODO excepto accesorios, embalajes y troqueles
        #    => (coste_piezas_taller + mano_de_obra) * margen + fijo
        pvp_material_total = ((out["coste_piezas_taller"] + out["c_mo"]) * float(margen)) + float(imp_fijo_pvp)
        pvp_material_unit = (pvp_material_total / q_n) if q_n > 0 else 0.0

        # 2) Precio venta embalaje (unitario) (venta ya incorpora 1.4)
        pvp_emb_unit = (out["pv_emb_total"] / q_n) if q_n > 0 else 0.0

        # 3) Precio venta troquel (TOTAL)
        pvp_troquel_total = float(out["tot_pv_trq"])

        # 4) Precio venta unitario incluyendo todo
        pvp_total_unit = (out["pvp_total"] / q_n) if q_n > 0 else 0.0

        oferta_precios[q_n] = {
            "pvp_material_unit": pvp_material_unit,
            "pvp_emb_unit": pvp_emb_unit,
            "pvp_troquel_total": pvp_troquel_total,
            "pvp_total_unit": pvp_total_unit,
            "pvp_total": out["pvp_total"],
        }

        if st.session_state.is_admin:
            res_admin.append({
                "Cantidad": q_n,
                "Precio Venta Total": f"{out['pvp_total']:.2f}€",
                "Unitario (Todo Incluido)": f"{pvp_total_unit:.3f}€",
            })
        else:
            res_operario.append({
                "Cantidad": q_n,
                "PVP unitario material producido": f"{pvp_material_unit:.3f}€",
                "Precio embalaje (unit)": f"{pvp_emb_unit:.3f}€",
                "Precio troquel (total)": f"{pvp_troquel_total:.2f}€",
                "PVP unitario todo incluido": f"{pvp_total_unit:.3f}€",
            })

# =========================================================
# VISTA OFERTA (para pantallazo)
# Requisitos:
# - Desglose de formas con características
# - Materiales extra
# - Características del embalaje
# - Precios detallados (por este orden):
#   1) PVP material (unitario)
#   2) PVP embalaje (unitario)
#   3) PVP troquel (TOTAL)
#   4) PVP unitario todo incluido
# =========================================================
def render_oferta_html() -> str:
    piezas = list(st.session_state.piezas_dict.values())
    extras = st.session_state.lista_extras_grabados
    emb_tipo = st.session_state.emb_tipo
    L = float(st.session_state.emb_dims.get("L", 0))
    W = float(st.session_state.emb_dims.get("W", 0))
    H = float(st.session_state.emb_dims.get("H", 0))

    # ---- Bloque de formas ----
    formas_html = ""
    for p in piezas:
        nombre = p.get("nombre", "Pieza")
        size = f"{int(p.get('h',0))}x{int(p.get('w',0))} mm"
        pliegos = float(p.get("pliegos", 1.0))

        # Soporte
        if p.get("tipo_base") == "Material Rígido":
            soporte = f"Rígido: {p.get('mat_rigido','')}"
        else:
            soporte = f"Ondulado: {p.get('pl','')} ({p.get('ap','')})"
            if p.get("pl_dif", False):
                soporte += f" | Plancha: {int(p.get('pl_h',0))}x{int(p.get('pl_w',0))} mm"

        # Materiales cara/dorso
        frontal = p.get("pf", "Ninguno")
        gf = int(p.get("gf", 0))
        dorso = p.get("pd", "Ninguno")
        gd = int(p.get("gd", 0))

        # Impresión
        imf = p.get("im", "No")
        imd = p.get("im_d", "No")
        ntf = int(p.get("nt", 0))
        ntd = int(p.get("nt_d", 0))
        baf = "Sí" if p.get("ba", False) else "No"
        bad = "Sí" if p.get("ba_d", False) else "No"
        pel_f = p.get("pel", "Sin Peliculado")
        pel_d = p.get("pel_d", "Sin Peliculado")

        # Corte
        corte = p.get("cor", "Troquelado")
        cobrar_arr = "Sí" if p.get("cobrar_arreglo", True) else "No"
        pv_trq = float(p.get("pv_troquel", 0.0))

        formas_html += f"""
        <div class="card">
          <div class="v">{nombre}</div>
          <div class="muted">{size} | Pliegos/ud: {pliegos:.4f}</div>
          <div class="sec">
            <div class="k">Soporte</div>
            <div class="v">{soporte}</div>
          </div>
          <div class="grid sec">
            <div>
              <div class="k">Cartoncillo cara</div>
              <div class="v">{frontal} ({gf} g)</div>
            </div>
            <div>
              <div class="k">Cartoncillo dorso</div>
              <div class="v">{dorso} ({gd} g)</div>
            </div>
          </div>
          <div class="grid sec">
            <div>
              <div class="k">Impresión cara</div>
              <div class="v">{imf}{" | " + str(ntf) + " tintas" if imf=="Offset" else ""}{" | Barniz: " + baf if imf=="Offset" else ""}</div>
              <div class="muted">Peliculado: {pel_f}</div>
            </div>
            <div>
              <div class="k">Impresión dorso</div>
              <div class="v">{imd}{" | " + str(ntd) + " tintas" if imd=="Offset" else ""}{" | Barniz: " + bad if imd=="Offset" else ""}</div>
              <div class="muted">Peliculado: {pel_d}</div>
            </div>
          </div>
          <div class="grid sec">
            <div>
              <div class="k">Corte</div>
              <div class="v">{corte}</div>
            </div>
            <div>
              <div class="k">Troquel (venta)</div>
              <div class="v">{pv_trq:.2f}€ | Cobrar arreglo: {cobrar_arr}</div>
            </div>
          </div>
        </div>
        """

    # ---- Extras ----
    extras_html = ""
    if extras:
        extras_html += "<table class='tbl'><tr><th>Extra</th><th>€/ud</th><th>Cant/ud prod</th></tr>"
        for e in extras:
            extras_html += f"<tr><td class='rowh'>{e.get('nombre','')}</td><td>{float(e.get('coste',0)):.4f}€</td><td>{float(e.get('cantidad',0)):.4f}</td></tr>"
        extras_html += "</table>"
    else:
        extras_html = "<div class='muted'>Sin extras.</div>"

    # ---- Embalaje ----
    emb_dims_txt = ""
    if emb_tipo in ["Embalaje Guaina (Automático)", "Embalaje en Plano"]:
        emb_dims_txt = f"{int(L)}x{int(W)}x{int(H)} mm"
    else:
        emb_dims_txt = "N/A"

    embalaje_html = f"""
    <div class="card">
      <div class="k">Tipo de embalaje</div>
      <div class="v">{emb_tipo}</div>
      <div class="k" style="margin-top:8px;">Medidas</div>
      <div class="v">{emb_dims_txt}</div>
    </div>
    """

    # ---- Precios (tabla: filas fijas, columnas cantidades) ----
    if not oferta_precios:
        precios_html = "<div class='muted'>Define cantidades para calcular precios.</div>"
    else:
        # Header
        precios_html = "<table class='tbl'>"
        precios_html += "<tr><th></th>"
        for q in lista_cants:
            precios_html += f"<th>{q} uds</th>"
        precios_html += "</tr>"

        # 1) PVP material (unitario)
        precios_html += "<tr><td class='rowh'>Precio venta material (unitario)</td>"
        for q in lista_cants:
            v = oferta_precios[q]["pvp_material_unit"]
            precios_html += f"<td>{v:.3f}€</td>"
        precios_html += "</tr>"

        # 2) PVP embalaje (unitario)
        precios_html += "<tr><td class='rowh'>Precio venta embalaje (unitario)</td>"
        for q in lista_cants:
            v = oferta_precios[q]["pvp_emb_unit"]
            precios_html += f"<td>{v:.3f}€</td>"
        precios_html += "</tr>"

        # 3) PVP troquel (TOTAL)
        precios_html += "<tr><td class='rowh'>Precio venta troquel (TOTAL)</td>"
        for q in lista_cants:
            v = oferta_precios[q]["pvp_troquel_total"]
            precios_html += f"<td>{v:.2f}€</td>"
        precios_html += "</tr>"

        # 4) PVP unitario incluyendo todo
        precios_html += "<tr><td class='rowh'>Precio venta unitario (todo incluido)</td>"
        for q in lista_cants:
            v = oferta_precios[q]["pvp_total_unit"]
            precios_html += f"<td><b>{v:.3f}€</b></td>"
        precios_html += "</tr>"

        precios_html += "</table>"

    html = f"""
    <div class="offer-wrap">
      <div class="offer-title">OFERTA · {st.session_state.cli or "Cliente"}</div>
      <div class="offer-sub">
        Ref: <b>{st.session_state.brf or "-"}</b> · {st.session_state.desc or ""}
      </div>

      <div class="sec">
        <h3>1) Formas</h3>
        <div class="grid">
          {formas_html}
        </div>
      </div>

      <div class="sec">
        <h3>2) Materiales extra</h3>
        {extras_html}
      </div>

      <div class="sec">
        <h3>3) Embalaje</h3>
        {embalaje_html}
      </div>

      <div class="sec">
        <h3>4) Precios de venta</h3>
        {precios_html}
      </div>

      <div class="sec muted">
        * “Precio venta material” incluye todos los costes del producido excepto extras, embalajes y troqueles.
      </div>
    </div>
    """
    return html

# =========================================================
# SALIDA PRINCIPAL
# =========================================================
if modo_comercial:
    st.markdown(render_oferta_html(), unsafe_allow_html=True)
else:
    if st.session_state.is_admin:
        if res_admin:
            st.header(f"📊 Resumen de Venta: {st.session_state.cli}")
            st.dataframe(pd.DataFrame(res_admin), use_container_width=True)

            st.divider()
            st.subheader("🧾 Auditoría de costes (por partida)")

            for q in lista_cants:
                out = desc_full.get(q)
                if not out:
                    continue

                with st.expander(f"🔍 Auditoría {q} uds", expanded=False):
                    aud = out["auditoria_partidas"]

                    df_aud = pd.DataFrame([{
                        "Partida": "MATERIAL_CARTONCILLO",
                        "Coste (€)": aud["MATERIAL_CARTONCILLO"],
                    }, {
                        "Partida": "MATERIAL_BASE_ONDULADO",
                        "Coste (€)": aud["MATERIAL_BASE_ONDULADO"],
                    }, {
                        "Partida": "MATERIAL_BASE_RIGIDO",
                        "Coste (€)": aud["MATERIAL_BASE_RIGIDO"],
                    }, {
                        "Partida": "IMPRESION",
                        "Coste (€)": aud["IMPRESION"],
                    }, {
                        "Partida": "ACABADO_PELICULADO",
                        "Coste (€)": aud["ACABADO_PELICULADO"],
                    }, {
                        "Partida": "ACABADO_CONTRACOLADO",
                        "Coste (€)": aud["ACABADO_CONTRACOLADO"],
                    }, {
                        "Partida": "CORTE_TROQUEL (taller)",
                        "Coste (€)": aud["CORTE_TROQUEL"],
                    }, {
                        "Partida": "CORTE_PLOTTER (taller)",
                        "Coste (€)": aud["CORTE_PLOTTER"],
                    }, {
                        "Partida": "EXTRAS_ACCESORIOS (taller)",
                        "Coste (€)": aud["EXTRAS_ACCESORIOS"],
                    }, {
                        "Partida": "MANO_DE_OBRA (taller)",
                        "Coste (€)": aud["MANO_DE_OBRA"],
                    }])

                    st.table(df_aud.style.format({"Coste (€)": "{:.2f}"}))

                    st.divider()
                    st.markdown("**Detalle por pieza (taller)**")
                    df_det = pd.DataFrame(out["detalle_por_pieza"])
                    st.dataframe(df_det.style.format("{:.2f}", subset=[c for c in df_det.columns if c != "Pieza"]), use_container_width=True)

                    st.divider()
                    st.markdown("**Embalaje (venta)**")
                    st.write(f"Coste compra embalaje (unit): {out['coste_emb_unit_compra']:.4f}€")
                    st.write(f"Venta embalaje total = coste_compra*1.4*q = {out['pv_emb_total']:.2f}€")

                    st.markdown("**Troquel (venta)**")
                    st.write(f"Tot. precio venta troquel = {out['tot_pv_trq']:.2f}€")

                    st.divider()
                    st.metric("COSTE PIEZAS (taller)", f"{out['coste_piezas_taller']:.2f}€")
                    st.metric("COSTE TALLER TOTAL", f"{out['taller_total']:.2f}€")
                    st.metric("PVP TOTAL", f"{out['pvp_total']:.2f}€")
        else:
            st.info("Define cantidades y formas para obtener resultados.")
    else:
        if res_operario:
            st.success("✅ Cálculo Realizado")
            st.dataframe(pd.DataFrame(res_operario), use_container_width=True)
        else:
            st.info("Define cantidades y formas para obtener resultados.")
