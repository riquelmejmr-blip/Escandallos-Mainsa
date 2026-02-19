import streamlit as st
import pandas as pd
import json
import re
import math
from copy import deepcopy
import hashlib

# =========================================================
# 1) CONFIGURACIÓN
# =========================================================
st.set_page_config(page_title="MAINSA ADMIN V44", layout="wide")

# =========================================================
# 2) FLEXICO
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
    "950221": {"desc": "BASE GIRATORIA Ø 150 MM", "precio": 1.9400}
}
OPCIONES_FLEXICO = [f"{k} - {v['desc']}" for k, v in PRODUCTOS_FLEXICO.items()]

# =========================================================
# 3) PRECIOS BASE + RÍGIDOS ACTUALIZADOS (TU LISTA)
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
        "Grande (> 1000x700)": {"arranque": 107.80, "tiro": 0.135}
    },
    "plotter": {"precio_hoja": 2.03}
}

FORMATOS_STD = {
    "Personalizado": (0, 0), "1600x1200": (1600, 1200), "1600x1100": (1600, 1100),
    "1400x1000": (1400, 1000), "1300x900": (1300, 900), "1200x800": (1200, 800),
    "1100x800": (1100, 800), "1000x700": (1000, 700), "900x650": (900, 650),
    "800x550": (800, 550), "700x500": (700, 500)
}

# =========================================================
# MERMAS (AUTO)
# =========================================================
def calcular_mermas_estandar(n, es_digital=False):
    if es_digital:
        return int(n * 0.02), 10
    if n < 100: return 10, 150
    if n < 200: return 20, 175
    if n < 600: return 30, 200
    if n < 1000: return 40, 220
    if n < 2000: return 50, 250
    return int(n * 0.03), 300

def parse_cantidades(s: str):
    if not s: return []
    out = []
    for x in s.split(","):
        x = x.strip()
        if x.isdigit() and int(x) > 0:
            out.append(int(x))
    return out

# =========================================================
# EMBALAJES (múltiples)
# =========================================================
TIPOS_EMB = ["Manual", "Embalaje Guaina (Automático)", "Embalaje en Plano", "Embalaje en Volumen"]
EMB_MATS = ["Canal 5", "D/D"]

def emb_mult(material: str) -> float:
    return 1.5 if material == "D/D" else 1.0

def embalaje_plano_unit(L_mm, W_mm, H_mm, Q):
    # P ≈ (152 + (20·S))/Q + 0,15 + (1,02·S)
    if Q <= 0 or L_mm <= 0 or W_mm <= 0 or H_mm <= 0:
        return 0.0, 0.0
    L = L_mm / 1000.0
    W = W_mm / 1000.0
    H = H_mm / 1000.0
    S = (L * W) + 2.0 * H * (L + W)
    P = ((152.0 + (20.0 * S)) / float(Q)) + 0.15 + (1.02 * S)
    return float(P), float(S)

def embalaje_volumen_unit(L_mm, A_mm, H_mm, Q):
    # P ≈ (20 + 8·S)/Q + 0,64·S
    # S = (2L + 2A + 0,05) * (H + A)
    if Q <= 0 or L_mm <= 0 or A_mm <= 0 or H_mm <= 0:
        return 0.0, 0.0
    L = L_mm / 1000.0
    A = A_mm / 1000.0
    H = H_mm / 1000.0
    S = (2.0 * L + 2.0 * A + 0.05) * (H + A)
    P = ((20.0 + (8.0 * S)) / float(Q)) + (0.64 * S)
    return float(P), float(S)

def crear_embalaje_vacio(idx):
    return {
        "id": f"emb_{idx}",
        "nombre": f"Embalaje {idx+1}",
        "tipo": "Manual",
        "material": "Canal 5",
        "dims": {"L": 0.0, "W": 0.0, "H": 0.0},
        "costes": {}  # q -> coste compra unit
    }

# =========================================================
# FORMAS
# =========================================================
def crear_forma_vacia(index):
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

        "pel": "Sin Peliculado",
        "pel_d": "Sin Peliculado",
        "ld": False, "ld_d": False,

        "cor": "Troquelado",
        "cobrar_arreglo": True,
        "pv_troquel": 0.0,
    }

def es_digital_en_proyecto(piezas_dict):
    for p in piezas_dict.values():
        if p.get("im") == "Digital" or p.get("im_d") == "Digital":
            return True
    return False

# =========================================================
# SESSION STATE INIT
# =========================================================
if "db_precios" not in st.session_state: st.session_state.db_precios = deepcopy(PRECIOS_BASE)
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "piezas_dict" not in st.session_state: st.session_state.piezas_dict = {0: crear_forma_vacia(0)}
if "lista_extras_grabados" not in st.session_state: st.session_state.lista_extras_grabados = []
if "embalajes" not in st.session_state: st.session_state.embalajes = [crear_embalaje_vacio(0)]
if "mermas_imp_manual" not in st.session_state: st.session_state.mermas_imp_manual = {}
if "mermas_proc_manual" not in st.session_state: st.session_state.mermas_proc_manual = {}

if "brf" not in st.session_state: st.session_state.brf = ""
if "cli" not in st.session_state: st.session_state.cli = ""
if "desc" not in st.session_state: st.session_state.desc = ""
if "cants_str_saved" not in st.session_state: st.session_state.cants_str_saved = "0"

if "unidad_t" not in st.session_state: st.session_state.unidad_t = "Segundos"
if "t_input" not in st.session_state: st.session_state.t_input = 0.0

if "dif_ud" not in st.session_state: st.session_state.dif_ud = 0.091
if "imp_fijo_pvp" not in st.session_state: st.session_state.imp_fijo_pvp = 500.0
if "margen" not in st.session_state: st.session_state.margen = 2.2

if "_last_import_hash" not in st.session_state: st.session_state._last_import_hash = None

