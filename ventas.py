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
# 2) FLEXICO (igual)
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
# 3) PRECIOS BASE + RÍGIDOS ACTUALIZADOS
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
    """Devuelve (merma_rodaje_proceso_hojas, merma_arranque_impresion_hojas).

    Regla: merma de rodaje/proceso proporcional con tope máximo de 150 hojas.
    """
    # Rodaje proceso: proporcional pero capado
    if es_digital:
        merma_proc = min(int(n * 0.02), 150)
        return merma_proc, 10

    if n < 100:
        merma_proc, merma_imp = 10, 150
    elif n < 200:
        merma_proc, merma_imp = 20, 175
    elif n < 600:
        merma_proc, merma_imp = 30, 200
    elif n < 1000:
        merma_proc, merma_imp = 40, 220
    elif n < 2000:
        merma_proc, merma_imp = 50, 250
    else:
        merma_proc, merma_imp = int(n * 0.03), 300

    return min(int(merma_proc), 150), int(merma_imp)


def parse_cantidades(s: str):
    if not s:
        return []
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
    if Q <= 0 or L_mm <= 0 or W_mm <= 0 or H_mm <= 0:
        return 0.0, 0.0
    L = L_mm / 1000.0
    W = W_mm / 1000.0
    H = H_mm / 1000.0
    S = (L * W) + 2.0 * H * (L + W)
    P = ((152.0 + (20.0 * S)) / float(Q)) + 0.15 + (1.02 * S)
    return float(P), float(S)

def embalaje_volumen_unit(L_mm, A_mm, H_mm, Q):
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
        "costes": {}
    }

# =========================================================
# EXTERNOS (PROVEEDORES ESPORÁDICOS)
# =========================================================
EXT_TIPOS_COSTE = ["Unitario (€/ud)", "Total (€)"]

def crear_externo_vacio(idx: int):
    return {
        "id": f"ext_{idx}",
        "concepto": f"Externo {idx+1}",
        "modo": "Unitario (€/ud)",
        "costes": {}  # por cantidad -> float (€/ud o € total)
    }

# =========================================================
# RÍGIDOS - MERMA FIJA (si NO hay contracolado)
# =========================================================
def merma_rigido_fija(hojas_netas: int) -> int:
    if hojas_netas <= 10:
        return 0
    if hojas_netas <= 50:
        return 1
    if hojas_netas <= 100:
        return 2
    if hojas_netas <= 300:
        return 3
    if hojas_netas <= 500:
        return 5
    if hojas_netas <= 750:
        return 7
    return 10

# =========================================================
# IMPRESIÓN OFFSET - NUEVA TARIFA
# =========================================================
def coste_offset_por_tinta(n_hojas: int) -> float:
    """
    Regla verificada con ejemplo:
    - Mínimo 85€ por tinta.
    - Hojas extra hasta 500: 0,0875€/hoja/tinta (contando desde hoja 101).
    - A partir de 501: 120€/tinta (mantiene el comportamiento anterior base).
    - A partir de 2001: +0,015€/hoja/tinta (permite cuadrar 2500 → 510 con 4 tintas)
    """
    n = max(0, int(round(n_hojas)))
    if n <= 100:
        return 85.0
    if n <= 500:
        extra = (n - 100) * 0.0875
        return 85.0 + extra
    base = 120.0
    if n > 2000:
        base += (n - 2000) * 0.015
    return base

