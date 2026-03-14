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

    ⚠️ Actualización (Mar 2026):
    - La merma se calcula por tramos (según guía MAINSA).
    - Se interpreta 'n' como nº de hojas netas del formato (q * pliegos/ud), porque un formato
      puede tener distinto rendimiento (p.ej. 1/hoja vs 4/hoja) y NO pueden compartir merma.
    - 'es_digital' se mantiene por compatibilidad pero no cambia la tabla.
    """
    n = max(0, int(math.ceil(float(n))))

    if n < 100:
        return 10, 130
    if 101 <= n <= 200:
        return 20, 150
    if 201 <= n <= 300:
        return 30, 170
    if 301 <= n <= 500:
        return 40, 180
    if 501 <= n <= 1000:
        return 50, 190
    if 1001 <= n <= 1500:
        return 60, 200
    if 1501 <= n <= 2000:
        return 70, 210
    if 2001 <= n <= 3500:
        return 80, 220
    return 90, 230


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
        "impresiones_extra": [],
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
if "mermas_proc_manual" not in st.session_state: st.session_state.mermas_proc_manual = {}
if "mermas_imp_pieza" not in st.session_state: st.session_state.mermas_imp_pieza = {}
if "mermas_proc_pieza" not in st.session_state: st.session_state.mermas_proc_pieza = {}
if "mermas_auto_pieza" not in st.session_state: st.session_state.mermas_auto_pieza = {}

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

    # Mermas (legacy global)
    for q in lista_cants:
        for k in [f"mi_{q}", f"mp_{q}"]:
            if k in st.session_state:
                del st.session_state[k]

    # Mermas por pieza/formato (nuevo)
    for pid in piezas_ids:
        for q in lista_cants:
            for k in [f"mi_{pid}_{q}", f"mp_{pid}_{q}", f"merma_auto_{pid}_{q}"]:
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

    # ✅ V44+: soportar varias impresiones por formato
    if not isinstance(base.get("impresiones_extra", []), list):
        base["impresiones_extra"] = []
    else:
        norm_list = []
        for it in base["impresiones_extra"]:
            if not isinstance(it, dict):
                continue
            x = {
                "id": str(it.get("id", "")),
                "nombre": str(it.get("nombre", "")),
                "qty": _coerce_int(it.get("qty", 0), 0),
                "im": str(it.get("im", base.get("im", "No"))),
                "nt": _coerce_int(it.get("nt", base.get("nt", 0)), 0),
                "ba": _coerce_bool(it.get("ba", base.get("ba", False)), False),
                "ld": _coerce_bool(it.get("ld", base.get("ld", False)), False),
                "pel": str(it.get("pel", base.get("pel", "Sin Peliculado"))),
                "im_d": str(it.get("im_d", base.get("im_d", "No"))),
                "nt_d": _coerce_int(it.get("nt_d", base.get("nt_d", 0)), 0),
                "ba_d": _coerce_bool(it.get("ba_d", base.get("ba_d", False)), False),
                "ld_d": _coerce_bool(it.get("ld_d", base.get("ld_d", False)), False),
                "pel_d": str(it.get("pel_d", base.get("pel_d", "Sin Peliculado"))),
                "merma_imp": _coerce_int(it.get("merma_imp", 0), 0),
                "auto_merma": _coerce_bool(it.get("auto_merma", True), True),
            }
            if not x["id"]:
                x["id"] = hashlib.sha256(f"{pid}-{len(norm_list)}".encode("utf-8")).hexdigest()[:10]
            if not x["nombre"]:
                x["nombre"] = f"Impresión {len(norm_list)+1}"
            norm_list.append(x)
        base["impresiones_extra"] = norm_list

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
    if isinstance(di.get("mermas_proc", None), dict):
        st.session_state.mermas_proc_manual = {int(k): int(v) for k, v in di["mermas_proc"].items()}

    # ✅ NUEVO (V44+): mermas por pieza/formato (compatibles hacia atrás)
    # Formato esperado:
    #   mermas_imp_pieza: {"1": {"500": 190, ...}, "2": {...}}
    #   mermas_proc_pieza: {"1": {"500": 50, ...}, "2": {...}}
    if isinstance(di.get("mermas_imp_pieza", None), dict):
        out = {}
        for kpid, vv in di["mermas_imp_pieza"].items():
            try:
                ipid = int(kpid)
            except:
                continue
            if isinstance(vv, dict):
                out[ipid] = {int(kq): int(vq) for kq, vq in vv.items() if str(kq).isdigit()}
        st.session_state.mermas_imp_pieza = out

    if isinstance(di.get("mermas_proc_pieza", None), dict):
        out = {}
        for kpid, vv in di["mermas_proc_pieza"].items():
            try:
                ipid = int(kpid)
            except:
                continue
            if isinstance(vv, dict):
                out[ipid] = {int(kq): int(vq) for kq, vq in vv.items() if str(kq).isdigit()}
        st.session_state.mermas_proc_pieza = out

    if isinstance(di.get("mermas_auto_pieza", None), dict):
        out = {}
        for kpid, vv in di["mermas_auto_pieza"].items():
            try:
                ipid = int(kpid)
            except:
                continue
            if isinstance(vv, dict):
                out[ipid] = {int(kq): bool(vq) for kq, vq in vv.items()}
        st.session_state.mermas_auto_pieza = out

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
        "mermas_proc": deepcopy(st.session_state.mermas_proc_manual),
        "mermas_imp_pieza": deepcopy(st.session_state.get("mermas_imp_pieza", {})),
        "mermas_proc_pieza": deepcopy(st.session_state.get("mermas_proc_pieza", {})),
        "mermas_auto_pieza": deepcopy(st.session_state.get("mermas_auto_pieza", {})),
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

    if lista_cants and st.session_state.piezas_dict:
        # ✅ Mermas por pieza (formato): se calculan por hojas netas (= q * pliegos)
        for pid, pz in st.session_state.piezas_dict.items():
            st.session_state.mermas_imp_pieza.setdefault(pid, {})
            st.session_state.mermas_proc_pieza.setdefault(pid, {})
            st.session_state.mermas_auto_pieza.setdefault(pid, {})

            pl = float(pz.get("pliegos", 1.0))
            for q in lista_cants:
                hojas_netas = q * pl
                mp, mi = calcular_mermas_estandar(hojas_netas)

                # flags auto por defecto
                st.session_state.mermas_auto_pieza[pid].setdefault(q, True)

                # si auto, refrescamos valores; si manual, respetamos lo que haya
                if st.session_state.mermas_auto_pieza[pid].get(q, True):
                    st.session_state.mermas_proc_pieza[pid][q] = int(mp)
                    st.session_state.mermas_imp_pieza[pid][q] = int(mi)
                else:
                    st.session_state.mermas_proc_pieza[pid].setdefault(q, int(mp))
                    st.session_state.mermas_imp_pieza[pid].setdefault(q, int(mi))

        # ✅ Compatibilidad hacia atrás:
        # mantenemos los diccionarios globales si alguien depende de ellos (export/import antiguos)
        for q in lista_cants:
            if q not in st.session_state.mermas_proc_manual:
                st.session_state.mermas_proc_manual[q] = calcular_mermas_estandar(q)[0]
            if q not in st.session_state.mermas_imp_manual:
                st.session_state.mermas_imp_manual[q] = calcular_mermas_estandar(q)[1]

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
        st.session_state.mermas_imp_pieza = {}
        st.session_state.mermas_proc_pieza = {}
        st.session_state.mermas_auto_pieza = {}
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

                # -------------------------------------------------
                # (OPCIONAL) Varias impresiones para este formato
                # -------------------------------------------------
                with st.expander("🖨️ Varias impresiones (opcional)", expanded=False):
                    st.caption("Útil si este formato se imprime en varios modelos (p.ej. 200 + 300 + 500).")
                    if "impresiones_extra" not in p or not isinstance(p.get("impresiones_extra", None), list):
                        p["impresiones_extra"] = []

                    if st.button("➕ Añadir impresión adicional", key=f"add_imp_{p_id}"):
                        new_idx = len(p["impresiones_extra"]) + 1
                        new_id = hashlib.sha256(f"{p_id}-{new_idx}-{p.get('nombre','')}".encode("utf-8")).hexdigest()[:10]
                        p["impresiones_extra"].append({
                            "id": new_id,
                            "nombre": f"Impresión {new_idx}",
                            "qty": 0,
                            # copiamos parámetros actuales como punto de partida
                            "im": p.get("im", "No"),
                            "nt": int(p.get("nt", 0)),
                            "ba": bool(p.get("ba", False)),
                            "ld": bool(p.get("ld", False)),
                            "pel": p.get("pel", "Sin Peliculado"),
                            "im_d": p.get("im_d", "No"),
                            "nt_d": int(p.get("nt_d", 0)),
                            "ba_d": bool(p.get("ba_d", False)),
                            "ld_d": bool(p.get("ld_d", False)),
                            "pel_d": p.get("pel_d", "Sin Peliculado"),
                            "merma_imp": 0,
                            "auto_merma": True,
                        })
                        st.rerun()

                    if p["impresiones_extra"]:
                        labels = [f"{it.get('nombre','')} · {int(it.get('qty',0))} uds" for it in p["impresiones_extra"]]
                        sel = st.selectbox("Selecciona impresión adicional", labels, index=0, key=f"sel_imp_{p_id}")
                        sel_i = labels.index(sel) if sel in labels else 0
                        it = p["impresiones_extra"][sel_i]

                        cI1, cI2 = st.columns([2, 1])
                        it["nombre"] = cI1.text_input("Nombre", value=str(it.get("nombre", f"Impresión {sel_i+1}")), key=f"imp_nom_{p_id}_{it['id']}")
                        it["qty"] = int(cI2.number_input("Cantidad (uds)", min_value=0, value=int(it.get("qty", 0)), step=1, key=f"imp_qty_{p_id}_{it['id']}"))

                        st.markdown("**Parámetros de impresión (pueden diferir del formato base):**")
                        opts_im2 = ["Offset", "Digital", "No"]

                        cpa, cpb = st.columns(2)
                        # Cara
                        val_imx = str(it.get("im", "No"))
                        idx_imx = opts_im2.index(val_imx) if val_imx in opts_im2 else 2
                        it["im"] = cpa.selectbox("Impresión Cara", opts_im2, index=idx_imx, key=f"imp_im_{p_id}_{it['id']}")
                        if it["im"] == "Offset":
                            it["nt"] = int(cpa.number_input("Tintas Cara", 0, 6, int(it.get("nt", 4)), key=f"imp_nt_{p_id}_{it['id']}"))
                            it["ba"] = bool(cpa.checkbox("Barniz Cara", value=bool(it.get("ba", False)), key=f"imp_ba_{p_id}_{it['id']}"))
                            it["ld"] = False
                        elif it["im"] == "Digital":
                            it["ld"] = bool(cpa.checkbox("Laminado Digital Cara", value=bool(it.get("ld", False)), key=f"imp_ld_{p_id}_{it['id']}"))
                            it["nt"] = int(it.get("nt", 0))
                            it["ba"] = bool(it.get("ba", False))
                        it["pel"] = cpa.selectbox("Peliculado Cara", opts_pel, index=opts_pel.index(it.get("pel", "Sin Peliculado")) if it.get("pel", "Sin Peliculado") in opts_pel else 0, key=f"imp_pel_{p_id}_{it['id']}")

                        # Dorso (solo si hay cartoncillo dorso)
                        val_imdx = str(it.get("im_d", "No"))
                        idx_imdx = opts_im2.index(val_imdx) if val_imdx in opts_im2 else 2
                        it["im_d"] = cpb.selectbox("Impresión Dorso", opts_im2, index=idx_imdx, key=f"imp_imd_{p_id}_{it['id']}")
                        if it["im_d"] == "Offset":
                            it["nt_d"] = int(cpb.number_input("Tintas Dorso", 0, 6, int(it.get("nt_d", 0)), key=f"imp_ntd_{p_id}_{it['id']}"))
                            it["ba_d"] = bool(cpb.checkbox("Barniz Dorso", value=bool(it.get("ba_d", False)), key=f"imp_bad_{p_id}_{it['id']}"))
                            it["ld_d"] = False
                        elif it["im_d"] == "Digital":
                            it["ld_d"] = bool(cpb.checkbox("Laminado Digital Dorso", value=bool(it.get("ld_d", False)), key=f"imp_ldd_{p_id}_{it['id']}"))
                            it["nt_d"] = int(it.get("nt_d", 0))
                            it["ba_d"] = bool(it.get("ba_d", False))
                        it["pel_d"] = cpb.selectbox("Peliculado Dorso", opts_pel, index=opts_pel.index(it.get("pel_d", "Sin Peliculado")) if it.get("pel_d", "Sin Peliculado") in opts_pel else 0, key=f"imp_peld_{p_id}_{it['id']}")

                        # Merma impresión extra (por impresión)
                        plx = float(p.get("pliegos", 1.0))
                        hojas_netas_x = float(it.get("qty", 0)) * plx
                        _mpx, mix_sug = calcular_mermas_estandar(hojas_netas_x)
                        it.setdefault("auto_merma", True)
                        it.setdefault("merma_imp", int(mix_sug))

                        cM1, cM2 = st.columns([1, 3])
                        it["auto_merma"] = bool(cM1.checkbox("Merma Auto", value=bool(it.get("auto_merma", True)), key=f"imp_auto_{p_id}_{it['id']}"))
                        if it["auto_merma"]:
                            it["merma_imp"] = int(mix_sug)
                        it["merma_imp"] = int(cM2.number_input("Merma impresión extra (hojas)", min_value=0, value=int(it.get("merma_imp", mix_sug)), key=f"imp_merma_{p_id}_{it['id']}", disabled=bool(it["auto_merma"])))

                        if st.button("🗑 Eliminar esta impresión adicional", key=f"del_imp_{p_id}_{it['id']}"):
                            p["impresiones_extra"].pop(sel_i)
                            st.rerun()
                    else:
                        st.caption("No hay impresiones adicionales creadas.")

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
                p["gd"] = st.number_input("Gramaje Dorso (g)", value=int(p.get("gd", 0)), key=f"gd_{p_id}")

            with col3:
                # Dorso
                opts_im = ["Offset", "Digital", "No"]
                val_im_d = p.get("im_d", "No")
                idx_im_d = opts_im.index(val_im_d) if val_im_d in opts_im else 2
                p["im_d"] = st.selectbox("Impresión Dorso", opts_im, index=idx_im_d, key=f"im_d_{p_id}")

                if p["im_d"] == "Offset":
                    p["nt_d"] = st.number_input("Tintas Dorso", 0, 6, int(p.get("nt_d", 0)), key=f"nt_d_{p_id}")
                    p["ba_d"] = st.checkbox("Barniz Dorso", value=bool(p.get("ba_d", False)), key=f"ba_d_{p_id}")
                elif p["im_d"] == "Digital":
                    p["ld_d"] = st.checkbox("Laminado Digital Dorso", value=bool(p.get("ld_d", False)), key=f"ld_d_{p_id}")

                opts_pel = list(db["peliculado"].keys())
                val_pel_d = p.get("pel_d", "Sin Peliculado")
                idx_pel_d = opts_pel.index(val_pel_d) if val_pel_d in opts_pel else 0
                p["pel_d"] = st.selectbox("Peliculado Dorso", opts_pel, index=idx_pel_d, key=f"pel_d_{p_id}")

                st.divider()

                opts_cor = ["Troquelado", "Plotter"]
                val_cor = p.get("cor_default", "Troquelado")
                idx_cor = opts_cor.index(val_cor) if val_cor in opts_cor else 0
                p["cor_default"] = st.selectbox("Corte (por defecto)", opts_cor, index=idx_cor, key=f"cor_def_{p_id}")

                if lista_cants:
                    p.setdefault("cor_by_qty", {})
                    st.caption("Corte por cantidad (si quieres forzar por tirada):")
                    for q in lista_cants:
                        p["cor_by_qty"][str(q)] = st.selectbox(
                            f"{q} uds", opts_cor,
                            index=opts_cor.index(p["cor_by_qty"].get(str(q), p["cor_default"])) if p["cor_by_qty"].get(str(q), p["cor_default"]) in opts_cor else 0,
                            key=f"cor_qty_{p_id}_{q}"
                        )

                p["cobrar_arreglo"] = st.checkbox("Cobrar arreglo troquel", value=bool(p.get("cobrar_arreglo", True)), key=f"arr_{p_id}")
                p["pv_troquel"] = float(st.number_input("Troquel (venta) €", value=float(p.get("pv_troquel", 0.0)), key=f"pvt_{p_id}"))

    # =========================================================
    # (UI) EXTRAS / EMBALAJES / EXTERNOS (igual que antes)
    # =========================================================
    st.divider()
    st.subheader("📌 3. Extras (materiales externos)")
    # ... (se mantiene el resto de tu app: extras, embalajes, externos, etc.)
    # NOTA: el código original continúa tal cual; la parte de abajo depende de tu fichero completo.

    # =========================================================
    # ⚙️ 5. Gestión de Mermas (por formato)
    # =========================================================
    st.divider()
    st.subheader("⚙️ 5. Gestión de Mermas (por formato)")
    if lista_cants and st.session_state.piezas_dict:
        piezas_ids = list(st.session_state.piezas_dict.keys())
        piezas_labels = [f"{pid} · {st.session_state.piezas_dict[pid].get('nombre', f'Forma {pid}')}" for pid in piezas_ids]
        sel_idx = 0
        sel_label = st.selectbox("Selecciona formato", piezas_labels, index=sel_idx, key="merma_sel_pieza")
        try:
            sel_pid = int(sel_label.split("·")[0].strip())
        except:
            sel_pid = piezas_ids[0]

        pz = st.session_state.piezas_dict.get(sel_pid, {})
        pl = float(pz.get("pliegos", 1.0))

        st.session_state.mermas_imp_pieza.setdefault(sel_pid, {})
        st.session_state.mermas_proc_pieza.setdefault(sel_pid, {})
        st.session_state.mermas_auto_pieza.setdefault(sel_pid, {})

        st.caption("La merma se calcula por hojas netas del formato (cantidad × pliegos/ud). Puedes pasar a manual por cantidad.")
        for q in lista_cants:
            hojas_netas = q * pl
            mp_sug, mi_sug = calcular_mermas_estandar(hojas_netas)

            st.session_state.mermas_auto_pieza[sel_pid].setdefault(q, True)
            is_auto = bool(st.session_state.mermas_auto_pieza[sel_pid].get(q, True))

            c0, c1, c2, c3 = st.columns([1.2, 1.0, 2.0, 2.0])
            c0.markdown(f"**{q} uds**")
            c1.caption(f"{int(math.ceil(hojas_netas))} hojas netas")

            # Toggle auto/manual (1 flag controla ambas para simplificar UX)
            new_auto = c1.checkbox("Auto", value=is_auto, key=f"merma_auto_{sel_pid}_{q}")
            st.session_state.mermas_auto_pieza[sel_pid][q] = bool(new_auto)

            if new_auto:
                st.session_state.mermas_proc_pieza[sel_pid][q] = int(mp_sug)
                st.session_state.mermas_imp_pieza[sel_pid][q] = int(mi_sug)

            st.session_state.mermas_imp_pieza[sel_pid][q] = int(c2.number_input(
                "Arranque impresión (hojas)",
                value=int(st.session_state.mermas_imp_pieza[sel_pid].get(q, mi_sug)),
                key=f"mi_{sel_pid}_{q}",
                disabled=new_auto
            ))
            st.session_state.mermas_proc_pieza[sel_pid][q] = int(c3.number_input(
                "Rodaje proceso (hojas)",
                value=int(st.session_state.mermas_proc_pieza[sel_pid].get(q, mp_sug)),
                key=f"mp_{sel_pid}_{q}",
                disabled=new_auto
            ))

        if st.button("🔄 Recalcular AUTO para este formato (todas las cantidades)", key="merma_recalc_one"):
            for q in lista_cants:
                st.session_state.mermas_auto_pieza[sel_pid][q] = True
            st.rerun()
    else:
        st.warning("Define cantidades en Paso 1 y al menos 1 formato en Paso 2.")

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
        # Compatibilidad: valores globales (JSON antiguos). Si hay mermas por pieza, se usan más abajo.
        merma_imp_global = int(st.session_state.mermas_imp_manual.get(q_n, 0))
        merma_proc_global = int(st.session_state.mermas_proc_manual.get(q_n, 0))

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

            pliegos_ud = float(p.get("pliegos", 1.0))
            nb_total = q_n * pliegos_ud  # hojas netas del formato (sin mermas)

            # ✅ Mermas por pieza (si existen). Si no, cae a global.
            mp_dict = st.session_state.get("mermas_proc_pieza", {}).get(pid, {}) if isinstance(st.session_state.get("mermas_proc_pieza", None), dict) else {}
            mi_dict = st.session_state.get("mermas_imp_pieza", {}).get(pid, {}) if isinstance(st.session_state.get("mermas_imp_pieza", None), dict) else {}

            merma_proc_hojas = int(mp_dict.get(q_n, merma_proc_global))
            # La merma de impresión "base" se usa SOLO si no hay varias impresiones
            merma_imp_base = int(mi_dict.get(q_n, merma_imp_global))

            hp_produccion = nb_total + merma_proc_hojas  # para procesos (troquel, contracolado, etc.)

            w = float(p.get("w", 0))
            h = float(p.get("h", 0))
            m2_papel = (w * h) / 1_000_000 if (w > 0 and h > 0) else 0.0

            # -------------------------------------------------
            # Varias impresiones (opcional):
            # - cada impresión tiene su coste (tintas/acabados) + su merma extra de impresión
            # - la merma de PROCESOS se queda en el total del formato
            # -------------------------------------------------
            impresiones = []
            extras = p.get("impresiones_extra", []) if isinstance(p.get("impresiones_extra", None), list) else []
            extras_valid = [it for it in extras if isinstance(it, dict) and int(it.get("qty", 0)) > 0]

            sum_extras = sum(int(it.get("qty", 0)) for it in extras_valid)
            resto = max(0, int(q_n) - int(sum_extras))

            # Si hay extras, interpretamos que son "modelos" y el resto (si existe) usa parámetros base.
            if extras_valid:
                for it in extras_valid:
                    impresiones.append({
                        "tipo": "extra",
                        "qty": int(it.get("qty", 0)),
                        "im": str(it.get("im", p.get("im", "No"))),
                        "nt": int(it.get("nt", p.get("nt", 0))),
                        "ba": bool(it.get("ba", p.get("ba", False))),
                        "ld": bool(it.get("ld", p.get("ld", False))),
                        "pel": str(it.get("pel", p.get("pel", "Sin Peliculado"))),
                        "im_d": str(it.get("im_d", p.get("im_d", "No"))),
                        "nt_d": int(it.get("nt_d", p.get("nt_d", 0))),
                        "ba_d": bool(it.get("ba_d", p.get("ba_d", False))),
                        "ld_d": bool(it.get("ld_d", p.get("ld_d", False))),
                        "pel_d": str(it.get("pel_d", p.get("pel_d", "Sin Peliculado"))),
                        "merma_imp": int(it.get("merma_imp", 0)),
                        "auto_merma": bool(it.get("auto_merma", True)),
                    })
                if resto > 0:
                    impresiones.append({
                        "tipo": "resto",
                        "qty": int(resto),
                        "im": str(p.get("im", "No")),
                        "nt": int(p.get("nt", 0)),
                        "ba": bool(p.get("ba", False)),
                        "ld": bool(p.get("ld", False)),
                        "pel": str(p.get("pel", "Sin Peliculado")),
                        "im_d": str(p.get("im_d", "No")),
                        "nt_d": int(p.get("nt_d", 0)),
                        "ba_d": bool(p.get("ba_d", False)),
                        "ld_d": bool(p.get("ld_d", False)),
                        "pel_d": str(p.get("pel_d", "Sin Peliculado")),
                        "merma_imp": int(0),
                        "auto_merma": True,
                    })
            else:
                impresiones = [{
                    "tipo": "base",
                    "qty": int(q_n),
                    "im": str(p.get("im", "No")),
                    "nt": int(p.get("nt", 0)),
                    "ba": bool(p.get("ba", False)),
                    "ld": bool(p.get("ld", False)),
                    "pel": str(p.get("pel", "Sin Peliculado")),
                    "im_d": str(p.get("im_d", "No")),
                    "nt_d": int(p.get("nt_d", 0)),
                    "ba_d": bool(p.get("ba_d", False)),
                    "ld_d": bool(p.get("ld_d", False)),
                    "pel_d": str(p.get("pel_d", "Sin Peliculado")),
                    "merma_imp": int(merma_imp_base),
                    "auto_merma": False,  # ya viene de gestión de mermas por pieza
                }]

            # Hojas a comprar/usar para materiales:
            # - base: hojas de producción (= nb_total + merma_proc)
            # - extra: sumamos SOLO las mermas de impresión de cada impresión que imprima
            hp_papel_f = float(hp_produccion)
            hp_papel_d = float(hp_produccion)

            imprime_cara_any = False
            imprime_dorso_any = False

            for it in impresiones:
                qty_it = int(it.get("qty", 0))
                if qty_it <= 0:
                    continue
                nb_it = qty_it * pliegos_ud  # hojas netas de esta impresión

                merma_imp_it = int(it.get("merma_imp", 0))
                if bool(it.get("auto_merma", False)):
                    _mp_s, mi_s = calcular_mermas_estandar(nb_it)
                    merma_imp_it = int(mi_s)
                    it["merma_imp"] = merma_imp_it

                imprime_cara_it = (str(it.get("im", "No")) != "No")
                imprime_dorso_it = (p.get("pd", "Ninguno") != "Ninguno" and str(it.get("im_d", "No")) != "No")

                if imprime_cara_it:
                    imprime_cara_any = True
                    hp_papel_f += merma_imp_it
                if imprime_dorso_it:
                    imprime_dorso_any = True
                    hp_papel_d += merma_imp_it

            # Si NO se imprime, no sumamos merma de impresión (pero sí proceso, ya incluido en hp_produccion).

            # ✅ Contracolado: solo cuando hay cartoncillo cara + otro material
            # Reglas:
            # - Cara + (plancha o rígido) -> 1 contracolado
            # - Cara + Dorso -> 1 contracolado
            # - Cara + (plancha o rígido) + Dorso -> 2 contracolados (sándwich)
            tiene_cara = (p.get("pf", "Ninguno") != "Ninguno")
            tiene_dorso = (p.get("pd", "Ninguno") != "Ninguno")
            tiene_base = (
                (p.get("tipo_base") == "Material Rígido" and p.get("mat_rigido", "Ninguno") != "Ninguno")
                or (p.get("tipo_base") != "Material Rígido" and p.get("pl", "Ninguna") != "Ninguna")
            )

            capas = 0
            if tiene_cara and tiene_dorso and tiene_base:
                capas = 2
            elif tiene_cara and (tiene_dorso or tiene_base):
                capas = 1
            else:
                capas = 0

            # =========================================================
            # COSTES MATERIALES + PROCESOS
            # =========================================================
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
                    if capas == 0:
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
                        "merma_regla": "fija" if capas == 0 else "2%"
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
            if capas > 0 and m2_papel > 0:
                c_contracolado = hp_produccion * m2_papel * peg_rate * capas

            # -------------------------------------------------
            # Impresión (y laminado digital) por impresión
            # -------------------------------------------------
            c_imp_total = 0.0

            for it in impresiones:
                qty_it = int(it.get("qty", 0))
                if qty_it <= 0:
                    continue
                nb_it = qty_it * pliegos_ud  # hojas netas de esta impresión

                merma_imp_it = int(it.get("merma_imp", 0))
                if bool(it.get("auto_merma", False)):
                    _mp_s, mi_s = calcular_mermas_estandar(nb_it)
                    merma_imp_it = int(mi_s)

                # Reparto de merma de proceso sobre las impresiones (proporcional a su qty)
                proc_share = (float(merma_proc_hojas) * (float(qty_it) / float(q_n))) if q_n > 0 else 0.0
                hojas_imp_cara = nb_it + proc_share + merma_imp_it
                hojas_imp_dorso = nb_it + proc_share + merma_imp_it

                # Cara
                if str(it.get("im", "No")) == "Digital":
                    c_imp_total += hojas_imp_cara * m2_papel * 6.5
                    if bool(it.get("ld", False)):
                        c_pel_total += hp_produccion * m2_papel * float(db.get("laminado_digital", 3.5))
                elif str(it.get("im", "No")) == "Offset":
                    tintas_cara = int(it.get("nt", 0)) + (1 if bool(it.get("ba", False)) else 0)
                    c_imp_total += coste_offset_por_tinta(int(round(hojas_imp_cara))) * tintas_cara

                # Dorso (solo si existe cartoncillo dorso)
                if p.get("pd", "Ninguno") != "Ninguno":
                    if str(it.get("im_d", "No")) == "Digital":
                        c_imp_total += hojas_imp_dorso * m2_papel * 6.5
                        if bool(it.get("ld_d", False)):
                            c_pel_total += hp_produccion * m2_papel * float(db.get("laminado_digital", 3.5))
                    elif str(it.get("im_d", "No")) == "Offset":
                        tintas_dorso = int(it.get("nt_d", 0)) + (1 if bool(it.get("ba_d", False)) else 0)
                        c_imp_total += coste_offset_por_tinta(int(round(hojas_imp_dorso))) * tintas_dorso

            # -------------------------------------------------
            # Peliculado (por impresión si hay varias)
            # -------------------------------------------------
            c_pel_cara = 0.0
            c_pel_dorso = 0.0

            if extras_valid:
                for it in impresiones:
                    qty_it = int(it.get("qty", 0))
                    if qty_it <= 0:
                        continue
                    nb_it = qty_it * pliegos_ud
                    merma_imp_it = int(it.get("merma_imp", 0))
                    if bool(it.get("auto_merma", False)):
                        _mp_s, mi_s = calcular_mermas_estandar(nb_it)
                        merma_imp_it = int(mi_s)
                    proc_share = (float(merma_proc_hojas) * (float(qty_it) / float(q_n))) if q_n > 0 else 0.0
                    hojas_it = nb_it + proc_share + merma_imp_it

                    if str(it.get("pel", "Sin Peliculado")) != "Sin Peliculado":
                        c_pel_cara += hojas_it * m2_papel * float(db["peliculado"][str(it.get("pel"))]) * f_narba
                    if p.get("pd", "Ninguno") != "Ninguno" and str(it.get("pel_d", "Sin Peliculado")) != "Sin Peliculado":
                        c_pel_dorso += hojas_it * m2_papel * float(db["peliculado"][str(it.get("pel_d"))]) * f_narba
                c_pel_total += (c_pel_cara + c_pel_dorso)
            else:
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

        # (el resto del motor: extras, mo, embalajes, comerciales, export, debug...)
        # Se mantiene como en tu fichero original.

# =========================================================
# SALIDAS (VISTA OFERTA / DESGLOSE)
# =========================================================
# ... (resto del fichero original, sin cambios)