# =========================================================
# IMPORT / EXPORT
# =========================================================
def normalizar_import(di: dict):
    # Identidad
    st.session_state.brf = str(di.get("brf", st.session_state.brf))
    st.session_state.cli = str(di.get("cli", st.session_state.cli))
    st.session_state.desc = str(di.get("desc", st.session_state.desc))

    # Cantidades (string original)
    if isinstance(di.get("cants_str", None), str):
        st.session_state.cants_str_saved = di["cants_str"]

    # Manipulación
    manip = di.get("manip", {})
    if isinstance(manip, dict):
        if "unidad_t" in manip:
            st.session_state.unidad_t = manip["unidad_t"]
        if "t_input" in manip:
            st.session_state.t_input = float(manip["t_input"])

    # Params (si existen)
    params = di.get("params", {})
    if isinstance(params, dict):
        if "dif_ud" in params: st.session_state.dif_ud = float(params["dif_ud"])
        if "imp_fijo_pvp" in params: st.session_state.imp_fijo_pvp = float(params["imp_fijo_pvp"])
        if "margen" in params: st.session_state.margen = float(params["margen"])

    # Base de precios (completa)
    if isinstance(di.get("db_precios", None), dict):
        st.session_state.db_precios = di["db_precios"]

    # Piezas
    if isinstance(di.get("piezas", None), dict):
        st.session_state.piezas_dict = {int(k): v for k, v in di["piezas"].items()}

    # Extras
    if isinstance(di.get("extras", None), list):
        st.session_state.lista_extras_grabados = di["extras"]

    # Mermas
    if isinstance(di.get("mermas_imp", None), dict):
        st.session_state.mermas_imp_manual = {int(k): int(v) for k, v in di["mermas_imp"].items()}
    if isinstance(di.get("mermas_proc", None), dict):
        st.session_state.mermas_proc_manual = {int(k): int(v) for k, v in di["mermas_proc"].items()}

    # Embalajes múltiples
    emb = di.get("embalajes", None)
    if isinstance(emb, list) and len(emb) > 0:
        new_list = []
        for idx, e in enumerate(emb):
            if not isinstance(e, dict):
                continue
            base = crear_embalaje_vacio(idx)
            base["id"] = str(e.get("id", base["id"]))
            base["nombre"] = str(e.get("nombre", base["nombre"]))
            base["tipo"] = str(e.get("tipo", base["tipo"]))
            base["material"] = str(e.get("material", base["material"]))
            if isinstance(e.get("dims", None), dict):
                base["dims"] = e["dims"]
            if isinstance(e.get("costes", None), dict):
                base["costes"] = {int(k): float(v) for k, v in e["costes"].items()}
            new_list.append(base)
        st.session_state.embalajes = new_list if new_list else [crear_embalaje_vacio(0)]
    else:
        st.session_state.embalajes = [crear_embalaje_vacio(0)]