# =========================================================
# FORMAS
# =========================================================
def crear_forma_vacia(index):
    # ✅ Formas 1..n (no 0)
    return {
        "nombre": f"Forma {index}",
        "pliegos": 1.0,
        "w": 0, "h": 0,
        "pf": "Ninguno", "gf": 0,
        "pd": "Ninguno", "gd": 0,
        "tipo_base": "Ondulado/Cartón",
        "pl": "Ninguna", "ap": "B/C",
        "pl_dif": False, "pl_h": 0, "pl_w": 0,
        "mat_rigido": "Ninguno",
        "rig_manual": False,
        "rig_w": 0, "rig_h": 0, "rig_precio_ud": 0.0,
        "im": "No", "nt": 0, "ba": False,
        "im_d": "No", "nt_d": 0, "ba_d": False,
        "pel": "Sin Peliculado",
        "pel_d": "Sin Peliculado",
        "ld": False, "ld_d": False,
        "cor_default": "Troquelado",
        "cor_by_qty": {},
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
if "piezas_dict" not in st.session_state: st.session_state.piezas_dict = {1: crear_forma_vacia(1)}
if "lista_extras_grabados" not in st.session_state: st.session_state.lista_extras_grabados = []
if "embalajes" not in st.session_state: st.session_state.embalajes = [crear_embalaje_vacio(0)]
if "externos" not in st.session_state: st.session_state.externos = [crear_externo_vacio(0)]
if "mermas_imp_manual" not in st.session_state: st.session_state.mermas_imp_manual = {}
if "mermas_imp_digital_manual" not in st.session_state: st.session_state.mermas_imp_digital_manual = {}
if "mermas_proc_manual" not in st.session_state: st.session_state.mermas_proc_manual = {}

if "brf" not in st.session_state: st.session_state.brf = ""
if "cli" not in st.session_state: st.session_state.cli = ""
if "desc" not in st.session_state: st.session_state.desc = ""
if "cants_str_saved" not in st.session_state: st.session_state.cants_str_saved = ""

if "unidad_t" not in st.session_state: st.session_state.unidad_t = "Segundos"
if "t_input" not in st.session_state: st.session_state.t_input = 0.0

if "dif_ud" not in st.session_state: st.session_state.dif_ud = 0.091
if "imp_fijo_pvp" not in st.session_state: st.session_state.imp_fijo_pvp = 500.0
if "margen" not in st.session_state: st.session_state.margen = 2.2

if "descuento_procesos" not in st.session_state: st.session_state.descuento_procesos = 0.0
if "margen_extras" not in st.session_state: st.session_state.margen_extras = 1.4
if "margen_embalajes" not in st.session_state: st.session_state.margen_embalajes = 1.4

if "db_descuentos" not in st.session_state:
    # Descuentos de compra por bloque (en %). Se aplican a los costes en cálculo.
    st.session_state.db_descuentos = {
        "cartoncillo": 0.0,
        "ondulado_rigidos": 0.0,
        "narba": 0.0,
    }


if "_last_import_hash" not in st.session_state: st.session_state._last_import_hash = None
if "_export_blob" not in st.session_state: st.session_state._export_blob = None
if "_export_filename" not in st.session_state: st.session_state._export_filename = "oferta.json"

# =========================================================
# FIX IMPORT: PURGE KEYS DE WIDGETS
# =========================================================
def purge_widget_keys_for_import(lista_cants=None, piezas_ids=None, externos_len=0, embalajes_len=0, extras_len=0):
    """
    Streamlit prioriza st.session_state[widget_key] sobre value=.
    Al importar, limpiamos claves de widgets para que se recarguen desde el JSON.
    """
    if piezas_ids is None:
        piezas_ids = []
    if lista_cants is None:
        lista_cants = []

    base_prefixes = [
        "n_", "p_", "std_", "h_", "w_", "im_", "nt_", "ba_", "ld_", "pel_",
        "pf_", "gf_", "tb_", "pl_", "pldif_", "plh_", "plw_", "ap_",
        "rigman_", "rigwman_", "righman_", "rigpman_", "mrig_",
        "pd_", "gd_", "cor_def_", "arr_", "pvt_", "im_d_", "nt_d_", "ba_d_", "ld_d_", "pel_d_"
    ]

    for pid in piezas_ids:
        for pref in base_prefixes:
            k = f"{pref}{pid}"
            if k in st.session_state:
                del st.session_state[k]

        for q in lista_cants:
            kq = f"cor_qty_{pid}_{q}"
            if kq in st.session_state:
                del st.session_state[kq]

        kdel = f"del_{pid}"
        if kdel in st.session_state:
            del st.session_state[kdel]

    for q in lista_cants:
        for k in [f"mi_{q}", f"mp_{q}"]:
            if k in st.session_state:
                del st.session_state[k]

    for i in range(max(0, extras_len)):
        for k in [f"exc_{i}", f"exq_{i}", f"exd_{i}"]:
            if k in st.session_state:
                del st.session_state[k]

    for ei in range(max(0, embalajes_len)):
        for k in [f"emb_name_{ei}", f"emb_tipo_{ei}", f"emb_mat_{ei}", f"embL_{ei}", f"embW_{ei}", f"embH_{ei}", f"emb_del_{ei}"]:
            if k in st.session_state:
                del st.session_state[k]
        for q in lista_cants:
            kq = f"embMan_{ei}_{q}"
            if kq in st.session_state:
                del st.session_state[kq]

    for xi in range(max(0, externos_len)):
        for k in [f"ext_con_{xi}", f"ext_modo_{xi}", f"ext_del_{xi}"]:
            if k in st.session_state:
                del st.session_state[k]
        for q in lista_cants:
            kq = f"ext_{xi}_{q}"
            if kq in st.session_state:
                del st.session_state[kq]

# =========================================================
# FIX IMPORT: SEED KEYS DE WIDGETS CON LO IMPORTADO (TODAS LAS FORMAS)
# =========================================================
def seed_widget_keys_from_import(lista_cants, piezas_dict):
    """
    Streamlit prioriza st.session_state[widget_key] sobre value=.
    Sembramos las keys de widgets con los valores importados para que NO se pierdan.
    """
    for pid, p in piezas_dict.items():
        st.session_state[f"n_{pid}"] = p.get("nombre", f"Forma {pid}")
        st.session_state[f"p_{pid}"] = float(p.get("pliegos", 1.0))

        st.session_state[f"h_{pid}"] = int(p.get("h", 0))
        st.session_state[f"w_{pid}"] = int(p.get("w", 0))

        st.session_state[f"im_{pid}"] = p.get("im", "No")
        st.session_state[f"nt_{pid}"] = int(p.get("nt", 0))
        st.session_state[f"ba_{pid}"] = bool(p.get("ba", False))
        st.session_state[f"ld_{pid}"] = bool(p.get("ld", False))
        st.session_state[f"pel_{pid}"] = p.get("pel", "Sin Peliculado")

        st.session_state[f"pf_{pid}"] = p.get("pf", "Ninguno")
        st.session_state[f"gf_{pid}"] = int(p.get("gf", 0))

        st.session_state[f"tb_{pid}"] = p.get("tipo_base", "Ondulado/Cartón")
        st.session_state[f"pl_{pid}"] = p.get("pl", "Ninguna")
        st.session_state[f"ap_{pid}"] = p.get("ap", "B/C")
        st.session_state[f"pldif_{pid}"] = bool(p.get("pl_dif", False))
        st.session_state[f"plh_{pid}"] = int(p.get("pl_h", p.get("h", 0)))
        st.session_state[f"plw_{pid}"] = int(p.get("pl_w", p.get("w", 0)))

        st.session_state[f"mrig_{pid}"] = p.get("mat_rigido", "Ninguno")
        st.session_state[f"rigman_{pid}"] = bool(p.get("rig_manual", False))
        st.session_state[f"rigwman_{pid}"] = int(p.get("rig_w", 0))
        st.session_state[f"righman_{pid}"] = int(p.get("rig_h", 0))
        st.session_state[f"rigpman_{pid}"] = float(p.get("rig_precio_ud", 0.0))

        st.session_state[f"pd_{pid}"] = p.get("pd", "Ninguno")
        st.session_state[f"gd_{pid}"] = int(p.get("gd", 0))

        st.session_state[f"cor_def_{pid}"] = p.get("cor_default", "Troquelado")
        if isinstance(p.get("cor_by_qty", {}), dict):
            for q in lista_cants:
                st.session_state[f"cor_qty_{pid}_{q}"] = p["cor_by_qty"].get(str(q), p.get("cor_default", "Troquelado"))

        st.session_state[f"arr_{pid}"] = bool(p.get("cobrar_arreglo", True))
        st.session_state[f"pvt_{pid}"] = float(p.get("pv_troquel", 0.0))

        st.session_state[f"im_d_{pid}"] = p.get("im_d", "No")
        st.session_state[f"nt_d_{pid}"] = int(p.get("nt_d", 0))
        st.session_state[f"ba_d_{pid}"] = bool(p.get("ba_d", False))
        st.session_state[f"ld_d_{pid}"] = bool(p.get("ld_d", False))
        st.session_state[f"pel_d_{pid}"] = p.get("pel_d", "Sin Peliculado")

# =========================================================
# IMPORT NORMALIZADO (ROBUSTO): GARANTIZA QUE SE CARGAN TODOS LOS CAMPOS
# =========================================================
def _coerce_bool(x, default=False):
    try:
        return bool(x)
    except:
        return default

def _coerce_int(x, default=0):
    try:
        return int(float(x))
    except:
        return default

def _coerce_float(x, default=0.0):
    try:
        return float(x)
    except:
        return default

def _normalizar_pieza_dict(pid: int, v: dict):
    base = crear_forma_vacia(pid)
    if isinstance(v, dict):
        base.update(v)

    base["nombre"] = str(base.get("nombre", f"Forma {pid}"))
    base["pliegos"] = _coerce_float(base.get("pliegos", 1.0), 1.0)

    base["w"] = _coerce_int(base.get("w", 0), 0)
    base["h"] = _coerce_int(base.get("h", 0), 0)

    base["pf"] = str(base.get("pf", "Ninguno"))
    base["gf"] = _coerce_int(base.get("gf", 0), 0)
    base["pd"] = str(base.get("pd", "Ninguno"))
    base["gd"] = _coerce_int(base.get("gd", 0), 0)

    base["tipo_base"] = str(base.get("tipo_base", "Ondulado/Cartón"))

    # ✅ blindaje plancha / calidad
    base["pl"] = str(base.get("pl", "Ninguna"))
    base["ap"] = str(base.get("ap", "B/C"))
    base["pl_dif"] = _coerce_bool(base.get("pl_dif", False), False)
    base["pl_h"] = _coerce_int(base.get("pl_h", base.get("h", 0)), 0)
    base["pl_w"] = _coerce_int(base.get("pl_w", base.get("w", 0)), 0)

    base["mat_rigido"] = str(base.get("mat_rigido", "Ninguno"))
    base["rig_manual"] = _coerce_bool(base.get("rig_manual", False), False)
    base["rig_w"] = _coerce_int(base.get("rig_w", 0), 0)
    base["rig_h"] = _coerce_int(base.get("rig_h", 0), 0)
    base["rig_precio_ud"] = _coerce_float(base.get("rig_precio_ud", 0.0), 0.0)

    base["im"] = str(base.get("im", "No"))
    base["nt"] = _coerce_int(base.get("nt", 0), 0)
    base["ba"] = _coerce_bool(base.get("ba", False), False)
    base["ld"] = _coerce_bool(base.get("ld", False), False)
    base["pel"] = str(base.get("pel", "Sin Peliculado"))

    base["im_d"] = str(base.get("im_d", "No"))
    base["nt_d"] = _coerce_int(base.get("nt_d", 0), 0)
    base["ba_d"] = _coerce_bool(base.get("ba_d", False), False)
    base["ld_d"] = _coerce_bool(base.get("ld_d", False), False)
    base["pel_d"] = str(base.get("pel_d", "Sin Peliculado"))

    base["cor_default"] = str(base.get("cor_default", "Troquelado"))
    if not isinstance(base.get("cor_by_qty", {}), dict):
        base["cor_by_qty"] = {}
    else:
        base["cor_by_qty"] = {str(k): str(vv) for k, vv in base["cor_by_qty"].items()}

    base["cobrar_arreglo"] = _coerce_bool(base.get("cobrar_arreglo", True), True)
    base["pv_troquel"] = _coerce_float(base.get("pv_troquel", 0.0), 0.0)

    return base

def normalizar_import(di: dict):
    prev_cants = parse_cantidades(st.session_state.get("cants_str_saved", ""))
    prev_piezas_ids = list(st.session_state.get("piezas_dict", {}).keys()) if isinstance(st.session_state.get("piezas_dict", None), dict) else []
    prev_extras_len = len(st.session_state.get("lista_extras_grabados", [])) if isinstance(st.session_state.get("lista_extras_grabados", None), list) else 0
    prev_emb_len = len(st.session_state.get("embalajes", [])) if isinstance(st.session_state.get("embalajes", None), list) else 0
    prev_ext_len = len(st.session_state.get("externos", [])) if isinstance(st.session_state.get("externos", None), list) else 0

    st.session_state.brf = str(di.get("brf", st.session_state.brf))
    st.session_state.cli = str(di.get("cli", st.session_state.cli))
    st.session_state.desc = str(di.get("desc", st.session_state.desc))
    if isinstance(di.get("cants_str", None), str):
        st.session_state.cants_str_saved = di["cants_str"]

    manip = di.get("manip", {})
    if isinstance(manip, dict):
        if "unidad_t" in manip:
            st.session_state.unidad_t = str(manip["unidad_t"])
        if "t_input" in manip:
            st.session_state.t_input = float(manip["t_input"])

    params = di.get("params", {})
    if isinstance(params, dict):
        if "dif_ud" in params: st.session_state.dif_ud = float(params["dif_ud"])
        if "imp_fijo_pvp" in params: st.session_state.imp_fijo_pvp = float(params["imp_fijo_pvp"])
        if "margen" in params: st.session_state.margen = float(params["margen"])
        # ✅ Nuevos (compatibles hacia atrás)
        if "descuento_procesos" in params: st.session_state.descuento_procesos = float(params["descuento_procesos"])
        if "margen_extras" in params: st.session_state.margen_extras = float(params["margen_extras"])
        if "margen_embalajes" in params: st.session_state.margen_embalajes = float(params["margen_embalajes"])

    if isinstance(di.get("db_precios", None), dict):
        st.session_state.db_precios = di["db_precios"]

    # ✅ Descuentos por bloque (si vienen en el JSON)
    if isinstance(di.get("db_descuentos", None), dict):
        cur = st.session_state.get("db_descuentos", {})
        if not isinstance(cur, dict):
            cur = {}
        for k, v in di["db_descuentos"].items():
            try:
                cur[str(k)] = float(v)
            except Exception:
                pass
        for k0 in ["cartoncillo", "ondulado_rigidos", "narba"]:
            cur.setdefault(k0, 0.0)
        st.session_state.db_descuentos = cur

    lista_cants_import = parse_cantidades(st.session_state.cants_str_saved)
    cants_all = sorted(set(prev_cants + lista_cants_import))

    raw = []
    piezas_in = di.get("piezas", None)

    # ✅ Import robusto:
    # - Si el JSON trae piezas como dict ({"1": {...}, "6": {...}}), mantenemos SUS IDs
    #   para que "Forma 6" siga siendo la 6 (y no se renumere).
    # - Si viene como lista, seguimos usando 1..n.
    if isinstance(piezas_in, dict):
        for k, v in piezas_in.items():
            try:
                ik = int(k)
            except:
                continue
            if isinstance(v, dict):
                raw.append((ik, v))
        raw.sort(key=lambda x: x[0])
    elif isinstance(piezas_in, list):
        for idx, v in enumerate(piezas_in, start=1):
            if isinstance(v, dict):
                raw.append((idx, v))

    new_piezas = {1: crear_forma_vacia(1)}
    new_ids = [1]
    if raw:
        new_piezas = {}
        new_ids = []
        for pid, v in raw:
            new_piezas[pid] = _normalizar_pieza_dict(pid, v)
            new_ids.append(pid)

    piezas_all = sorted(set(prev_piezas_ids + new_ids))
    purge_widget_keys_for_import(
        lista_cants=cants_all,
        piezas_ids=piezas_all,
        externos_len=max(prev_ext_len, len(di.get("externos", []) if isinstance(di.get("externos", None), list) else []), 1),
        embalajes_len=max(prev_emb_len, len(di.get("embalajes", []) if isinstance(di.get("embalajes", None), list) else []), 1),
        extras_len=max(prev_extras_len, len(di.get("extras", []) if isinstance(di.get("extras", None), list) else []), 0),
    )

    st.session_state.piezas_dict = new_piezas if new_piezas else {1: crear_forma_vacia(1)}

    if isinstance(di.get("extras", None), list):
        st.session_state.lista_extras_grabados = di["extras"]

    if isinstance(di.get("mermas_imp", None), dict):
        st.session_state.mermas_imp_manual = {int(k): int(v) for k, v in di["mermas_imp"].items()}
    if isinstance(di.get("mermas_imp_digital", None), dict):
        st.session_state.mermas_imp_digital_manual = {int(k): int(v) for k, v in di["mermas_imp_digital"].items()}
    if isinstance(di.get("mermas_proc", None), dict):
        st.session_state.mermas_proc_manual = {int(k): int(v) for k, v in di["mermas_proc"].items()}

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

    ext = di.get("externos", None)
    if isinstance(ext, list) and len(ext) > 0:
        new_ext = []
        for idx, e in enumerate(ext):
            if not isinstance(e, dict):
                continue
            base = crear_externo_vacio(idx)
            base["id"] = str(e.get("id", base["id"]))
            base["concepto"] = str(e.get("concepto", base["concepto"]))
            base["modo"] = str(e.get("modo", base["modo"]))
            if isinstance(e.get("costes", None), dict):
                base["costes"] = {int(k): float(v) for k, v in e["costes"].items()}
            new_ext.append(base)
        st.session_state.externos = new_ext if new_ext else [crear_externo_vacio(0)]
    else:
        if "externos" not in st.session_state or not st.session_state.externos:
            st.session_state.externos = [crear_externo_vacio(0)]

    purge_widget_keys_for_import(
        lista_cants=lista_cants_import,
        piezas_ids=list(st.session_state.piezas_dict.keys()),
        externos_len=len(st.session_state.externos),
        embalajes_len=len(st.session_state.embalajes),
        extras_len=len(st.session_state.lista_extras_grabados),
    )

    seed_widget_keys_from_import(
        lista_cants=lista_cants_import,
        piezas_dict=st.session_state.piezas_dict
    )

# =========================================================
# EXPORT ROBUSTO
# =========================================================
def construir_export(resumen_compra=None, resumen_costes=None):
    piezas_out = {}
    for pid, p in st.session_state.piezas_dict.items():
        piezas_out[str(int(pid))] = deepcopy(p)

    data = {
        "_schema": {"app": "MAINSA ADMIN V44", "piezas_index_base": 1},
        "brf": st.session_state.brf,
        "cli": st.session_state.cli,
        "desc": st.session_state.desc,
        "cants_str": st.session_state.cants_str_saved,
        "manip": {"unidad_t": st.session_state.unidad_t, "t_input": float(st.session_state.t_input)},
        "params": {"dif_ud": float(st.session_state.dif_ud), "imp_fijo_pvp": float(st.session_state.imp_fijo_pvp), "margen": float(st.session_state.margen), "descuento_procesos": float(st.session_state.descuento_procesos), "margen_extras": float(st.session_state.margen_extras), "margen_embalajes": float(st.session_state.margen_embalajes)},
        "db_precios": deepcopy(st.session_state.db_precios),
        "db_descuentos": deepcopy(st.session_state.db_descuentos),
        "piezas": piezas_out,
        "extras": deepcopy(st.session_state.lista_extras_grabados),
        "embalajes": deepcopy(st.session_state.embalajes),
        "externos": deepcopy(st.session_state.externos),
        "mermas_imp": deepcopy(st.session_state.mermas_imp_manual),
        "mermas_imp_digital": deepcopy(st.session_state.mermas_imp_digital_manual),
        "mermas_proc": deepcopy(st.session_state.mermas_proc_manual),
    }
    if resumen_compra is not None:
        data["compras_legible"] = resumen_compra
    if resumen_costes is not None:
        data["resumen_costes"] = resumen_costes
    return data

# =========================================================
# CSS
# =========================================================
CSS_COMERCIAL = """
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
    .warn{background:#fff7e6;border:1px solid #ffe0a3;padding:10px;border-radius:10px;}
</style>
"""
st.markdown(CSS_COMERCIAL, unsafe_allow_html=True)

st.title("🛡️ PANEL ADMIN - ESCANDALLO")

# =========================================================
# SIDEBAR (visualización + import/export)
# =========================================================
with st.sidebar:
    st.header("📦 JSON / Visualización")
    modo_comercial = st.checkbox("🌟 VISTA OFERTA", value=st.session_state.get("modo_oferta", False), key="modo_oferta")

    st.divider()

    with st.expander("📥 Importar JSON", expanded=False):
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

    with st.expander("📤 Exportar JSON", expanded=True):
        if st.session_state._export_blob:
            st.download_button(
                "💾 Descargar JSON",
                data=st.session_state._export_blob,
                file_name=st.session_state._export_filename,
                mime="application/json"
            )
        else:
            st.caption("Calcula una vez para habilitar la exportación.")

# =========================================================
# PESTAÑAS (SIEMPRE ADMIN)
# =========================================================
tab_calculadora, tab_costes, tab_debug = st.tabs(["🧮 Calculadora", "💰 Base de Datos", "🔍 Desglose"])

# =========================================================
# TAB COSTES (siempre visible)
# =========================================================
with tab_costes:
    col_c1, col_c2 = st.columns(2)
    db = st.session_state.db_precios

    # defaults descuentos (por si vienen viejos)
    if "db_descuentos" not in st.session_state or not isinstance(st.session_state.db_descuentos, dict):
        st.session_state.db_descuentos = {"cartoncillo": 0.0, "ondulado_rigidos": 0.0, "narba": 0.0}
    for _k0 in ["cartoncillo", "ondulado_rigidos", "narba"]:
        st.session_state.db_descuentos.setdefault(_k0, 0.0)

    with col_c1:
        with st.expander("📄 Cartoncillo (€/Kg)", expanded=True):
            st.session_state.db_descuentos["cartoncillo"] = st.number_input(
                "Descuento bloque Cartoncillo (%)",
                min_value=0.0, max_value=100.0, step=0.5,
                value=float(st.session_state.db_descuentos.get("cartoncillo", 0.0)),
                key="db_desc_cart"
            )
            for k, v in db["cartoncillo"].items():
                if k != "Ninguno":
                    db["cartoncillo"][k]["precio_kg"] = st.number_input(
                        f"{k} (€/kg)", value=float(v["precio_kg"]), key=f"cost_cart_{k}"
                    )

        with st.expander("🧱 Ondulado y Rígidos (€/hoja)", expanded=True):
            st.session_state.db_descuentos["ondulado_rigidos"] = st.number_input(
                "Descuento bloque Ondulado + Rígidos (%)",
                min_value=0.0, max_value=100.0, step=0.5,
                value=float(st.session_state.db_descuentos.get("ondulado_rigidos", 0.0)),
                key="db_desc_or"
            )

            st.markdown("##### Ondulado")
            for k, v in db["planchas"].items():
                if k != "Ninguna":
                    st.markdown(f"**{k}**")
                    # ✅ 'peg' se gestiona en NARBA, aquí solo calidades de plancha
                    vv = {kk: sv for kk, sv in v.items() if kk != "peg"}
                    cols = st.columns(len(vv)) if vv else st.columns(1)
                    for idx, (sk, sv) in enumerate(vv.items()):
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
        with st.expander("✨ Acabados (otros)", expanded=True):
            # Laminado digital se mantiene aquí (no NARBA)
            db["laminado_digital"] = st.number_input(
                "Laminado Digital", value=float(db.get("laminado_digital", 3.5)), key="cost_lam_dig"
            )

        with st.expander("🧩 NARBA (Procesos: Contracolado · Peliculado · Troquelado)", expanded=True):
            st.session_state.db_descuentos["narba"] = st.number_input(
                "Descuento bloque NARBA (%)",
                min_value=0.0, max_value=100.0, step=0.5,
                value=float(st.session_state.db_descuentos.get("narba", 0.0)),
                key="db_desc_narba"
            )

            st.markdown("##### Contracolado (€/m² por capa)")
            for k, v in db["planchas"].items():
                if k != "Ninguna":
                    if "peg" in v:
                        db["planchas"][k]["peg"] = st.number_input(
                            f"{k} · peg", value=float(v["peg"]), key=f"cost_peg_{k}", format="%.4f"
                        )

            st.markdown("---")
            st.markdown("##### Peliculado (€/m²)")
            for k, v in db["peliculado"].items():
                if k != "Sin Peliculado":
                    db["peliculado"][k] = st.number_input(f"{k}", value=float(v), key=f"cost_pel_{k}")

            st.markdown("---")
            st.markdown("##### Troquelado")
            for k, v in db["troquelado"].items():
                st.markdown(f"**{k}**")
                c_arr, c_tir = st.columns(2)
                db["troquelado"][k]["arranque"] = c_arr.number_input(
                    "Arranque (€)", value=float(v["arranque"]), key=f"trq_arr_{k}"
                )
                db["troquelado"][k]["tiro"] = c_tir.number_input(
                    "Tiro (€/h)", value=float(v["tiro"]), format="%.4f", key=f"trq_tir_{k}"
                )

        with st.expander("✂️ Plotter", expanded=True):
            db["plotter"]["precio_hoja"] = st.number_input(
                "Corte Plotter (€/hoja)", value=float(db["plotter"]["precio_hoja"]), key="plotter_precio"
            )

        with st.expander("🖨️ Impresión Offset (info)", expanded=True):
            st.markdown(
                """
<div class="warn">
<b>Nueva regla Offset</b><br>
• Mínimo: <b>85€ por tinta</b> (hasta 100 hojas)<br>
• Hojas extra (101..500): <b>0,0875€ / hoja / tinta</b><br>
• 501..2000: <b>120€ por tinta</b><br>
• &gt;2000: <b>+0,015€ / hoja / tinta</b><br>
</div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# TAB CALCULADORA
# =========================================================
with tab_calculadora:
    db = st.session_state.db_precios

    st.header("Paso 1 · Datos de oferta")

    cA, cB, cC = st.columns([2, 2, 3])
    with cA:
        st.text_input("Nº Briefing", key="brf")
        st.text_input("Cliente", key="cli")
    with cB:
        st.text_input("Descripción", key="desc")
        st.text_input("Cantidades (ej: 500, 1000)", key="cants_str_saved")
    with cC:
        st.radio("Manipulación", ["Segundos", "Minutos"], horizontal=True, key="unidad_t")
        st.number_input("Tiempo/ud", min_value=0.0, value=float(st.session_state.t_input), step=1.0, key="t_input")

    lista_cants = parse_cantidades(st.session_state.cants_str_saved)

    unidad_t = st.session_state.unidad_t
    t_input = float(st.session_state.t_input)
    seg_man_total = t_input * 60 if unidad_t == "Minutos" else t_input

    with st.expander("💰 Finanzas", expanded=False):
        st.selectbox("Dificultad (€/ud)", [0.02, 0.061, 0.091], index=2, key="dif_ud")
        st.number_input("Fijo PVP (€)", value=float(st.session_state.imp_fijo_pvp), key="imp_fijo_pvp")
        st.number_input("Multiplicador", step=0.1, value=float(st.session_state.margen), key="margen")

        st.markdown("---")
        st.number_input("Descuento sobre PROCESOS (%)", min_value=0.0, max_value=100.0, step=0.5, value=float(st.session_state.descuento_procesos), key="descuento_procesos")
        st.number_input("Margen materiales EXTRA", min_value=1.0, step=0.05, value=float(st.session_state.margen_extras), key="margen_extras")
        st.number_input("Margen EMBALAJES", min_value=1.0, step=0.05, value=float(st.session_state.margen_embalajes), key="margen_embalajes")

    dif_ud = float(st.session_state.dif_ud)
    imp_fijo_pvp = float(st.session_state.imp_fijo_pvp)
    margen = float(st.session_state.margen)
    descuento_procesos = float(st.session_state.descuento_procesos)
    margen_extras = float(st.session_state.margen_extras)
    margen_embalajes = float(st.session_state.margen_embalajes)

    st.divider()

    if lista_cants:
        # Mermas por defecto:
        # - 'mermas_proc_manual' y 'mermas_imp_manual' se consideran la referencia "normal" (offset / general)
        # - 'mermas_imp_digital_manual' es específica para impresión digital
        for q in lista_cants:
            mp_off, mi_off = calcular_mermas_estandar(q, es_digital=False)
            _mp_dig, mi_dig = calcular_mermas_estandar(q, es_digital=True)

            if q not in st.session_state.mermas_proc_manual:
                st.session_state.mermas_proc_manual[q] = mp_off

            if q not in st.session_state.mermas_imp_manual:
                st.session_state.mermas_imp_manual[q] = mi_off

            if q not in st.session_state.mermas_imp_digital_manual:
                st.session_state.mermas_imp_digital_manual[q] = mi_dig

    # -----------------------------------------------------
    # PASO 2: TÉCNICO
    # -----------------------------------------------------
    st.header("Paso 2 · Datos técnicos")

    c_btns = st.columns([1, 4])
    if c_btns[0].button("➕ Forma"):
        nid = max(st.session_state.piezas_dict.keys()) + 1
        st.session_state.piezas_dict[nid] = crear_forma_vacia(nid)
        st.rerun()
    if c_btns[1].button("🗑 Reiniciar"):
        st.session_state.piezas_dict = {1: crear_forma_vacia(1)}
        st.session_state.lista_extras_grabados = []
        st.session_state.embalajes = [crear_embalaje_vacio(0)]
        st.session_state.externos = [crear_externo_vacio(0)]
        st.session_state.mermas_imp_manual = {}
        st.session_state.mermas_proc_manual = {}
        st.rerun()

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
            if not st.session_state.get(f"pldif_{pid}", False):
                st.session_state[f"plh_{pid}"] = nh
                st.session_state[f"plw_{pid}"] = nw

    def callback_rigido(pid):
        mat = st.session_state.get(f"mrig_{pid}", "Ninguno")
        if mat != "Ninguno":
            info = st.session_state.db_precios["rigidos"][mat]
            st.session_state[f"w_{pid}"] = int(info["w"])
            st.session_state[f"h_{pid}"] = int(info["h"])

    for p_id, p in st.session_state.piezas_dict.items():
        with st.expander(f"🛠 {p.get('nombre','Forma')} - {p.get('h',0)}x{p.get('w',0)} mm", expanded=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                p["nombre"] = st.text_input("Etiqueta", p.get("nombre", f"Forma {p_id}"), key=f"n_{p_id}")
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
                    p["rig_manual"] = st.checkbox("🧩 Rígido Manual (tamaño + precio)", value=bool(p.get("rig_manual", False)), key=f"rigman_{p_id}")

                    if p["rig_manual"]:
                        c_rw, c_rh, c_rp = st.columns(3)
                        p["rig_w"] = int(c_rw.number_input("Hoja w (mm)", 0, 10000, value=int(p.get("rig_w", 0)), key=f"rigwman_{p_id}"))
                        p["rig_h"] = int(c_rh.number_input("Hoja h (mm)", 0, 10000, value=int(p.get("rig_h", 0)), key=f"righman_{p_id}"))
                        p["rig_precio_ud"] = float(c_rp.number_input("Precio hoja (€)", 0.0, 999999.0, value=float(p.get("rig_precio_ud", 0.0)), step=0.01, key=f"rigpman_{p_id}"))
                        st.caption("Este rígido manual se usa SOLO en esta pieza.")
                        p["mat_rigido"] = "MANUAL"
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

                opts_pd = list(db["cartoncillo"].keys())
                val_pd = p.get("pd", "Ninguno")
                idx_pd = opts_pd.index(val_pd) if val_pd in opts_pd else 0
                p["pd"] = st.selectbox("Cartoncillo Dorso", opts_pd, index=idx_pd, key=f"pd_{p_id}",
                                       on_change=callback_cambio_dorso, args=(p_id,))
                if p["pd"] != "Ninguno":
                    p["gd"] = st.number_input("Gramaje Dorso (g)", value=int(p.get("gd", 0)), key=f"gd_{p_id}")
                else:
                    p["gd"] = 0

            with col3:
                st.markdown("##### Corte")
                opts_cor = ["Troquelado", "Plotter"]
                val_cor = p.get("cor_default", p.get("cor", "Troquelado"))
                idx_cor = opts_cor.index(val_cor) if val_cor in opts_cor else 0
                p["cor_default"] = st.selectbox("Corte (por defecto)", opts_cor, index=idx_cor, key=f"cor_def_{p_id}")

                if lista_cants:
                    st.caption("Corte por cantidad (opcional):")
                    if not isinstance(p.get("cor_by_qty", {}), dict):
                        p["cor_by_qty"] = {}
                    for q in lista_cants:
                        cur = p["cor_by_qty"].get(str(q), p["cor_default"])
                        idxq = opts_cor.index(cur) if cur in opts_cor else idx_cor
                        p["cor_by_qty"][str(q)] = st.selectbox(
                            f"{q} uds", opts_cor, index=idxq, key=f"cor_qty_{p_id}_{q}"
                        )

                st.divider()

                p["cobrar_arreglo"] = st.checkbox("¿Cobrar Arreglo?", value=bool(p.get("cobrar_arreglo", True)), key=f"arr_{p_id}")
                p["pv_troquel"] = st.number_input("Precio Venta Troquel (€) (si aplica)", value=float(p.get("pv_troquel", 0.0)), key=f"pvt_{p_id}")

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

                    opts_pel = list(db["peliculado"].keys())
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
        ex["coste"] = c2.number_input("€/ud compra", value=float(ex.get("coste", 0.0)), key=f"exc_{i}", format="%.4f")
        ex["cantidad"] = c3.number_input("Cant/Ud prod", value=float(ex.get("cantidad", 1.0)), key=f"exq_{i}")
        if c4.button("🗑", key=f"exd_{i}"):
            st.session_state.lista_extras_grabados.pop(i)
            st.rerun()

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
        st.warning("Define cantidades en Paso 1.")
    else:
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

                d1, d2, d3 = st.columns(3)
                emb["dims"]["L"] = float(d1.number_input("Largo mm", value=float(emb["dims"].get("L",0.0)), key=f"embL_{ei}"))
                emb["dims"]["W"] = float(d2.number_input("Ancho mm", value=float(emb["dims"].get("W",0.0)), key=f"embW_{ei}"))
                emb["dims"]["H"] = float(d3.number_input("Alto mm", value=float(emb["dims"].get("H",0.0)), key=f"embH_{ei}"))

                mult = emb_mult(emb["material"])
                cols = st.columns(len(lista_cants))

                for idx, q in enumerate(lista_cants):
                    if emb["tipo"] == "Manual":
                        emb["costes"][q] = float(cols[idx].number_input(f"Coste compra {q}", value=float(emb["costes"].get(q, 0.0)), key=f"embMan_{ei}_{q}"))
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

    st.divider()
    st.subheader("📌 4. Externos (proveedores / procesos esporádicos)")

    cX1, cX2 = st.columns([1, 4])
    if cX1.button("➕ Añadir externo"):
        if len(st.session_state.externos) < 10:
            st.session_state.externos.append(crear_externo_vacio(len(st.session_state.externos)))
            st.rerun()
        else:
            st.warning("Máximo 10 externos.")

    if cX2.button("🗑 Reset externos"):
        st.session_state.externos = [crear_externo_vacio(0)]
        st.rerun()

    if not lista_cants:
        st.warning("Define cantidades en Paso 1 para poder asignar costes por cantidad.")
    else:
        for xi, ext in enumerate(st.session_state.externos):
            with st.expander(f"📌 {ext.get('concepto', f'Externo {xi+1}')}", expanded=True):
                c1, c2, c3 = st.columns([3, 2, 1])
                ext["concepto"] = c1.text_input("Concepto", value=ext.get("concepto", f"Externo {xi+1}"), key=f"ext_con_{xi}")
                ext["modo"] = c2.selectbox("Modo coste", EXT_TIPOS_COSTE, index=EXT_TIPOS_COSTE.index(ext.get("modo","Unitario (€/ud)")) if ext.get("modo","Unitario (€/ud)") in EXT_TIPOS_COSTE else 0, key=f"ext_modo_{xi}")
                if c3.button("🗑", key=f"ext_del_{xi}"):
                    if len(st.session_state.externos) > 1:
                        st.session_state.externos.pop(xi)
                        st.rerun()
                    else:
                        st.warning("Debe existir al menos 1 externo.")

                cols = st.columns(len(lista_cants))
                for idx, q in enumerate(lista_cants):
                    label = f"{q} uds (€ / ud)" if ext["modo"] == "Unitario (€/ud)" else f"{q} uds (Total €)"
                    ext["costes"][q] = float(cols[idx].number_input(label, value=float(ext.get("costes", {}).get(q, 0.0)), step=0.01, key=f"ext_{xi}_{q}"))

    st.divider()
    st.subheader("⚙️ 5. Gestión de Mermas (auto-relleno)")
    if lista_cants:
        for q in lista_cants:
            c1, c2, c3, c4 = st.columns([1, 2, 2, 2])
            c1.markdown(f"**{q} uds**")
            st.session_state.mermas_imp_manual[q] = int(
                c2.number_input(
                    "Arranque impresión OFFSET (hojas)",
                    value=int(st.session_state.mermas_imp_manual.get(q, 0)),
                    key=f"mi_{q}",
                )
            )
            st.session_state.mermas_imp_digital_manual[q] = int(
                c3.number_input(
                    "Arranque impresión DIGITAL (hojas)",
                    value=int(st.session_state.mermas_imp_digital_manual.get(q, 0)),
                    key=f"mid_{q}",
                )
            )
            st.session_state.mermas_proc_manual[q] = int(
                c4.number_input(
                    "Rodaje proceso (hojas)",
                    value=int(st.session_state.mermas_proc_manual.get(q, 0)),
                    key=f"mp_{q}",
                )
            )
    else:
        st.warning("Define cantidades en Paso 1.")

# =========================================================
# MOTOR DE CÁLCULO + DESGLOSE + COMPRAS
# =========================================================
res_final = []
desc_full = {}
compras_legible = {}
resumen_costes_export = {}

if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
    tot_pv_trq = sum(float(pz.get("pv_troquel", 0.0)) for pz in st.session_state.piezas_dict.values())

    for q_n in lista_cants:
        # Mermas:
        # - Offset/general: mermas_imp_manual
        # - Digital: mermas_imp_digital_manual (fallback a regla digital si no existe)
        merma_imp_offset_hojas = int(st.session_state.mermas_imp_manual.get(q_n, 0))
        merma_imp_digital_hojas = int(
            st.session_state.mermas_imp_digital_manual.get(
                q_n, calcular_mermas_estandar(q_n, es_digital=True)[1]
            )
        )
        merma_proc_hojas = int(st.session_state.mermas_proc_manual.get(q_n, 0))

        coste_f = 0.0
        det_f = []
        debug_log = []

        tot_cat = {
            "materiales": {
                "cartoncillo": 0.0,
                "ondulado": 0.0,
                "rigidos": 0.0,
                "extras": 0.0,
                "embalajes_compra": 0.0
            },
            "procesos": {
                "contracolado": 0.0,
                "impresion": 0.0,
                "peliculado": 0.0,
                "corte": 0.0,
                "manipulacion": 0.0,
                "dificultad": 0.0,
                "externos": 0.0,
            }
        }

        # Descuentos de compra por bloque (BD)
        db_desc = st.session_state.get("db_descuentos", {}) if isinstance(st.session_state.get("db_descuentos", None), dict) else {}
        f_cart = 1.0 - (float(db_desc.get("cartoncillo", 0.0)) / 100.0)
        f_or = 1.0 - (float(db_desc.get("ondulado_rigidos", 0.0)) / 100.0)
        f_narba = 1.0 - (float(db_desc.get("narba", 0.0)) / 100.0)

        for pid, p in st.session_state.piezas_dict.items():
            c_cart_cara = c_cart_dorso = 0.0
            c_ondulado = 0.0
            c_rigido = 0.0
            c_contracolado = 0.0
            c_imp_total = 0.0
            c_pel_total = 0.0
            c_troquel_taller = 0.0
            c_plotter = 0.0

            nb = q_n * float(p.get("pliegos", 1.0))
            hp_produccion = nb + merma_proc_hojas

            im_cara = p.get("im", "No")
            im_dorso = p.get("im_d", "No")

            imprime_cara = (im_cara != "No")
            imprime_dorso = (p.get("pd", "Ninguno") != "Ninguno" and im_dorso != "No")

            # 👇 Merma de impresión depende del tipo (Offset vs Digital)
            if imprime_cara:
                merma_cara = merma_imp_digital_hojas if im_cara == "Digital" else merma_imp_offset_hojas
                hp_papel_f = hp_produccion + merma_cara
            else:
                hp_papel_f = hp_produccion

            if imprime_dorso:
                merma_d = merma_imp_digital_hojas if im_dorso == "Digital" else merma_imp_offset_hojas
                hp_papel_d = hp_produccion + merma_d
            else:
                hp_papel_d = hp_produccion

            w = float(p.get("w", 0))
            h = float(p.get("h", 0))
            m2_papel = (w * h) / 1_000_000 if (w > 0 and h > 0) else 0.0

            # Capas de cartoncillo seleccionadas (cara/dorso)
            has_cart_cara = (p.get("pf", "Ninguno") != "Ninguno")
            has_cart_dorso = (p.get("pd", "Ninguno") != "Ninguno")
            capas_cartoncillo = (1 if has_cart_cara else 0) + (1 if has_cart_dorso else 0)

            # ✅ Reglas de CONTRACOLADO:
            # - Solo se contracola si hay que pegar capas entre sí.
            # - Si hay base (plancha ondulado o rígido) + cartoncillo: 1 contracolado por cada cara con cartoncillo.
            # - Si NO hay base (solo cartoncillo):
            #     · 1 cara: NO hay contracolado
            #     · cara + dorso: 1 contracolado (pegarlos entre sí)
            has_base_ondulado = (p.get("tipo_base") == "Ondulado/Cartón" and p.get("pl", "Ninguna") != "Ninguna")
            has_base_rigido = (p.get("tipo_base") == "Material Rígido" and (
                bool(p.get("rig_manual", False)) or p.get("mat_rigido", "Ninguno") != "Ninguno"
            ))
            has_base = (has_base_ondulado or has_base_rigido)

            if has_base:
                capas_contracolado = (1 if has_cart_cara else 0) + (1 if has_cart_dorso else 0)
            else:
                capas_contracolado = 1 if (has_cart_cara and has_cart_dorso) else 0

            if p.get("tipo_base") == "Material Rígido":
                if bool(p.get("rig_manual", False)):
                    mw, mh = float(p.get("rig_w", 0)), float(p.get("rig_h", 0))
                    precio_hoja = float(p.get("rig_precio_ud", 0.0))
                else:
                    if p.get("mat_rigido") != "Ninguno":
                        info = db["rigidos"][p["mat_rigido"]]
                        mw, mh = float(info["w"]), float(info["h"])
                        precio_hoja = float(info["precio_ud"]) * f_or
                    else:
                        mw = mh = precio_hoja = 0.0

                if w > 0 and h > 0 and mw > 0 and mh > 0:
                    y1 = int(mw // w) * int(mh // h)
                    y2 = int(mw // h) * int(mh // w)
                    by = max(y1, y2)
                else:
                    by = 0

                if by > 0:
                    n_net = math.ceil(hp_produccion / by)
                    if capas_contracolado == 0:
                        n_pl = n_net + merma_rigido_fija(n_net)
                    else:
                        n_pl = math.ceil(n_net * 1.02)
                    c_rigido = n_pl * precio_hoja

                    debug_log.append({
                        "qty": q_n,
                        "pieza": p.get("nombre",""),
                        "tipo": "rigido",
                        "by": by,
                        "hojas_netas": n_net,
                        "hojas_total": n_pl,
                        "precio_hoja": precio_hoja,
                        "coste": c_rigido,
                        "merma_regla": "fija" if capas_contracolado == 0 else "2%"
                    })
            else:
                if p.get("pl", "Ninguna") != "Ninguna":
                    if bool(p.get("pl_dif", False)) and float(p.get("pl_h", 0)) > 0 and float(p.get("pl_w", 0)) > 0:
                        m2_plancha = (float(p["pl_w"]) * float(p["pl_h"])) / 1_000_000
                    else:
                        m2_plancha = m2_papel
                    c_ondulado = hp_produccion * m2_plancha * float(db["planchas"][p["pl"]][p.get("ap","B/C")]) * f_or

            if p.get("pf", "Ninguno") != "Ninguno" and m2_papel > 0:
                c_cart_cara = hp_papel_f * m2_papel * (float(p.get("gf", 0))/1000.0) * float(db["cartoncillo"][p["pf"]]["precio_kg"]) * f_cart
            if p.get("pd", "Ninguno") != "Ninguno" and m2_papel > 0:
                c_cart_dorso = hp_papel_d * m2_papel * (float(p.get("gd", 0))/1000.0) * float(db["cartoncillo"][p["pd"]]["precio_kg"]) * f_cart

            peg_rate = float(db["planchas"]["Microcanal / Canal 3"]["peg"]) * f_narba
            if capas_contracolado > 0 and m2_papel > 0:
                c_contracolado = hp_produccion * m2_papel * peg_rate * capas_contracolado

            c_imp_cara = 0.0
            c_imp_dorso = 0.0

            if p.get("im","No") == "Digital":
                c_imp_cara = hp_papel_f * m2_papel * 6.5
                if bool(p.get("ld", False)):
                    c_pel_total += hp_produccion * m2_papel * float(db.get("laminado_digital", 3.5))
            elif p.get("im","No") == "Offset":
                tintas_cara = int(p.get("nt",0)) + (1 if bool(p.get("ba",False)) else 0)
                c_imp_cara = coste_offset_por_tinta(int(round(nb))) * tintas_cara

            if p.get("im_d","No") == "Digital":
                c_imp_dorso = hp_papel_d * m2_papel * 6.5
                if bool(p.get("ld_d", False)):
                    c_pel_total += hp_produccion * m2_papel * float(db.get("laminado_digital", 3.5))
            elif p.get("im_d","No") == "Offset":
                tintas_dorso = int(p.get("nt_d",0)) + (1 if bool(p.get("ba_d",False)) else 0)
                c_imp_dorso = coste_offset_por_tinta(int(round(nb))) * tintas_dorso

            c_imp_total = c_imp_cara + c_imp_dorso

            c_pel_cara = 0.0
            c_pel_dorso = 0.0
            if p.get("pel","Sin Peliculado") != "Sin Peliculado":
                c_pel_cara = hp_produccion * m2_papel * float(db["peliculado"][p["pel"]]) * f_narba
            if p.get("pd","Ninguno") != "Ninguno" and p.get("pel_d","Sin Peliculado") != "Sin Peliculado":
                c_pel_dorso = hp_produccion * m2_papel * float(db["peliculado"][p["pel_d"]]) * f_narba
            c_pel_total += (c_pel_cara + c_pel_dorso)

            cor_sel = p.get("cor_default", "Troquelado")
            if isinstance(p.get("cor_by_qty", {}), dict):
                cor_sel = p["cor_by_qty"].get(str(q_n), cor_sel)

            cat = "Grande (> 1000x700)" if (h>1000 or w>700) else ("Pequeño (< 1000x700)" if (h<1000 and w<700) else "Mediano (Estándar)")
            if cor_sel == "Troquelado":
                arr = float(db["troquelado"][cat]["arranque"]) * f_narba if bool(p.get("cobrar_arreglo", True)) else 0.0
                tiro = float(db["troquelado"][cat]["tiro"]) * f_narba
                c_troquel_taller = arr + (hp_produccion * tiro)
            else:
                c_plotter = hp_produccion * float(db["plotter"]["precio_hoja"])

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
                "Subtotal Pieza": sub,
                "Corte Seleccionado": cor_sel
            })

            tot_cat["materiales"]["cartoncillo"] += (c_cart_cara + c_cart_dorso)
            tot_cat["materiales"]["ondulado"] += c_ondulado
            tot_cat["materiales"]["rigidos"] += c_rigido
            tot_cat["procesos"]["contracolado"] += c_contracolado
            tot_cat["procesos"]["impresion"] += c_imp_total
            tot_cat["procesos"]["peliculado"] += c_pel_total
            tot_cat["procesos"]["corte"] += (c_troquel_taller + c_plotter)

        c_ext = sum(float(e.get("coste",0.0)) * float(e.get("cantidad",1.0)) * q_n for e in st.session_state.lista_extras_grabados)
        tot_cat["materiales"]["extras"] += c_ext

        c_mo_man = (seg_man_total/3600.0)*18.0*q_n
        c_mo_dif = (q_n * float(dif_ud))
        c_mo = c_mo_man + c_mo_dif
        tot_cat["procesos"]["manipulacion"] += c_mo_man
        tot_cat["procesos"]["dificultad"] += c_mo_dif

        emb_compra_total = 0.0
        emb_det = []
        for emb in st.session_state.embalajes:
            cu = float(emb.get("costes", {}).get(q_n, 0.0))
            emb_compra_total += cu * q_n
            emb_det.append({"nombre": emb.get("nombre",""), "tipo": emb.get("tipo",""), "material": emb.get("material",""), "coste_unit_compra": cu})
        tot_cat["materiales"]["embalajes_compra"] += emb_compra_total

        ext_total = 0.0
        ext_det = []
        for ext in st.session_state.externos:
            val = float(ext.get("costes", {}).get(q_n, 0.0))
            if ext.get("modo", "Unitario (€/ud)") == "Unitario (€/ud)":
                coste = val * q_n
                tipo = "unitario"
            else:
                coste = val
                tipo = "total"
            ext_total += coste
            ext_det.append({"concepto": ext.get("concepto",""), "modo": ext.get("modo",""), "tipo_aplicado": tipo, "valor_input": val, "coste_total": coste})
        tot_cat["procesos"]["externos"] += ext_total

        pv_emb_total = (emb_compra_total * margen_embalajes)

        # Venta producido (excluye extras, embalajes y troquel)
        materiales_cost = float(
            tot_cat["materiales"]["cartoncillo"]
            + tot_cat["materiales"]["ondulado"]
            + tot_cat["materiales"]["rigidos"]
        )

        # Procesos incluye "externos" en el desglose de costes, pero comercialmente los queremos tratar como "Extras".
        procesos_cost_total = float(sum(tot_cat["procesos"].values()))  # incluye externos, manipulación y dificultad
        procesos_cost_sin_externos = float(procesos_cost_total - ext_total)

        pv_materiales_total = materiales_cost * margen
        pv_procesos_total = (procesos_cost_sin_externos * margen) + imp_fijo_pvp

        # ✅ Descuento SOLO sobre procesos (no afecta extras, embalajes ni troqueles).
        # Al mover "externos" a extras, tampoco se les aplica este descuento.
        pv_procesos_total = pv_procesos_total * (1.0 - (descuento_procesos / 100.0))

        pv_producido_total = pv_materiales_total + pv_procesos_total
        pv_material_unit = pv_producido_total / q_n

        # Extras comerciales = extras grabados + procesos externos
        pv_extras_total = ((c_ext + ext_total) * margen_extras)
        pv_extras_unit = pv_extras_total / q_n if q_n > 0 else 0.0

        tot_pv_trq = sum(float(pz.get("pv_troquel", 0.0)) for pz in st.session_state.piezas_dict.values())

        pvp_total_todo = pv_producido_total + pv_extras_total + pv_emb_total + tot_pv_trq
        unit_todo = pvp_total_todo / q_n

        # Unitario sin troquel: producido + embalaje + extras
        pvp_prod_emb_extras = pv_producido_total + pv_emb_total + pv_extras_total
        unit_prod_emb_extras = pvp_prod_emb_extras / q_n if q_n > 0 else 0.0

        res_final.append({
            "Cantidad": q_n,
            "Precio venta material (unitario)": f"{pv_material_unit:.3f}€",
            "Precio venta extras (unitario)": f"{pv_extras_unit:.3f}€",
            "Precio venta embalaje (unitario)": f"{(pv_emb_total/q_n):.3f}€",
            "Precio venta troquel (TOTAL)": f"{tot_pv_trq:.2f}€",
            "Precio venta unitario (prod+emb+extras)": f"{unit_prod_emb_extras:.3f}€",
            "Precio venta unitario (todo)": f"{unit_todo:.3f}€",
            "Precio venta total": f"{pvp_total_todo:.2f}€"
        })

        desc_full[q_n] = {
            "det_piezas": det_f,
            "embalajes": emb_det,
            "externos": ext_det,
            "mermas": {"impresion_offset_hojas": merma_imp_offset_hojas, "impresion_digital_hojas": merma_imp_digital_hojas, "proceso_hojas": merma_proc_hojas},
            "debug": debug_log
        }

        compras_legible[q_n] = {
            "Cantidad": q_n,
            "Materiales": tot_cat["materiales"],
            "Procesos": tot_cat["procesos"],
            "Detalle piezas": det_f,
            "Detalle embalajes": emb_det,
            "Detalle externos": ext_det,
            "Extras (detalle)": st.session_state.lista_extras_grabados
        }

        resumen_costes_export[q_n] = {
            "Cantidad": q_n,
            "materiales": {k: round(v, 4) for k, v in tot_cat["materiales"].items()},
            "procesos": {k: round(v, 4) for k, v in tot_cat["procesos"].items()},
            "totales": {
                "materiales_total": round(sum(tot_cat["materiales"].values()), 4),
                "procesos_total": round(sum(tot_cat["procesos"].values()), 4),
                "coste_total_compra_estimado": round(sum(tot_cat["materiales"].values()) + sum(tot_cat["procesos"].values()), 4)
            }
        }

safe_brf = re.sub(r'[\\/*?:"<>|]', "", st.session_state.brf or "Ref").replace(" ", "_")
safe_cli = re.sub(r'[\\/*?:"<>|]', "", st.session_state.cli or "Cli").replace(" ", "_")
st.session_state._export_filename = f"{safe_brf}_{safe_cli}.json"

export_data = construir_export(
    resumen_compra=compras_legible if compras_legible else None,
    resumen_costes=resumen_costes_export if resumen_costes_export else None
)
st.session_state._export_blob = json.dumps(export_data, indent=4, ensure_ascii=False)

# =========================================================
# SALIDAS
# =========================================================
def build_comercial_html(res_final_rows, desc_html, extras_html, emb_html, ext_html, tabla_html):
    return f"""
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Oferta - {st.session_state.cli or 'CLIENTE'}</title>
{CSS_COMERCIAL}
</head>
<body>
<div class='comercial-box'>
  <div class='comercial-header'>OFERTA COMERCIAL - {st.session_state.cli or 'CLIENTE'}</div>
  <div class='comercial-ref'>Ref. Briefing: {st.session_state.brf or '-'}</div>
  {desc_html}
  {extras_html}
  {emb_html}
  {ext_html}
  {tabla_html}
</div>
</body>
</html>
"""

if modo_comercial and res_final:
    manip_unit_txt = f"{t_input:g} {('min' if unidad_t=='Minutos' else 'seg')}/ud"
    manip_seg_txt = f"{seg_man_total:g} seg/ud"

    desc_html = "<div class='sec-title'>📋 Especificaciones del Proyecto</div>"
    desc_html += "<div class='card'>"
    desc_html += (
        "<div style='margin-bottom:10px;'>"
        "<span class='tag'>Manipulación</span>"
        f"<span class='small muted'><b>Tiempo/ud:</b> {manip_unit_txt} &nbsp;|&nbsp; <b>Equivalente:</b> {manip_seg_txt}</span>"
        "</div>"
    )

    for p in st.session_state.piezas_dict.values():
        base_info = ""
        if p.get("tipo_base") == "Material Rígido":
            if bool(p.get("rig_manual", False)):
                base_info = f"Rígido Manual: {int(p.get('rig_w',0))}×{int(p.get('rig_h',0))} mm | {float(p.get('rig_precio_ud',0.0)):.2f}€/hoja"
            else:
                base_info = f"Rígido: {p.get('mat_rigido','')}"
        else:
            base_info = f"Ondulado: {p.get('pl','')} ({p.get('ap','')})"

        cara = f"{p.get('pf','')} ({p.get('gf',0)}g)"
        dorso = f"{p.get('pd','')} ({p.get('gd',0)}g)"
        imp_c = f"{p.get('im','No')}"
        imp_d = f"{p.get('im_d','No')}"
        pel_c = f"{p.get('pel','Sin Peliculado')}"
        pel_d = f"{p.get('pel_d','Sin Peliculado')}"

        tintas_c = ""
        if p.get("im","No") == "Offset":
            tintas_c = f" | <b>Tintas:</b> {int(p.get('nt',0))}" + (" + Barniz" if bool(p.get("ba",False)) else "")
        elif p.get("im","No") == "Digital":
            tintas_c = " | <b>Laminado:</b> " + ("Sí" if bool(p.get("ld",False)) else "No")

        tintas_d = ""
        if p.get("im_d","No") == "Offset":
            tintas_d = f" | <b>Tintas:</b> {int(p.get('nt_d',0))}" + (" + Barniz" if bool(p.get("ba_d",False)) else "")
        elif p.get("im_d","No") == "Digital":
            tintas_d = " | <b>Laminado:</b> " + ("Sí" if bool(p.get("ld_d",False)) else "No")

        corte = p.get("cor_default","Troquelado")
        trq = f"{float(p.get('pv_troquel',0.0)):.2f}€"

        desc_html += (
            "<div style='margin-bottom:8px;'>"
            f"<span class='tag'>{p.get('nombre','')}</span>"
            f"<span class='small muted'>{int(p.get('h',0))}×{int(p.get('w',0))} mm | Pliegos/ud: {float(p.get('pliegos',1.0)):.4f}</span>"
            "<div class='small'>"
            f"<b>Soporte:</b> {base_info}<br>"
            f"<b>Cara:</b> {cara} | <b>Imp:</b> {imp_c}{tintas_c} | <b>Pel:</b> {pel_c}<br>"
            f"<b>Dorso:</b> {dorso} | <b>Imp:</b> {imp_d}{tintas_d} | <b>Pel:</b> {pel_d}<br>"
            f"<b>Corte (def):</b> {corte} | <b>Troquel (venta):</b> {trq}"
            "</div></div>"
        )
    desc_html += "</div>"

    extras_html = "<div class='sec-title'>➕ Materiales extra</div><div class='card'>"
    if st.session_state.lista_extras_grabados:
        for e in st.session_state.lista_extras_grabados:
            extras_html += f"<div class='small'>• <b>{e.get('nombre','')}</b> — {float(e.get('cantidad',1.0))} /ud — {float(e.get('coste',0.0)):.4f}€ compra</div>"
    else:
        extras_html += "<div class='small muted'>Sin extras.</div>"
    extras_html += "</div>"

    emb_html = "<div class='sec-title'>📦 Embalajes</div><div class='card'>"
    for emb in st.session_state.embalajes:
        L, W, H = emb["dims"].get("L",0), emb["dims"].get("W",0), emb["dims"].get("H",0)
        emb_html += f"<div class='small'>• <b>{emb.get('nombre','')}</b> — {emb.get('tipo','')} — {emb.get('material','')} — {L:.0f}×{W:.0f}×{H:.0f} mm</div>"
    emb_html += "</div>"

    ext_html = "<div class='sec-title'>📌 Externos</div><div class='card'>"
    if st.session_state.externos:
        for ext in st.session_state.externos:
            ext_html += f"<div class='small'>• <b>{ext.get('concepto','')}</b> — {ext.get('modo','')}</div>"
    else:
        ext_html += "<div class='small muted'>Sin externos.</div>"
    ext_html += "</div>"

    rows_list = []
    for r in res_final:
        rows_list.append(
            "<tr>"
            f"<td><b>{r['Cantidad']}</b></td>"
            f"<td>{r['Precio venta material (unitario)']}</td>"
            f"<td>{r.get('Precio venta extras (unitario)', '0.000€')}</td>"
            f"<td>{r['Precio venta embalaje (unitario)']}</td>"
            f"<td>{r['Precio venta troquel (TOTAL)']}</td>"
            f"<td>{r.get('Precio venta unitario (prod+emb+extras)', '0.000€')}</td>"
            f"<td><b style='color:#1E88E5;'>{r['Precio venta unitario (todo)']}</b></td>"
            f"<td>{r['Precio venta total']}</td>"
            "</tr>"
        )
    rows = "".join(rows_list)

    tabla = (
        "<div class='sec-title'>€ Precios de venta</div>"
        "<table class='comercial-table'>"
        "<tr>"
        "<th>Cantidad</th>"
        "<th>Venta material (unit)</th>"
        "<th>Venta extras+externos (unit)</th>"
        "<th>Venta embalaje (unit)</th>"
        "<th>Troquel (TOTAL)</th>"
        "<th>Unitario (prod+emb+extras)</th>"
        "<th>UNITARIO (TODO)</th>"
        "<th>VENTA TOTAL</th>"
        "</tr>"
        f"{rows}"
        "</table>"
        "<div class='small muted' style='margin-top:10px;'>"
        "* &quot;Venta material&quot; incluye el producido (materiales + procesos internos) excluyendo extras, procesos externos, embalajes y troqueles. &quot;Extras+externos&quot; incluye extras grabados y procesos externos. IVA no incluido."
        "</div>"
    )

    oferta_html = build_comercial_html(res_final, desc_html, extras_html, emb_html, ext_html, tabla)
    safe_desc = re.sub(r'[\\/*?:"<>|]', "", st.session_state.desc or "Oferta").replace(" ", "_")
    fname_html = f"OFERTA_{safe_brf}_{safe_cli}_{safe_desc}.html"

    st.download_button(
        "⬇️ Descargar VISTA OFERTA (HTML)",
        data=oferta_html.encode("utf-8"),
        file_name=fname_html,
        mime="text/html",
        use_container_width=True
    )

    st.markdown(
        "<div class='comercial-box'>"
        f"<div class='comercial-header'>OFERTA COMERCIAL - {st.session_state.cli or 'CLIENTE'}</div>"
        f"<div class='comercial-ref'>Ref. Briefing: {st.session_state.brf or '-'}</div>"
        f"{desc_html}{extras_html}{emb_html}{ext_html}{tabla}"
        "</div>",
        unsafe_allow_html=True
    )
else:
    if res_final:
        st.header(f"📊 Resumen de Venta: {st.session_state.cli}")
        df = pd.DataFrame(res_final)[[
            "Cantidad",
            "Precio venta material (unitario)",
            "Precio venta extras (unitario)",
            "Precio venta embalaje (unitario)",
            "Precio venta troquel (TOTAL)",
            "Precio venta unitario (prod+emb+extras)",
            "Precio venta unitario (todo)",
            "Precio venta total"
        ]]
        st.dataframe(df, use_container_width=True)

# =========================================================
# TAB DEBUG (SIEMPRE)
# =========================================================
with tab_debug:
    lista_cants_dbg = parse_cantidades(st.session_state.cants_str_saved)

    if lista_cants_dbg and desc_full:
        sq = st.selectbox("Ver detalle por cantidad:", lista_cants_dbg, key="dbg_sel")

        st.subheader("Desglose por pieza")
        det = desc_full.get(sq, {}).get("det_piezas", [])
        if det:
            st.dataframe(pd.DataFrame(det), use_container_width=True)
        else:
            st.info("No hay detalle de piezas para esta cantidad.")

        st.subheader("Resumen compras (materiales y procesos)")
        comp = compras_legible.get(sq, {})
        if comp:
            materiales = comp.get("Materiales", {}) or {}
            procesos = comp.get("Procesos", {}) or {}

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Materiales (compra estimada)**")
                st.dataframe(pd.DataFrame([materiales]), use_container_width=True)
            with c2:
                st.markdown("**Procesos (coste estimado)**")
                st.dataframe(pd.DataFrame([procesos]), use_container_width=True)

            total_materiales = sum(float(v or 0.0) for v in materiales.values())
            total_procesos = sum(float(v or 0.0) for v in procesos.values())
            total_compra = total_materiales + total_procesos

            st.metric("TOTAL COSTE (compra) · Materiales + Procesos", f"{total_compra:,.2f}€")

        st.subheader("Externos (detalle)")
        exd = desc_full.get(sq, {}).get("externos", [])
        if exd:
            st.dataframe(pd.DataFrame(exd), use_container_width=True)
        else:
            st.caption("Sin externos para esta cantidad.")

        st.subheader("Debug log (técnico)")
        dbg = desc_full.get(sq, {}).get("debug", [])
        if dbg:
            st.dataframe(pd.DataFrame(dbg), use_container_width=True)
        else:
            st.caption("Sin entradas debug (solo se rellenan algunas líneas, p.ej. rígidos).")
    else:
        st.info("No hay desglose aún. Define cantidades y calcula.")