def construir_export(resumen_compra=None):
    data = {
        "brf": st.session_state.brf,
        "cli": st.session_state.cli,
        "desc": st.session_state.desc,
        "cants_str": st.session_state.cants_str_saved,
        "manip": {"unidad_t": st.session_state.unidad_t, "t_input": float(st.session_state.t_input)},
        "params": {"dif_ud": float(st.session_state.dif_ud), "imp_fijo_pvp": float(st.session_state.imp_fijo_pvp), "margen": float(st.session_state.margen)},
        "db_precios": st.session_state.db_precios,
        "piezas": st.session_state.piezas_dict,
        "extras": st.session_state.lista_extras_grabados,
        "embalajes": st.session_state.embalajes,
        "mermas_imp": st.session_state.mermas_imp_manual,
        "mermas_proc": st.session_state.mermas_proc_manual,
    }
    if resumen_compra is not None:
        data["compras_legible"] = resumen_compra
    return data

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
    .comercial-box { background-color: white; padding: 26px; border: 2px solid #1E88E5; border-radius: 12px; color: #222; }
    .comercial-header { color: #1E88E5; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 12px; font-weight: 800; letter-spacing: .5px;}
    .comercial-ref { text-align: center; color: #555; font-size: 1.0em; margin-bottom: 18px; font-weight: 600; }
    .comercial-table { width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 1.02em; }
    .comercial-table th { background-color: #1E88E5; color: white; padding: 10px; text-align: left; }
    .comercial-table td { padding: 10px; border: 1px solid #e1e1e1; text-align: left; vertical-align: top;}
    .tag {display:inline-block; padding:2px 8px; border-radius: 999px; font-size:.88em; background:#f2f6ff; border:1px solid #dbe6ff; color:#1E88E5; margin-right:6px;}
    .sec-title{margin-top:14px; font-weight:800; color:#1E88E5;}
    .small{font-size:.92em; color:#555;}
    .muted{color:#666;}
    .grid2{display:grid; grid-template-columns: 1fr 1fr; gap:10px;}
    .card{border:1px solid #eee; border-radius:10px; padding:12px; background:#fff;}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ PANEL ADMIN - ESCANDALLO")

# =========================================================
# SIDEBAR (CORREGIDO: NO asignar session_state = widget con misma key)
# =========================================================
with st.sidebar:
    st.header("⚙️ Configuración")

    pwd = st.text_input("🔑 Contraseña Admin", type="password", key="pwd_admin")
    st.session_state.is_admin = (pwd == "mainsa2024")
    if st.session_state.is_admin:
        st.success("Modo Admin Activo")
    elif pwd:
        st.error("Contraseña incorrecta")

    st.divider()

    with st.expander("🤖 Importar Datos (JSON)", expanded=False):
        uploaded = st.file_uploader("Subir JSON", type=["json"], key="uploader_json")
        if uploaded is not None:
            try:
                raw = uploaded.getvalue()
                h = hashlib.sha256(raw).hexdigest()
                if st.session_state._last_import_hash != h:
                    di = json.loads(raw.decode("utf-8"))
                    normalizar_import(di)
                    st.session_state._last_import_hash = h
                    st.success("Importación completa OK")
                    st.rerun()
                else:
                    st.caption("Este JSON ya se importó (evitado bucle).")
            except Exception as e:
                st.error(f"Error importando JSON: {e}")

        if st.button("🧹 Permitir re-importar el mismo JSON", key="reset_import"):
            st.session_state._last_import_hash = None
            st.success("Listo.")

    # Inputs (se escriben en session_state manualmente, sin keys conflictivas)
    brf_val = st.text_input("Nº Briefing", value=st.session_state.brf, key="brf_input")
    cli_val = st.text_input("Cliente", value=st.session_state.cli, key="cli_input")
    desc_val = st.text_input("Descripción", value=st.session_state.desc, key="desc_input")
    st.session_state.brf = brf_val
    st.session_state.cli = cli_val
    st.session_state.desc = desc_val

    st.divider()

    cants_str_val = st.text_input("Cantidades (ej: 500, 1000)", value=st.session_state.cants_str_saved, key="cants_input")
    st.session_state.cants_str_saved = cants_str_val
    lista_cants = parse_cantidades(cants_str_val)

    # Manipulación
    st.radio("Manipulación:", ["Segundos", "Minutos"], horizontal=True, key="unidad_t")
    st.number_input("Tiempo/ud", value=float(st.session_state.t_input), key="t_input")

    unidad_t = st.session_state["unidad_t"]
    t_input = float(st.session_state["t_input"])
    seg_man_total = t_input * 60 if unidad_t == "Minutos" else t_input

    # Finanzas
    if st.session_state.is_admin:
        st.divider()
        st.markdown("### 💰 Finanzas")
        st.selectbox("Dificultad (€/ud)", [0.02, 0.061, 0.091], index=2, key="dif_ud")
        st.number_input("Fijo PVP (€)", value=float(st.session_state.imp_fijo_pvp), key="imp_fijo_pvp")
        st.number_input("Multiplicador", step=0.1, value=float(st.session_state.margen), key="margen")
        dif_ud = float(st.session_state["dif_ud"])
        imp_fijo_pvp = float(st.session_state["imp_fijo_pvp"])
        margen = float(st.session_state["margen"])
    else:
        dif_ud, imp_fijo_pvp, margen = 0.091, 500.0, 2.2

    modo_comercial = st.checkbox("🌟 VISTA OFERTA", value=False, key="modo_oferta")

# =========================================================
# PESTAÑAS
# =========================================================
if st.session_state.is_admin:
    tab_calculadora, tab_costes, tab_debug = st.tabs(["🧮 Calculadora", "💰 Base de Datos", "🔍 Desglose"])
else:
    tab_calculadora, = st.tabs(["🧮 Calculadora Técnica"])
    tab_costes, tab_debug = None, None

# =========================================================
# TAB COSTES (ADMIN)
# =========================================================
if tab_costes:
    with tab_costes:
        col_c1, col_c2 = st.columns(2)
        db = st.session_state.db_precios

        with col_c1:
            with st.expander("📄 Cartoncillo (€/Kg)", expanded=True):
                for k, v in db["cartoncillo"].items():
                    if k != "Ninguno":
                        db["cartoncillo"][k]["precio_kg"] = st.number_input(
                            f"{k} (€/kg)", value=float(v["precio_kg"]), key=f"cost_cart_{k}"
                        )

            with st.expander("🧱 Ondulado y Rígidos (€/hoja)", expanded=True):
                st.markdown("##### Ondulado")
                for k, v in db["planchas"].items():
                    if k != "Ninguna":
                        st.markdown(f"**{k}**")
                        cols = st.columns(len(v))
                        for idx, (sk, sv) in enumerate(v.items()):
                            db["planchas"][k][sk] = cols[idx].number_input(
                                sk, value=float(sv), key=f"cost_pl_{k}_{sk}"
                            )
                st.markdown("---")
                st.markdown("##### Rígidos (Precio Hoja + Tamaño)")
                for k, v in db["rigidos"].items():
                    if k != "Ninguno":
                        c1, c2, c3 = st.columns([3, 1, 1])
                        db["rigidos"][k]["precio_ud"] = c1.number_input(
                            f"{k} (€/hoja)", value=float(v["precio_ud"]), key=f"cost_rig_{k}"
                        )
                        db["rigidos"][k]["w"] = int(c2.number_input("w", value=int(v["w"]), key=f"rigw_{k}"))
                        db["rigidos"][k]["h"] = int(c3.number_input("h", value=int(v["h"]), key=f"righ_{k}"))

        with col_c2:
            with st.expander("✨ Acabados", expanded=True):
                for k, v in db["peliculado"].items():
                    if k != "Sin Peliculado":
                        db["peliculado"][k] = st.number_input(f"{k}", value=float(v), key=f"cost_pel_{k}")
                db["laminado_digital"] = st.number_input("Laminado Digital", value=float(db.get("laminado_digital", 3.5)), key="cost_lam_dig")

            with st.expander("🔪 Troquelado", expanded=True):
                for k, v in db["troquelado"].items():
                    st.markdown(f"**{k}**")
                    c_arr, c_tir = st.columns(2)
                    db["troquelado"][k]["arranque"] = c_arr.number_input(f"Arranque (€)", value=float(v["arranque"]), key=f"trq_arr_{k}")
                    db["troquelado"][k]["tiro"] = c_tir.number_input(f"Tiro (€/h)", value=float(v["tiro"]), format="%.4f", key=f"trq_tir_{k}")

            with st.expander("✂️ Plotter", expanded=True):
                db["plotter"]["precio_hoja"] = st.number_input("Corte Plotter (€/hoja)", value=float(db["plotter"]["precio_hoja"]), key="plotter_precio")

# =========================================================
# TAB CALCULADORA
# =========================================================
with tab_calculadora:
    db = st.session_state.db_precios

    # Auto-relleno mermas según escalado si no existen
    if lista_cants:
        es_dig = es_digital_en_proyecto(st.session_state.piezas_dict)
        for q in lista_cants:
            mp, mi = calcular_mermas_estandar(q, es_digital=es_dig)
            if q not in st.session_state.mermas_proc_manual:
                st.session_state.mermas_proc_manual[q] = mp
            if q not in st.session_state.mermas_imp_manual:
                st.session_state.mermas_imp_manual[q] = mi

    if not modo_comercial:
        st.header("1. Definición Técnica")

        c_btns = st.columns([1, 4])
        if c_btns[0].button("➕ Forma"):
            nid = max(st.session_state.piezas_dict.keys()) + 1
            st.session_state.piezas_dict[nid] = crear_forma_vacia(nid)
            st.rerun()
        if c_btns[1].button("🗑 Reiniciar"):
            st.session_state.piezas_dict = {0: crear_forma_vacia(0)}
            st.session_state.lista_extras_grabados = []
            st.session_state.embalajes = [crear_embalaje_vacio(0)]
            st.rerun()

        # Callbacks
        def callback_cambio_frontal(pid):
            new_mat = st.session_state[f"pf_{pid}"]
            if new_mat != "Ninguno":
                st.session_state[f"gf_{pid}"] = st.session_state.db_precios["cartoncillo"][new_mat]["gramaje"]
                st.session_state[f"im_{pid}"] = "Offset"
                st.session_state[f"nt_{pid}"] = 4
            else:
                st.session_state[f"im_{pid}"] = "No"
                st.session_state[f"nt_{pid}"] = 0

        def callback_cambio_dorso(pid):
            new_mat = st.session_state[f"pd_{pid}"]
            if new_mat != "Ninguno":
                st.session_state[f"gd_{pid}"] = st.session_state.db_precios["cartoncillo"][new_mat]["gramaje"]
                # si hay dorso, por defecto NO imprime si no quieres, pero habilita opciones
                if st.session_state.get(f"im_d_{pid}", "No") == "No":
                    st.session_state[f"im_d_{pid}"] = "No"
            else:
                st.session_state[f"im_d_{pid}"] = "No"
                st.session_state[f"nt_d_{pid}"] = 0

        def callback_medida_estandar(pid):
            fmt = st.session_state[f"std_{pid}"]
            if fmt != "Personalizado":
                nh, nw = FORMATOS_STD[fmt]
                st.session_state[f"h_{pid}"] = nh
                st.session_state[f"w_{pid}"] = nw
                # si plancha dif no está activa, arrastra
                if not st.session_state.get(f"pldif_{pid}", False):
                    st.session_state[f"plh_{pid}"] = nh
                    st.session_state[f"plw_{pid}"] = nw

        def callback_rigido(pid):
            mat = st.session_state.get(f"mrig_{pid}", "Ninguno")
            if mat != "Ninguno":
                info = st.session_state.db_precios["rigidos"][mat]
                # auto colocar tamaño hoja en la medida de la forma (tal como pediste)
                st.session_state[f"w_{pid}"] = int(info["w"])
                st.session_state[f"h_{pid}"] = int(info["h"])

        for p_id, p in st.session_state.piezas_dict.items():
            with st.expander(f"🛠 {p.get('nombre','Forma')} - {p.get('h',0)}x{p.get('w',0)} mm", expanded=True):
                col1, col2, col3 = st.columns(3)

                # ------------- COL1 -------------
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
                    idx_im = opts_im.index(val_im) if val_im in opts_im else 2
                    p["im"] = st.selectbox("Impresión Cara", opts_im, index=idx_im, key=f"im_{p_id}")

                    if p["im"] == "Offset":
                        p["nt"] = st.number_input("Tintas Cara", 0, 6, int(p.get("nt", 4)), key=f"nt_{p_id}")
                        p["ba"] = st.checkbox("Barniz Cara", value=bool(p.get("ba", False)), key=f"ba_{p_id}")
                    elif p["im"] == "Digital":
                        p["ld"] = st.checkbox("Laminado Digital Cara", value=bool(p.get("ld", False)), key=f"ld_{p_id}")

                    opts_pel = list(db["peliculado"].keys())
                    val_pel = p.get("pel", "Sin Peliculado")
                    idx_pel = opts_pel.index(val_pel) if val_pel in opts_pel else 0
                    p["pel"] = st.selectbox("Peliculado Cara", opts_pel, index=idx_pel, key=f"pel_{p_id}")

                # ------------- COL2 -------------
                with col2:
                    opts_pf = list(db["cartoncillo"].keys())
                    val_pf = p.get("pf", "Ninguno")
                    idx_pf = opts_pf.index(val_pf) if val_pf in opts_pf else 0
                    p["pf"] = st.selectbox("Cartoncillo Cara", opts_pf, index=idx_pf, key=f"pf_{p_id}",
                                           on_change=callback_cambio_frontal, args=(p_id,))
                    p["gf"] = st.number_input("Gramaje Cara (g)", value=int(p.get("gf", 0)), key=f"gf_{p_id}")

                    st.divider()

                    opts_base = ["Ondulado/Cartón", "Material Rígido"]
                    idx_base = opts_base.index(p.get("tipo_base", "Ondulado/Cartón")) if p.get("tipo_base") in opts_base else 0
                    p["tipo_base"] = st.selectbox("Tipo Soporte", opts_base, index=idx_base, key=f"tb_{p_id}")

                    if p["tipo_base"] == "Ondulado/Cartón":
                        opts_pl = list(db["planchas"].keys())
                        val_pl = p.get("pl", "Ninguna")
                        idx_pl = opts_pl.index(val_pl) if val_pl in opts_pl else 0
                        p["pl"] = st.selectbox("Plancha Base", opts_pl, index=idx_pl, key=f"pl_{p_id}")

                        if p["pl"] != "Ninguna":
                            p["pl_dif"] = st.checkbox("📏 Medida Plancha Diferente", value=bool(p.get("pl_dif", False)), key=f"pldif_{p_id}")
                            if p["pl_dif"]:
                                c_ph, c_pw = st.columns(2)
                                p["pl_h"] = c_ph.number_input("Alto Plancha", 0, 5000, value=int(p.get("pl_h", p["h"])), key=f"plh_{p_id}")
                                p["pl_w"] = c_pw.number_input("Ancho Plancha", 0, 5000, value=int(p.get("pl_w", p["w"])), key=f"plw_{p_id}")
                            else:
                                p["pl_h"] = p["h"]
                                p["pl_w"] = p["w"]

                        opts_ap = ["C/C", "B/C", "B/B"]
                        val_ap = p.get("ap", "B/C")
                        idx_ap = opts_ap.index(val_ap) if val_ap in opts_ap else 1
                        p["ap"] = st.selectbox("Calidad Ondulado", opts_ap, index=idx_ap, key=f"ap_{p_id}")

                    else:
                        opts_rig = list(db["rigidos"].keys())
                        val_rig = p.get("mat_rigido", "Ninguno")
                        idx_rig = opts_rig.index(val_rig) if val_rig in opts_rig else 0
                        p["mat_rigido"] = st.selectbox("Material Rígido (hoja)", opts_rig, index=idx_rig, key=f"mrig_{p_id}",
                                                       on_change=callback_rigido, args=(p_id,))
                        if p["mat_rigido"] != "Ninguno":
                            info = db["rigidos"][p["mat_rigido"]]
                            st.info(f"Tamaño hoja: {info['w']}x{info['h']} mm | Precio: {info['precio_ud']:.2f}€/hoja")

                    st.divider()

                    # DORSO (re-implementado)
                    opts_pd = list(db["cartoncillo"].keys())
                    val_pd = p.get("pd", "Ninguno")
                    idx_pd = opts_pd.index(val_pd) if val_pd in opts_pd else 0
                    p["pd"] = st.selectbox("Cartoncillo Dorso", opts_pd, index=idx_pd, key=f"pd_{p_id}",
                                           on_change=callback_cambio_dorso, args=(p_id,))
                    if p["pd"] != "Ninguno":
                        p["gd"] = st.number_input("Gramaje Dorso (g)", value=int(p.get("gd", 0)), key=f"gd_{p_id}")
                    else:
                        p["gd"] = 0

                # ------------- COL3 -------------
                with col3:
                    opts_cor = ["Troquelado", "Plotter"]
                    val_cor = p.get("cor", "Troquelado")
                    idx_cor = opts_cor.index(val_cor) if val_cor in opts_cor else 0
                    p["cor"] = st.selectbox("Corte", opts_cor, index=idx_cor, key=f"cor_{p_id}")

                    if p["cor"] == "Troquelado":
                        p["cobrar_arreglo"] = st.checkbox("¿Cobrar Arreglo?", value=bool(p.get("cobrar_arreglo", True)), key=f"arr_{p_id}")
                        p["pv_troquel"] = st.number_input("Precio Venta Troquel (€)", value=float(p.get("pv_troquel", 0.0)), key=f"pvt_{p_id}")

                    # impresión dorso (solo si hay cartoncillo dorso)
                    if p.get("pd", "Ninguno") != "Ninguno":
                        opts_imd = ["Offset", "Digital", "No"]
                        val_imd = p.get("im_d", "No")
                        idx_imd = opts_imd.index(val_imd) if val_imd in opts_imd else 2
                        p["im_d"] = st.selectbox("Impresión Dorso", opts_imd, index=idx_imd, key=f"im_d_{p_id}")

                        if p["im_d"] == "Offset":
                            p["nt_d"] = st.number_input("Tintas Dorso", 0, 6, int(p.get("nt_d", 0)), key=f"nt_d_{p_id}")
                            p["ba_d"] = st.checkbox("Barniz Dorso", value=bool(p.get("ba_d", False)), key=f"ba_d_{p_id}")
                        elif p["im_d"] == "Digital":
                            p["ld_d"] = st.checkbox("Laminado Digital Dorso", value=bool(p.get("ld_d", False)), key=f"ld_d_{p_id}")
                        else:
                            p["nt_d"] = 0
                            p["ba_d"] = False
                            p["ld_d"] = False

                        val_peld = p.get("pel_d", "Sin Peliculado")
                        idx_peld = opts_pel.index(val_peld) if val_peld in opts_pel else 0
                        p["pel_d"] = st.selectbox("Peliculado Dorso", opts_pel, index=idx_peld, key=f"pel_d_{p_id}")
                    else:
                        p["im_d"] = "No"
                        p["nt_d"] = 0
                        p["ba_d"] = False
                        p["ld_d"] = False
                        p["pel_d"] = "Sin Peliculado"

                    if st.button("🗑 Borrar Forma", key=f"del_{p_id}"):
                        del st.session_state.piezas_dict[p_id]
                        st.rerun()

        # =====================================================
        # EXTRAS
        # =====================================================
        st.divider()
        st.subheader("📦 2. Materiales extra")

        c_add_main, c_add_flex, c_add_manual = st.columns(3)

        with c_add_main:
            st.markdown("**Extras Mainsa**")
            opts_extra = ["---"] + list(db["extras_base"].keys())
            ex_sel = st.selectbox("Añadir extra estándar:", opts_extra, key="sel_extra_mainsa")
            if st.button("➕ Añadir Mainsa", key="btn_add_mainsa") and ex_sel != "---":
                coste_actual = db["extras_base"][ex_sel]
                st.session_state.lista_extras_grabados.append({"nombre": ex_sel, "coste": float(coste_actual), "cantidad": 1.0, "tipo": "mainsa"})
                st.rerun()

        with c_add_flex:
            st.markdown("**Catálogo FLEXICO**")
            flx_sel = st.selectbox("Buscar Ref/Desc:", ["---"] + OPCIONES_FLEXICO, key="sel_extra_flexico")
            if st.button("➕ Añadir Flexico", key="btn_add_flexico") and flx_sel != "---":
                cod = flx_sel.split(" - ")[0]
                prod = PRODUCTOS_FLEXICO[cod]
                st.session_state.lista_extras_grabados.append({"nombre": f"FLEXICO: {prod['desc']}", "coste": float(prod["precio"]), "cantidad": 1.0, "tipo": "flexico"})
                st.rerun()

        with c_add_manual:
            st.markdown("**Extra manual**")
            m_name = st.text_input("Nombre", key="manual_ex_name")
            m_cost = st.number_input("Precio unitario", min_value=0.0, value=0.0, step=0.01, key="manual_ex_cost")
            m_qty = st.number_input("Cantidad/ud prod", min_value=0.0, value=1.0, step=0.1, key="manual_ex_qty")
            if st.button("➕ Añadir Manual", key="btn_add_manual"):
                if m_name.strip():
                    st.session_state.lista_extras_grabados.append({"nombre": m_name.strip(), "coste": float(m_cost), "cantidad": float(m_qty), "tipo": "manual"})
                    st.rerun()
                else:
                    st.warning("Pon un nombre para el extra manual.")

        for i, ex in enumerate(st.session_state.lista_extras_grabados):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            c1.write(f"**{ex['nombre']}**")
            if st.session_state.is_admin:
                ex["coste"] = c2.number_input("€/ud compra", value=float(ex.get("coste", 0.0)), key=f"exc_{i}", format="%.4f")
            else:
                c2.write(f"{float(ex.get('coste',0.0)):.4f}€")
            ex["cantidad"] = c3.number_input("Cant/Ud prod", value=float(ex.get("cantidad", 1.0)), key=f"exq_{i}")
            if c4.button("🗑", key=f"exd_{i}"):
                st.session_state.lista_extras_grabados.pop(i)
                st.rerun()

        # =====================================================
        # EMBALAJES MÚLTIPLES
        # =====================================================
        st.divider()
        st.subheader("📦 3. Embalajes (múltiples)")

        cE1, cE2 = st.columns([1, 4])
        if cE1.button("➕ Añadir embalaje"):
            if len(st.session_state.embalajes) < 5:
                st.session_state.embalajes.append(crear_embalaje_vacio(len(st.session_state.embalajes)))
                st.rerun()
            else:
                st.warning("Máximo 5 embalajes.")

        if cE2.button("🗑 Reset embalajes"):
            st.session_state.embalajes = [crear_embalaje_vacio(0)]
            st.rerun()

        if not lista_cants:
            st.warning("Define cantidades primero.")
        else:
            # Render embalajes
            for ei, emb in enumerate(st.session_state.embalajes):
                with st.expander(f"📦 {emb.get('nombre', f'Embalaje {ei+1}')}", expanded=True):
                    c0, c1, c2, c3 = st.columns([2, 2, 2, 1])
                    emb["nombre"] = c0.text_input("Nombre", value=emb.get("nombre", f"Embalaje {ei+1}"), key=f"emb_name_{ei}")
                    emb["tipo"] = c1.selectbox("Tipo", TIPOS_EMB, index=TIPOS_EMB.index(emb.get("tipo", "Manual")) if emb.get("tipo","Manual") in TIPOS_EMB else 0, key=f"emb_tipo_{ei}")
                    emb["material"] = c2.selectbox("Material", EMB_MATS, index=EMB_MATS.index(emb.get("material","Canal 5")) if emb.get("material","Canal 5") in EMB_MATS else 0, key=f"emb_mat_{ei}")
                    if c3.button("🗑", key=f"emb_del_{ei}"):
                        if len(st.session_state.embalajes) > 1:
                            st.session_state.embalajes.pop(ei)
                            st.rerun()
                        else:
                            st.warning("Debe existir al menos 1 embalaje.")

                    # dims
                    d1, d2, d3 = st.columns(3)
                    emb["dims"]["L"] = float(d1.number_input("Largo mm", value=float(emb["dims"].get("L",0.0)), key=f"embL_{ei}"))
                    emb["dims"]["W"] = float(d2.number_input("Ancho mm", value=float(emb["dims"].get("W",0.0)), key=f"embW_{ei}"))
                    emb["dims"]["H"] = float(d3.number_input("Alto mm", value=float(emb["dims"].get("H",0.0)), key=f"embH_{ei}"))

                    mult = emb_mult(emb["material"])

                    # costes por cantidad
                    cols = st.columns(len(lista_cants))
                    for idx, q in enumerate(lista_cants):
                        if q <= 0:
                            continue

                        if emb["tipo"] == "Manual":
                            if st.session_state.is_admin:
                                emb["costes"][q] = float(cols[idx].number_input(f"Coste compra {q}", value=float(emb["costes"].get(q, 0.0)), key=f"embMan_{ei}_{q}"))
                            else:
                                cols[idx].write(f"**{q} uds**: Manual")

                        elif emb["tipo"] == "Embalaje Guaina (Automático)":
                            L, W, H = emb["dims"]["L"], emb["dims"]["W"], emb["dims"]["H"]
                            sup_m2 = ((2*(L+W)*H) + (L*W)) / 1_000_000 if (L>0 and W>0 and H>0) else 0.0
                            coste_auto = (sup_m2 * 0.70) + (30 / q) if q>0 else 0.0
                            coste_auto *= mult
                            emb["costes"][q] = float(coste_auto)
                            cols[idx].metric(f"{q} uds", f"{coste_auto:.3f}€")

                        elif emb["tipo"] == "Embalaje en Plano":
                            L, W, H = emb["dims"]["L"], emb["dims"]["W"], emb["dims"]["H"]
                            c_plano, _S = embalaje_plano_unit(L, W, H, q)
                            c_plano *= mult
                            emb["costes"][q] = float(c_plano)
                            cols[idx].metric(f"{q} uds", f"{c_plano:.3f}€")

                        elif emb["tipo"] == "Embalaje en Volumen":
                            L, W, H = emb["dims"]["L"], emb["dims"]["W"], emb["dims"]["H"]
                            c_vol, _S = embalaje_volumen_unit(L, W, H, q)
                            c_vol *= mult
                            emb["costes"][q] = float(c_vol)
                            cols[idx].metric(f"{q} uds", f"{c_vol:.3f}€")

        # =====================================================
        # MERMAS
        # =====================================================
        st.divider()
        st.subheader("⚙️ 4. Gestión de Mermas (auto-relleno)")
        if lista_cants:
            for q in lista_cants:
                c1, c2, c3 = st.columns([1, 2, 2])
                c1.markdown(f"**{q} uds**")
                st.session_state.mermas_imp_manual[q] = int(c2.number_input("Arranque impresión (hojas)", value=int(st.session_state.mermas_imp_manual.get(q, 0)), key=f"mi_{q}"))
                st.session_state.mermas_proc_manual[q] = int(c3.number_input("Rodaje proceso (hojas)", value=int(st.session_state.mermas_proc_manual.get(q, 0)), key=f"mp_{q}"))
        else:
            st.warning("Define cantidades primero.")

    # =========================================================
    # MOTOR DE CÁLCULO
    # =========================================================
    res_final = []
    res_tecnico = []
    desc_full = {}
    compras_legible = {}

    if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
        tot_pv_trq = sum(float(pz.get("pv_troquel", 0.0)) for pz in st.session_state.piezas_dict.values())

        for q_n in lista_cants:
            merma_imp_hojas = int(st.session_state.mermas_imp_manual.get(q_n, 0))
            merma_proc_hojas = int(st.session_state.mermas_proc_manual.get(q_n, 0))

            coste_f = 0.0
            det_f = []
            debug_log = []

            # Técnico
            tech_hojas_papel = 0
            tech_planchas_rigidas = 0

            for pid, p in st.session_state.piezas_dict.items():
                # Inicializar partidas
                c_cart_cara = c_cart_dorso = 0.0
                c_ondulado = 0.0
                c_rigido = 0.0
                c_contracolado = 0.0
                c_imp_total = 0.0
                c_pel_total = 0.0
                c_troquel_taller = 0.0
                c_plotter = 0.0

                # Hojas
                nb = q_n * float(p.get("pliegos", 1.0))
                hp_produccion = nb + merma_proc_hojas

                imprime_cara = (p.get("im", "No") != "No")
                imprime_dorso = (p.get("pd", "Ninguno") != "Ninguno" and p.get("im_d", "No") != "No")

                hp_papel_f = hp_produccion + merma_imp_hojas if imprime_cara else hp_produccion
                hp_papel_d = hp_produccion + merma_imp_hojas if imprime_dorso else hp_produccion

                # Área
                w = float(p.get("w", 0))
                h = float(p.get("h", 0))
                m2_papel = (w * h) / 1_000_000 if (w > 0 and h > 0) else 0.0
                tech_hojas_papel += hp_papel_f

                debug_log.append(f"<br><b>🔹 PIEZA: {p.get('nombre','')}</b>")

                # SOPORTE
                if p.get("tipo_base") == "Material Rígido" and p.get("mat_rigido") != "Ninguno":
                    info = db["rigidos"][p["mat_rigido"]]
                    mw, mh = float(info["w"]), float(info["h"])
                    precio_hoja = float(info["precio_ud"])

                    # rendimiento por hoja (en base a tamaño pieza = tamaño hoja en tu modo actual)
                    if w > 0 and h > 0 and mw > 0 and mh > 0:
                        y1 = int(mw // w) * int(mh // h)
                        y2 = int(mw // h) * int(mh // w)
                        by = max(y1, y2)
                    else:
                        by = 0

                    if by <= 0:
                        debug_log.append("⚠️ <b>Rígido:</b> Pieza muy grande para esa hoja (no cabe 1 ud).")
                    else:
                        n_pl = math.ceil(hp_produccion / by)
                        # merma porcentual tipo digital (2%) sobre hojas rígidas
                        n_pl = math.ceil(n_pl * 1.02)
                        tech_planchas_rigidas += n_pl
                        c_rigido = n_pl * precio_hoja
                        debug_log.append(f"🏗️ <b>Material rígido (hojas):</b> ceil({hp_produccion:.0f}/{by})*1.02 → {n_pl} hojas × {precio_hoja:.2f}€ = {c_rigido:.2f}€")

                else:
                    # Ondulado
                    if p.get("pl", "Ninguna") != "Ninguna":
                        if bool(p.get("pl_dif", False)) and float(p.get("pl_h", 0)) > 0 and float(p.get("pl_w", 0)) > 0:
                            m2_plancha = (float(p["pl_w"]) * float(p["pl_h"])) / 1_000_000
                        else:
                            m2_plancha = m2_papel

                        c_ondulado = hp_produccion * m2_plancha * float(db["planchas"][p["pl"]][p.get("ap","B/C")])
                        debug_log.append(f"📦 <b>Plancha ondulado:</b> {hp_produccion:.0f} × {m2_plancha:.4f}m² × {db['planchas'][p['pl']][p.get('ap','B/C')]:.3f} = {c_ondulado:.2f}€")

                # CARTONCILLO (cara y dorso)
                if p.get("pf", "Ninguno") != "Ninguno" and m2_papel > 0:
                    c_cart_cara = hp_papel_f * m2_papel * (float(p.get("gf", 0))/1000.0) * float(db["cartoncillo"][p["pf"]]["precio_kg"])
                if p.get("pd", "Ninguno") != "Ninguno" and m2_papel > 0:
                    c_cart_dorso = hp_papel_d * m2_papel * (float(p.get("gd", 0))/1000.0) * float(db["cartoncillo"][p["pd"]]["precio_kg"])
                debug_log.append(f"📄 <b>Cartoncillo cara:</b> {c_cart_cara:.2f}€ | <b>Cartoncillo dorso:</b> {c_cart_dorso:.2f}€")

                # CONTRACOLADO (✅ cuenta cara y dorso si existen)
                # coste pegado por m2 (uso el 'peg' de Microcanal / Canal 3 como tenías)
                peg_rate = float(db["planchas"]["Microcanal / Canal 3"]["peg"])
                capas = 0
                if p.get("pf","Ninguno") != "Ninguno": capas += 1
                if p.get("pd","Ninguno") != "Ninguno": capas += 1
                if capas > 0 and m2_papel > 0:
                    c_contracolado = hp_produccion * m2_papel * peg_rate * capas
                    debug_log.append(f"🧬 <b>Contracolado:</b> {hp_produccion:.0f} × {m2_papel:.4f} × {peg_rate:.3f} × {capas} = {c_contracolado:.2f}€")

                # IMPRESIÓN
                c_imp_cara = 0.0
                c_imp_dorso = 0.0

                def f_o(n): return 60 if n < 100 else (120 if n > 500 else 60 + 0.15*(n-100))

                if p.get("im","No") == "Digital":
                    c_imp_cara = hp_papel_f * m2_papel * 6.5
                elif p.get("im","No") == "Offset":
                    c_imp_cara = f_o(nb) * (int(p.get("nt",0)) + (1 if bool(p.get("ba",False)) else 0))

                if p.get("im_d","No") == "Digital":
                    c_imp_dorso = hp_papel_d * m2_papel * 6.5
                elif p.get("im_d","No") == "Offset":
                    c_imp_dorso = f_o(nb) * (int(p.get("nt_d",0)) + (1 if bool(p.get("ba_d",False)) else 0))

                c_imp_total = c_imp_cara + c_imp_dorso
                if c_imp_total > 0:
                    debug_log.append(f"🖨️ <b>Impresión:</b> cara {c_imp_cara:.2f}€ + dorso {c_imp_dorso:.2f}€ = {c_imp_total:.2f}€")

                # PELICULADO
                c_pel_cara = 0.0
                c_pel_dorso = 0.0
                if p.get("pel","Sin Peliculado") != "Sin Peliculado":
                    c_pel_cara = hp_produccion * m2_papel * float(db["peliculado"][p["pel"]])
                if p.get("pd","Ninguno") != "Ninguno" and p.get("pel_d","Sin Peliculado") != "Sin Peliculado":
                    c_pel_dorso = hp_produccion * m2_papel * float(db["peliculado"][p["pel_d"]])
                c_pel_total = c_pel_cara + c_pel_dorso
                if c_pel_total > 0:
                    debug_log.append(f"✨ <b>Peliculado:</b> cara {c_pel_cara:.2f}€ + dorso {c_pel_dorso:.2f}€ = {c_pel_total:.2f}€")

                # CORTE
                cat = "Grande (> 1000x700)" if (h>1000 or w>700) else ("Pequeño (< 1000x700)" if (h<1000 and w<700) else "Mediano (Estándar)")
                if p.get("cor","Troquelado") == "Troquelado":
                    arr = float(db["troquelado"][cat]["arranque"]) if bool(p.get("cobrar_arreglo", True)) else 0.0
                    tiro = float(db["troquelado"][cat]["tiro"])
                    c_troquel_taller = arr + (hp_produccion * tiro)
                    debug_log.append(f"🔪 <b>Troquelado (taller):</b> {arr:.2f} + ({hp_produccion:.0f}×{tiro:.3f}) = {c_troquel_taller:.2f}€")
                else:
                    c_plotter = hp_produccion * float(db["plotter"]["precio_hoja"])
                    debug_log.append(f"✂️ <b>Plotter:</b> {hp_produccion:.0f}×{db['plotter']['precio_hoja']:.2f} = {c_plotter:.2f}€")

                # SUBTOTAL PIEZA
                sub = c_cart_cara + c_cart_dorso + c_ondulado + c_rigido + c_contracolado + c_imp_total + c_pel_total + c_troquel_taller + c_plotter
                coste_f += sub

                det_f.append({
                    "Pieza": p.get("nombre",""),
                    "Cartoncillo Cara": c_cart_cara,
                    "Cartoncillo Dorso": c_cart_dorso,
                    "Plancha Ondulado": c_ondulado,
                    "Material Rígido": c_rigido,
                    "Contracolado": c_contracolado,
                    "Impresión": c_imp_total,
                    "Peliculado": c_pel_total,
                    "Corte (Troquel/Plotter)": c_troquel_taller + c_plotter,
                    "Subtotal Pieza": sub
                })

            # EXTRAS compra
            c_ext = sum(float(e.get("coste",0.0)) * float(e.get("cantidad",1.0)) * q_n for e in st.session_state.lista_extras_grabados)

            # Mano de obra compra
            c_mo = ((seg_man_total/3600.0)*18.0*q_n) + (q_n * float(dif_ud))

            # Embalaje compra (sumatoria de embalajes)
            emb_compra_total = 0.0
            emb_det = []
            for emb in st.session_state.embalajes:
                cu = float(emb.get("costes", {}).get(q_n, 0.0))
                emb_compra_total += cu * q_n
                emb_det.append({"nombre": emb.get("nombre",""), "tipo": emb.get("tipo",""), "material": emb.get("material",""), "coste_unit_compra": cu})

            # Venta embalaje (margen fijo 1.4 como antes)
            pv_emb_total = (emb_compra_total * 1.4)

            # Precio venta material (sin extras, sin embalaje, sin troquel venta)
            pv_material_total = ((coste_f + c_mo) * margen) + imp_fijo_pvp
            pv_material_unit = pv_material_total / q_n

            # Troquel venta total
            tot_pv_trq = sum(float(pz.get("pv_troquel", 0.0)) for pz in st.session_state.piezas_dict.values())

            # Total todo
            pvp_total_todo = ((coste_f + c_ext + c_mo) * margen) + imp_fijo_pvp + pv_emb_total + tot_pv_trq
            unit_todo = pvp_total_todo / q_n

            # para tabla
            res_final.append({
                "Cantidad": q_n,
                "Precio venta material (unitario)": f"{pv_material_unit:.3f}€",
                "Precio venta embalaje (unitario)": f"{(pv_emb_total/q_n):.3f}€",
                "Precio venta troquel (TOTAL)": f"{tot_pv_trq:.2f}€",
                "Precio venta unitario (todo)": f"{unit_todo:.3f}€",
                "Precio venta total": f"{pvp_total_todo:.2f}€"
            })

            # técnico
            res_tecnico.append({
                "Cantidad": q_n,
                "Hojas Papel (cara)": f"{tech_hojas_papel:.0f}",
                "Hojas Rígidas (compra)": f"{tech_planchas_rigidas}",
                "Embalaje compra total": f"{emb_compra_total:.2f}€"
            })

            # guardado para desglose/admin
            desc_full[q_n] = {
                "det": det_f,
                "mo": c_mo,
                "extras": c_ext,
                "coste_fabrica": coste_f,
                "emb_compra_total": emb_compra_total,
                "emb_det": emb_det,
                "pv_material_total": pv_material_total,
                "pv_emb_total": pv_emb_total,
                "tot_pv_trq": tot_pv_trq,
                "total": pvp_total_todo,
                "debug": debug_log
            }

            # legible compras
            compras_legible[q_n] = {
                "Cantidad": q_n,
                "Coste fabricación (piezas)": round(coste_f, 4),
                "Coste mano de obra": round(c_mo, 4),
                "Coste extras": round(c_ext, 4),
                "Coste embalaje compra": round(emb_compra_total, 4),
                "Detalle embalajes": emb_det,
                "Troquel venta total": round(tot_pv_trq, 4),
                "Venta material total (sin extras/emb/troquel)": round(pv_material_total, 4),
                "Venta embalaje total": round(pv_emb_total, 4),
                "Venta total todo": round(pvp_total_todo, 4)
            }

    # =========================================================
    # GUARDAR JSON (sidebar -> aquí lo ponemos bajo tabla)
    # =========================================================
    st.divider()
    safe_brf = re.sub(r'[\\/*?:"<>|]', "", st.session_state.brf or "Ref").replace(" ", "_")
    safe_cli = re.sub(r'[\\/*?:"<>|]', "", st.session_state.cli or "Cli").replace(" ", "_")
    nombre_archivo = f"{safe_brf}_{safe_cli}.json"

    export_data = construir_export(resumen_compra=compras_legible if compras_legible else None)
    st.download_button(
        f"💾 Descargar {nombre_archivo}",
        data=json.dumps(export_data, indent=4, ensure_ascii=False),
        file_name=nombre_archivo,
        mime="application/json"
    )

    # =========================================================
    # SALIDAS
    # =========================================================
    if st.session_state.is_admin:
        if modo_comercial and res_final:
            # OFERTA (compacta y “pantallazo-friendly”)
            desc_html = "<div class='sec-title'>📋 Especificaciones del Proyecto</div>"
            desc_html += "<div class='card'>"

            for p in st.session_state.piezas_dict.values():
                base_info = f"Rígido: {p.get('mat_rigido','')}" if p.get("tipo_base") == "Material Rígido" else f"Ondulado: {p.get('pl','')} ({p.get('ap','')})"
                cara = f"{p.get('pf','')} ({p.get('gf',0)}g)"
                dorso = f"{p.get('pd','')} ({p.get('gd',0)}g)"
                imp_c = f"{p.get('im','No')}"
                imp_d = f"{p.get('im_d','No')}"
                pel_c = f"{p.get('pel','Sin Peliculado')}"
                pel_d = f"{p.get('pel_d','Sin Peliculado')}"
                corte = p.get("cor","Troquelado")
                trq = f"{float(p.get('pv_troquel',0.0)):.2f}€"

                desc_html += f"""
                <div style="margin-bottom:8px;">
                    <span class="tag">{p.get('nombre','')}</span>
                    <span class="small muted">{int(p.get('h',0))}×{int(p.get('w',0))} mm | Pliegos/ud: {float(p.get('pliegos',1.0)):.4f}</span>
                    <div class="small">
                        <b>Soporte:</b> {base_info}<br>
                        <b>Cara:</b> {cara} | <b>Imp:</b> {imp_c} | <b>Pel:</b> {pel_c}<br>
                        <b>Dorso:</b> {dorso} | <b>Imp:</b> {imp_d} | <b>Pel:</b> {pel_d}<br>
                        <b>Corte:</b> {corte} | <b>Troquel (venta):</b> {trq}
                    </div>
                </div>
                """

            desc_html += "</div>"

            # Extras
            extras_html = "<div class='sec-title'>➕ Materiales extra</div><div class='card'>"
            if st.session_state.lista_extras_grabados:
                for e in st.session_state.lista_extras_grabados:
                    extras_html += f"<div class='small'>• <b>{e.get('nombre','')}</b> — {float(e.get('cantidad',1.0))} /ud — {float(e.get('coste',0.0)):.4f}€ compra</div>"
            else:
                extras_html += "<div class='small muted'>Sin extras.</div>"
            extras_html += "</div>"

            # Embalajes
            emb_html = "<div class='sec-title'>📦 Embalajes</div><div class='card'>"
            for emb in st.session_state.embalajes:
                L, W, H = emb["dims"].get("L",0), emb["dims"].get("W",0), emb["dims"].get("H",0)
                emb_html += f"<div class='small'>• <b>{emb.get('nombre','')}</b> — {emb.get('tipo','')} — {emb.get('material','')} — {L:.0f}×{W:.0f}×{H:.0f} mm</div>"
            emb_html += "</div>"

            # Tabla precios
            rows = ""
            for r in res_final:
                rows += f"""
                <tr>
                    <td><b>{r['Cantidad']}</b></td>
                    <td>{r['Precio venta material (unitario)']}</td>
                    <td>{r['Precio venta embalaje (unitario)']}</td>
                    <td>{r['Precio venta troquel (TOTAL)']}</td>
                    <td><b style="color:#1E88E5;">{r['Precio venta unitario (todo)']}</b></td>
                    <td>{r['Precio venta total']}</td>
                </tr>
                """

            tabla = f"""
            <div class='sec-title'>€ Precios de venta</div>
            <table class="comercial-table">
                <tr>
                    <th>Cantidad</th>
                    <th>Venta material (unit)</th>
                    <th>Venta embalaje (unit)</th>
                    <th>Troquel (TOTAL)</th>
                    <th>UNITARIO (TODO)</th>
                    <th>VENTA TOTAL</th>
                </tr>
                {rows}
            </table>
            <div class="small muted" style="margin-top:10px;">
                * "Venta material" incluye todos los costes del producido excepto extras, embalajes y troqueles. IVA no incluido.
            </div>
            """

            st.markdown(f"""
            <div class="comercial-box">
                <div class="comercial-header">OFERTA COMERCIAL - {st.session_state.cli or "CLIENTE"}</div>
                <div class="comercial-ref">Ref. Briefing: {st.session_state.brf or "-"}</div>
                {desc_html}
                {extras_html}
                {emb_html}
                {tabla}
            </div>
            """, unsafe_allow_html=True)

        else:
            # Admin: tabla y auditoría
            if res_final:
                st.header(f"📊 Resumen de Venta: {st.session_state.cli}")
                df = pd.DataFrame(res_final)[[
                    "Cantidad",
                    "Precio venta material (unitario)",
                    "Precio venta embalaje (unitario)",
                    "Precio venta troquel (TOTAL)",
                    "Precio venta unitario (todo)",
                    "Precio venta total"
                ]]
                st.dataframe(df, use_container_width=True)

                for q, info in desc_full.items():
                    with st.expander(f"🔍 Auditoría de Costes (ADMIN) — {q} uds", expanded=False):
                        st.subheader("Auditoría de partidas")
                        df_raw = pd.DataFrame(info["det"])
                        cols = ["Pieza","Cartoncillo Cara","Cartoncillo Dorso","Plancha Ondulado","Material Rígido","Contracolado","Impresión","Peliculado","Corte (Troquel/Plotter)","Subtotal Pieza"]
                        st.table(df_raw[cols].style.format("{:.2f}€", subset=cols[1:]))

                        st.markdown("### Totales")
                        st.metric("Coste fabricación (piezas)", f"{info['coste_fabrica']:.2f}€")
                        st.metric("Coste mano de obra", f"{info['mo']:.2f}€")
                        st.metric("Coste extras", f"{info['extras']:.2f}€")
                        st.metric("Coste embalaje (compra)", f"{info['emb_compra_total']:.2f}€")
                        st.metric("Venta material total (sin extras/emb/troquel)", f"{info['pv_material_total']:.2f}€")
                        st.metric("Venta embalaje total", f"{info['pv_emb_total']:.2f}€")
                        st.metric("Troquel venta total", f"{info['tot_pv_trq']:.2f}€")
                        st.metric("VENTA TOTAL", f"{info['total']:.2f}€")

    else:
        # Operario: coste visible de venta (lo que pediste, SIN más info)
        if res_final:
            st.success("✅ Cálculo Realizado")
            df = pd.DataFrame(res_final)[[
                "Cantidad",
                "Precio venta material (unitario)",
                "Precio venta embalaje (unitario)",
                "Precio venta troquel (TOTAL)",
                "Precio venta unitario (todo)"
            ]]
            st.table(df)

# =========================================================
# TAB DEBUG (ADMIN)
# =========================================================
if tab_debug:
    with tab_debug:
        if lista_cants and desc_full:
            sq = st.selectbox("Ver detalle:", lista_cants, key="dbg_sel")
            st.subheader("Desglose de cálculos (solo líneas con fórmulas)")
            for l in desc_full[sq]["debug"]:
                st.markdown(l, unsafe_allow_html=True)
        else:
            st.info("No hay desglose aún. Define cantidades y calcula.")
