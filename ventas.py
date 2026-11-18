import streamlit as st
import pandas as pd
import json
import re
import html
import math
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import os
import unicodedata
from pathlib import Path
from datetime import datetime

# =========================================================
# Helpers (mínimo)
# =========================================================
def _formato_precio_venta(valor) -> str:
    """Venta a céntimos: desde medio céntimo se redondea hacia arriba.

    Se aplica solo a la salida; el motor conserva su precisión de cálculo.
    """
    importe = Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{importe:.2f}€"


MARGEN_NORMAL = 2.2
MARGEN_ESPECIAL = 2.1
COMERCIALES_MARGEN_ESPECIAL = {52, 47, 46, 62}
CLIENTES_MARGEN_ESPECIAL = {"PLANETA", "ILIDIA"}


def _parse_comercial_num(value: str):
    """Devuelve el número de comercial si es interpretable, si no None."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    m = re.search(r"(\d+)", s)
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None


def _cliente_tiene_margen_especial(cliente: str) -> bool:
    if cliente is None:
        return False
    c = str(cliente).upper()
    return any(k in c for k in CLIENTES_MARGEN_ESPECIAL)


def _margen_por_comercial(n) -> float:
    if n is None:
        return MARGEN_NORMAL
    return MARGEN_ESPECIAL if n in COMERCIALES_MARGEN_ESPECIAL else MARGEN_NORMAL


def _margen_sugerido(com1: str, com2: str, cliente: str) -> float:
    # Si el cliente es especial, manda 2.1.
    if _cliente_tiene_margen_especial(cliente):
        return MARGEN_ESPECIAL

    n1 = _parse_comercial_num(com1)
    n2 = _parse_comercial_num(com2)
    return min(_margen_por_comercial(n1), _margen_por_comercial(n2))


def _aplicar_margen_auto_si_procede() -> None:
    """Actualiza st.session_state.margen solo si el usuario no lo ha sobreescrito."""
    sugerido = float(_margen_sugerido(st.session_state.comercial_1, st.session_state.comercial_2, st.session_state.cli))
    actual = float(st.session_state.margen)
    last_auto = float(st.session_state.last_auto_margen)

    # Si el margen actual coincide con el último auto, interpretamos que el usuario no lo tocó.
    if (actual == last_auto) and (sugerido != actual):
        st.session_state.margen = sugerido
        st.session_state.last_auto_margen = sugerido
    else:
        # Aun así guardamos el sugerido para la próxima comparación.
        st.session_state.last_auto_margen = sugerido

# =========================================================
# 1) CONFIGURACIÓN
# =========================================================
st.set_page_config(page_title="MAINSA ADMIN V45", layout="wide")

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
        "Reverso Gris": {"precio_kg": 0.96, "gramaje": 220},
        "Zenith": {"precio_kg": 1.55, "gramaje": 350},
        "Reverso Madera": {"precio_kg": 0.975, "gramaje": 400},
        "Folding Kraft": {"precio_kg": 1.90, "gramaje": 340},
        "Folding Blanco": {"precio_kg": 1.82, "gramaje": 350},
    },
    "planchas": {
        "Ninguna": {"C/C": 0.0, "B/C": 0.0, "B/B": 0.0, "B/B TEST": 0.0, "peg": 0.0},
        # Tarifas de Compras 28/10/2026, importes en EUR/m2 (precio por 1.000 m2 / 1.000).
        "Canal 3 / Micro": {"Cuero/Cuero SQ": 0.768, "Blanco 1 cara SQ": 0.783, "Blanco 2 caras SQ": 0.889, "peg": 0.2353},
        "Doble Micro": {"Cuero/Cuero SQ": 1.220, "Blanco 1 cara SQ": 1.241, "Blanco 2 caras SQ": 1.488,
                        "Test blanco 2 caras": 1.441, "Kraft blanco/Kraft": 1.421, "Kraft blanco/Kraft SQ": 1.603,
                        "Estucada ET160-F095-F095-F095-BB115": 1.339, "peg": 0.2726},
        "Doble Doble": {"Cuero/Cuero SQ": 1.220, "Blanco 1 cara SQ": 1.283, "peg": 0.2726},
        "Canal 5": {"Test blanco 2 caras SQ": 1.121, "peg": 0.2353},
        "Especial - Plancha AC": {"Plancha AC": 2.922, "peg": 0.2353},
        "Especial - Micro estucada": {"ET160-M095-BB125": 1.013, "peg": 0.2353},
        # Entradas legadas conservadas EXCLUSIVAMENTE para JSON V44 anteriores.
        "Microcanal / Canal 3": {"C/C": 0.702, "B/C": 0.725, "B/B": 0.805, "B/B TEST": 1.038, "peg": 0.2353},
        "Doble Micro / Doble Doble": {"C/C": 1.128, "B/C": 1.187, "B/B": 1.378, "B/B TEST": 1.334, "peg": 0.2726},
        "AC (Cuero/Cuero)": {"C/C": 2.505, "peg": 0.2353},
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
        "Polipropileno": 0.2709,
        "Poliéster brillo": 0.53,
        "Poliéster mate": 0.79,
    },
    "laminado_digital": 3.5,
    "impresion_digital": {"precio_m2": 6.5},
    "offset": {"minimo_tinta": 85.0, "extra_101_500": 0.0875,
               "base_501_2000": 120.0, "extra_2001": 0.015},
    "mano_obra": {"manipulado_hora": 18.0, "rellenado_hora": 18.0, "armado_hora": 18.0},
    "embalajes": {
        "multiplicador_dd": 1.5,
        "guaina": {"precio_m2": 0.70, "arreglo": 30.0},
        "plano": {"arreglo": 152.0, "arreglo_m2": 20.0, "precio_ud": 0.15, "precio_m2": 1.02},
        "volumen": {"arreglo": 20.0, "arreglo_m2": 8.0, "precio_m2": 0.64},
        "aros": {"precio_ud": 0.120838225, "precio_m2": 0.469363762,
                 "arreglo": 1600.52632, "exponente": 1.48},
    },
    "flexico": {k: float(v["precio"]) for k, v in PRODUCTOS_FLEXICO.items()},
    "extras_base": {
        "CINTA D/CARA": 0.26, "CINTA LOHMAN": 0.49, "CINTA GEL": 1.2,
        "GOMA TERMINALES": 0.079, "IMAN 20x2mm": 1.145, "TUBOS": 1.06,
        "REMACHES": 0.049, "VELCRO": 0.43, "PUNTO ADHESIVO": 0.08,
        "Soporte Balda Blanco": 0.08, "Soporte Balda Negro": 0.10,
        "PUNTO ADHESIVO REDONDO 30mm GEL": 0.085
    },
    "troquelado": {
        "Pequeño (< 1000x700)": {"arranque": 50.12, "tiro": 0.0624},
        "Mediano (Estándar)": {"arranque": 84.00, "tiro": 0.0936},
        "Grande (> 1000x700)": {"arranque": 112.01, "tiro": 0.1398}
    },
    # Stamping (película + calor). Similar a troquelado pero con consumible de película por superficie.
    "stamping": {"arreglo": 176.40, "pisada": 0.2117, "pelicula_m2": 0.4095},
    # Flexografía (coste fijo por plancha)
    "flexografia": {"arreglo": 180.0},
    "plotter": {"precio_hoja": 2.03},
    "narba": {
        "contracolado_a_mano_m2": 0.6864,
        "peliculado_menor_50x70_hoja": 0.0572,
        "guillotina_impresion_corte": 0.0175,
        "guillotina_plancha_corte": 0.1398
    }
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
def _tabla_merma_procesos_offset(hojas_netas: float) -> int:
    """Merma de procesos en OFFSET según tabla del cliente.

    IMPORTANTE:
    - La tabla se aplica sobre *hojas/pliegos netos* (ya ajustados por formato: Pliegos/Ud).
    - Redondea hacia arriba a hoja entera.
    """
    n = int(math.ceil(max(0.0, float(hojas_netas))))
    # Tabla (Desde incl., Hasta incl., Merma)
    tramos = [
        (0, 99, 20),
        (100, 149, 30),
        (150, 200, 40),
        (201, 600, 40),
        (601, 1000, 60),
        (1001, 1500, 60),
        (1501, 2000, 80),
        (2001, 3000, 80),
        (3001, 3500, 100),
        (3501, 5000, 100),
        (5001, 8000, 120),
        (8001, 10000, 120),
        (10001, 13000, 140),
        (13001, 15000, 140),
    ]
    for a, b, merma in tramos:
        if a <= n <= b:
            return int(merma)
    # A partir de 15001
    return 150


def _merma_impresion_offset_por_pasadas(n_tintas: int, barniz: bool) -> int:
    """Merma de impresión OFFSET por pasadas.

    Regla:
    - Base: 100 hojas (arranque mínimo).
    - Máquina 4 cuerpos: nº pasadas = ceil((tintas + (barniz?1:0)) / 4).
    - Merma = 100 + 50*(pasadas-1)

    Nota importante:
    - Si por UI/JSON llega n_tintas vacío/0, igualmente aplicamos el mínimo de 100 hojas.
    """
    # Robustez ante valores vacíos/None/strings
    try:
        tintas = int(n_tintas)
    except Exception:
        tintas = 0

    tintas = max(0, tintas)
    apps = max(1, tintas) + (1 if bool(barniz) else 0)  # mínimo 1 aplicación para garantizar arranque
    pasadas = int(math.ceil(apps / 4.0))
    return int(100 + 50 * max(0, pasadas - 1))


def calcular_mermas_estandar(n_uds: int, pliegos_por_ud: float = 1.0, es_digital: bool = False,
                            n_tintas: int = 4, barniz: bool = False) -> tuple[int, int]:
    """Devuelve (merma_proceso_hojas, merma_impresion_hojas).

    - Proceso (OFFSET): según tabla del cliente, aplicada a hojas netas = uds * pliegos_por_ud.
    - Impresión:
        * Offset: 100 + 50*(pasadas-1), con pasadas por (tintas + barniz) en grupos de 4.
        * Digital: mantiene comportamiento anterior (10 hojas) salvo que se fuerce manualmente.
    """
    uds = max(0, int(n_uds))
    pl = float(pliegos_por_ud) if pliegos_por_ud is not None else 1.0
    hojas_netas = uds * pl

    if es_digital:
        merma_proc = min(int(math.ceil(hojas_netas * 0.02)), 150)
        return int(merma_proc), 10

    merma_proc = _tabla_merma_procesos_offset(hojas_netas)
    merma_imp = _merma_impresion_offset_por_pasadas(n_tintas=n_tintas, barniz=barniz)
    return int(merma_proc), int(merma_imp)



# =========================================================
# NARBA 2026 - CONTRACOLADO
# =========================================================
def _get_contracolado_rate_m2(pieza: dict, db: dict, f_narba: float = 1.0) -> float:
    """Devuelve la tarifa de contracolado €/m² aplicable a una forma.

    Reglas:
    - Si la forma tiene "contracolado_a_mano" activo, aplica la tarifa a mano NARBA 2026:
      0,6864 €/m², independiente del material.
    - Si hay una plancha real seleccionada y tiene tarifa de pegado (>0), usa esa tarifa.
    - Si NO hay plancha ("Ninguna"), pero sí hay dos capas de cartoncillo u otro soporte,
      igualmente debe existir contracolado. En ese caso usa una tarifa de fallback segura
      equivalente al contracolado base por m², evitando que "Ninguna.peg = 0" deje el coste a 0.
    """
    try:
        mult = float(f_narba)
    except Exception:
        mult = 1.0

    narba = (db or {}).get("narba", {}) if isinstance((db or {}).get("narba", {}), dict) else {}

    if bool((pieza or {}).get("contracolado_a_mano", False)):
        try:
            return float(narba.get("contracolado_a_mano_m2", 0.6864)) * mult
        except Exception:
            return 0.6864 * mult

    # Tarifa base cuando no hay plancha real. Mantiene compatibilidad con tarifas antiguas:
    # primero intenta Microcanal/Canal 3.peg, y si no existe usa 0,2353 €/m².
    try:
        planchas = (db or {}).get("planchas", {})
        fallback = float(planchas.get("Microcanal / Canal 3", {}).get("peg", 0.2353))
        if fallback <= 0:
            fallback = 0.2353
    except Exception:
        planchas = {}
        fallback = 0.2353

    try:
        plancha = str((pieza or {}).get("pl", "Ninguna"))
        info = planchas.get(plancha, {}) if isinstance(planchas, dict) else {}
        rate = float(info.get("peg", 0.0)) if isinstance(info, dict) else 0.0

        # Importante: "Ninguna" existe en la tarifa con peg=0.0.
        # No debe bloquear el coste cuando se contracolan dos cartoncillos entre sí.
        if plancha.strip().lower() == "ninguna" or rate <= 0:
            rate = fallback

        return float(rate) * mult
    except Exception:
        return float(fallback) * mult


# =========================================================
# MERMAS (AUTO TRACKERS) - para actualizar defaults cuando cambian tintas/formato
# =========================================================
def _ss_autoref_init() -> None:
    # Trackers para saber si el usuario ha sobreescrito un valor o sigue en automático
    if "mermas_proc_auto_ref" not in st.session_state or not isinstance(st.session_state.get("mermas_proc_auto_ref"), dict):
        st.session_state.mermas_proc_auto_ref = {}
    if "mermas_imp_auto_ref" not in st.session_state or not isinstance(st.session_state.get("mermas_imp_auto_ref"), dict):
        st.session_state.mermas_imp_auto_ref = {}

def _ss_autoupdate_merma_proc(pid: int, qty: int, new_default: int) -> None:
    """Actualiza la merma de proceso solo si sigue en automático.

    IMPORTANTE:
    - La merma 0 es un valor manual válido.
    - No se debe interpretar 0 como "vacío" ni reemplazarlo por el default.
    """
    _ss_autoref_init()
    pid_k = str(pid)
    qty_k = str(int(qty))

    d = st.session_state.get("mermas_proc_manual", {})
    has_manual_value = False
    if isinstance(d, dict):
        for pk in (pid_k, pid):
            if pk in d and isinstance(d.get(pk), dict):
                sub = d.get(pk, {})
                has_manual_value = qty_k in sub or int(qty) in sub
                break
        if not has_manual_value:
            has_manual_value = qty_k in d or int(qty) in d  # legacy global

    cur = _ss_get_merma_proc(pid, qty, new_default)
    auto_pid = st.session_state.mermas_proc_auto_ref.setdefault(pid_k, {})
    old_auto = int(auto_pid.get(qty_k, new_default))

    # Solo actualizamos si no existía valor manual o si el valor actual coincide con el último automático.
    # Un 0 introducido por el usuario se respeta.
    if (not has_manual_value) or int(cur) == int(old_auto):
        st.session_state.mermas_proc_manual.setdefault(pid_k, {})
        st.session_state.mermas_proc_manual[pid_k][qty_k] = int(new_default)
        auto_pid[qty_k] = int(new_default)

def _ss_autoupdate_merma_imp(pid: int, qty: int, lado: str, new_default: int) -> None:
    """Auto-update para merma de impresión por lado, respetando 0 manual."""
    _ss_autoref_init()
    pid_k = str(pid)
    qty_k = str(int(qty))
    lado_k = str(lado)

    d = st.session_state.get("mermas_imp_manual", {})
    has_manual_value = False
    if isinstance(d, dict):
        for pk in (pid_k, pid):
            if pk in d and isinstance(d.get(pk), dict):
                sub = d.get(pk, {})
                v = sub.get(qty_k, sub.get(int(qty), None))
                if isinstance(v, dict):
                    has_manual_value = lado_k in v
                else:
                    has_manual_value = v is not None
                break

    cur = _ss_get_merma_imp(pid, qty, lado_k, new_default)
    auto_pid = st.session_state.mermas_imp_auto_ref.setdefault(pid_k, {})
    auto_qty = auto_pid.setdefault(qty_k, {})
    auto_known = lado_k in auto_qty
    old_auto = int(auto_qty.get(lado_k, new_default))

    # Solo actualizamos si:
    # - no había valor manual; o
    # - todavía no existe referencia automática para esta forma/cantidad/lado
    #   (caso típico: antes no era Offset y el campo estaba deshabilitado a 0); o
    # - el valor actual coincide con el último automático.
    #
    # Si el usuario puso 0 manualmente cuando el campo SÍ estaba activo en Offset,
    # auto_known será True y cur != old_auto, así que se respeta el 0.
    if (not has_manual_value) or (not auto_known) or int(cur) == int(old_auto):
        st.session_state.mermas_imp_manual.setdefault(pid_k, {})
        st.session_state.mermas_imp_manual[pid_k].setdefault(qty_k, {"cara": 0, "dorso": 0})
        if not isinstance(st.session_state.mermas_imp_manual[pid_k][qty_k], dict):
            try:
                iv = int(st.session_state.mermas_imp_manual[pid_k][qty_k])
            except Exception:
                iv = 0
            st.session_state.mermas_imp_manual[pid_k][qty_k] = {"cara": iv, "dorso": iv}
        st.session_state.mermas_imp_manual[pid_k][qty_k][lado_k] = int(new_default)
        auto_qty[lado_k] = int(new_default)


def _ss_sync_merma_imp_widget(pid: int, qty: int, lado: str, widget_key: str, new_default: int) -> None:
    """Sincroniza la merma de impresión con el default calculado, respetando 0 manual.

    Solo pisa el widget si:
    - todavía no existe la key del widget; o
    - el valor actual coincide con el último default automático.
    """
    _ss_autoref_init()
    pid_k = str(pid)
    qty_k = str(int(qty))
    lado_k = str(lado)

    auto_pid = st.session_state.mermas_imp_auto_ref.setdefault(pid_k, {})
    auto_qty = auto_pid.setdefault(qty_k, {})
    auto_known = lado_k in auto_qty
    old_auto = int(auto_qty.get(lado_k, int(new_default)))

    widget_exists = widget_key in st.session_state
    try:
        cur_widget = int(st.session_state.get(widget_key, int(new_default)))
    except Exception:
        cur_widget = int(new_default)

    # Si el widget venía de estar deshabilitado porque no era Offset, suele existir
    # con valor 0 pero SIN referencia automática. En ese caso sí debemos colocar
    # la merma de impresión automática al pasar a Offset.
    #
    # Si el usuario puso 0 manualmente con el campo activo, auto_known será True
    # y cur_widget != old_auto, así que no lo pisamos.
    if (not widget_exists) or (not auto_known) or (cur_widget == old_auto):
        st.session_state[widget_key] = int(new_default)
        st.session_state.mermas_imp_manual.setdefault(pid_k, {})
        st.session_state.mermas_imp_manual[pid_k].setdefault(qty_k, {"cara": 0, "dorso": 0})
        if not isinstance(st.session_state.mermas_imp_manual[pid_k][qty_k], dict):
            try:
                iv = int(st.session_state.mermas_imp_manual[pid_k][qty_k])
            except Exception:
                iv = 0
            st.session_state.mermas_imp_manual[pid_k][qty_k] = {"cara": iv, "dorso": iv}
        st.session_state.mermas_imp_manual[pid_k][qty_k][lado_k] = int(new_default)
        auto_qty[lado_k] = int(new_default)
# =========================================================
# MERMAS (SESSION HELPERS - compat JSON antiguo/nuevo)
# =========================================================
def _ss_get_merma_proc(pid: int, qty: int, default: int = 0) -> int:
    """Obtiene merma de procesos por forma+cantidad.
    Compatibilidad:
    - Nuevo: mermas_proc_manual = {pid: {qty: val}}
    - Antiguo: mermas_proc_manual = {qty: val}
    """
    d = st.session_state.get("mermas_proc_manual", {})
    try:
        pid_k = str(pid)
        qty_k = str(int(qty))
        if isinstance(d, dict):
            if pid_k in d and isinstance(d.get(pid_k), dict):
                sub = d[pid_k]
                return int(sub.get(qty_k, sub.get(int(qty), default)))
            if pid in d and isinstance(d.get(pid), dict):
                sub = d[pid]
                return int(sub.get(qty_k, sub.get(int(qty), default)))
            # legacy
            return int(d.get(qty_k, d.get(int(qty), default)))
    except Exception:
        pass
    return int(default)


def _ss_setdefault_merma_proc(pid: int, qty: int, value: int) -> None:
    d = st.session_state.get("mermas_proc_manual", {})
    if not isinstance(d, dict):
        d = {}
        st.session_state.mermas_proc_manual = d
    pid_k = str(pid)
    qty_k = str(int(qty))
    if pid_k not in d or not isinstance(d.get(pid_k), dict):
        d[pid_k] = {}
    sub = d[pid_k]
    if qty_k not in sub and int(qty) not in sub:
        sub[qty_k] = int(value)


def _ss_get_merma_imp(pid: int, qty: int, lado: str, default: int = 0) -> int:
    """Merma de impresión OFFSET por forma+cantidad+lado ('cara'/'dorso').

    Compatibilidad:
    - Nuevo: mermas_imp_manual = {pid: {qty: {'cara': x, 'dorso': y}}}
    - Intermedio: {pid: {qty: x}} -> aplica a ambos lados
    - Antiguo: {qty: x} -> aplica a ambos lados

    Nota:
    - La merma 0 es un valor manual válido. No se sustituye por el default.
    - Solo se usa el default si el valor no existe o no es interpretable.
    """
    d = st.session_state.get("mermas_imp_manual", {})

    def _sanitize(v: object) -> int | None:
        try:
            return int(v)  # type: ignore[arg-type]
        except Exception:
            return None

    try:
        pid_k = str(pid)
        qty_i = int(qty)
        qty_k = str(qty_i)

        # Intentamos leer en orden: nuevo -> intermedio -> legacy
        if isinstance(d, dict):
            # NUEVO / INTERMEDIO por pid
            for pk in (pid_k, pid):
                if pk in d and isinstance(d.get(pk), dict):
                    sub = d[pk]
                    v = sub.get(qty_k, sub.get(qty_i, None))
                    if isinstance(v, dict):
                        vv = _sanitize(v.get(lado, None))
                        if vv is not None:
                            return vv
                    else:
                        vv = _sanitize(v)
                        if vv is not None:
                            return vv

            # LEGACY global por cantidad
            v = d.get(qty_k, d.get(qty_i, None))
            if isinstance(v, dict):
                vv = _sanitize(v.get(lado, None))
                if vv is not None:
                    return vv
            else:
                vv = _sanitize(v)
                if vv is not None:
                    return vv
    except Exception:
        pass

    # Si llegamos aquí, devolvemos default porque no existe valor manual.
    try:
        _ss_setdefault_merma_imp(int(pid), int(qty), str(lado), int(default))
    except Exception:
        pass
    return int(default)


def _ss_setdefault_merma_imp(pid: int, qty: int, lado: str, value: int) -> None:
    """Inicializa merma de impresión si no existe. Respeta 0 como valor manual válido."""
    d = st.session_state.get("mermas_imp_manual", {})
    if not isinstance(d, dict):
        d = {}
        st.session_state.mermas_imp_manual = d
    pid_k = str(pid)
    qty_i = int(qty)
    qty_k = str(qty_i)
    if pid_k not in d or not isinstance(d.get(pid_k), dict):
        d[pid_k] = {}
    sub = d[pid_k]

    # Normalizamos a dict por lado ('cara'/'dorso')
    v = sub.get(qty_k, sub.get(qty_i, None))
    if not isinstance(v, dict):
        # Si no existe, inicializamos ambos lados con el default calculado.
        # Si venía como entero legacy, lo convertimos respetando el valor, incluido 0.
        if v is None:
            v = {"cara": int(value), "dorso": int(value)}
        else:
            try:
                iv = int(v)
            except Exception:
                iv = int(value)
            v = {"cara": iv, "dorso": iv}
        sub[qty_k] = v

    # Solo escribimos default si el lado no existe o está vacío/no interpretable.
    current = v.get(lado, None)
    if current in (None, ""):
        v[lado] = int(value)
    else:
        try:
            int(current)
        except Exception:
            v[lado] = int(value)
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
# IMPRESIONES POR CANTIDAD (multi-tirada)
# =========================================================
def _split_equal(total: int, n: int) -> list:
    """Reparte 'total' en 'n' partes lo más igualadas posible."""
    if n <= 1 or total <= 0:
        return [int(total)] if total > 0 else []
    base = total // n
    rem = total % n
    partes = [base + (1 if i < rem else 0) for i in range(n)]
    return [p for p in partes if p > 0]

def _parse_partes_str(s: str) -> list:
    """Parsea '100+400+500' o '100, 400, 500' -> [100,400,500]."""
    if not s:
        return []
    nums = re.split(r"[,+\s]+", str(s).strip())
    out = []
    for x in nums:
        x = x.strip()
        if x.isdigit():
            v = int(x)
            if v > 0:
                out.append(v)
    return out

def obtener_partes_impresion_por_cantidad(q_total: int) -> list:
    """Devuelve el desglose de impresiones para una cantidad concreta.

    Regla:
    - Si no hay configuración: 1 impresión con q_total.
    - Si hay N impresiones: se reparte igual o se usa el desglose manual.
    - Siempre normaliza para que la suma sea q_total (fallback a reparto igual).
    """
    if q_total <= 0:
        return []
    cfg_all = st.session_state.get("impresiones_by_qty", {})
    if not isinstance(cfg_all, dict):
        return [int(q_total)]
    cfg = cfg_all.get(str(int(q_total)), None)
    if not isinstance(cfg, dict):
        return [int(q_total)]

    try:
        n = int(cfg.get("n", 1))
    except Exception:
        n = 1
    n = max(1, n)
    modo = str(cfg.get("modo", "igual")).lower().strip()
    partes = cfg.get("partes", [])
    if isinstance(partes, list):
        try:
            partes = [int(x) for x in partes if int(x) > 0]
        except Exception:
            partes = []
    else:
        partes = []

    if n == 1:
        return [int(q_total)]
    if modo == "manual" and partes and sum(partes) == int(q_total) and len(partes) == n:
        return partes

    # Fallback: reparto igual
    return _split_equal(int(q_total), int(n))


def obtener_partes_impresion_por_formato(pid: int, q_total: int) -> list:
    """Devuelve el desglose de impresiones para una cantidad concreta, PERO por formato (forma).

    - Se activa solo si el TIC (checkbox) del formato está activo.
    - Si no está activo, devuelve 1 impresión con q_total.
    - Si existe configuración por formato, la aplica.
    - Fallback de compatibilidad: si no hay cfg por formato, usa 'impresiones_by_qty' (global legacy).
    """
    if q_total <= 0:
        return []
    pid_key = str(int(pid))

    enabled_all = st.session_state.get("impresiones_by_qty_fmt_enabled", {})
    enabled = False
    if isinstance(enabled_all, dict):
        enabled = bool(enabled_all.get(pid_key, False))
    if not enabled:
        return [int(q_total)]

    cfg_fmt_all = st.session_state.get("impresiones_by_qty_fmt", {})
    if isinstance(cfg_fmt_all, dict):
        cfg_all = cfg_fmt_all.get(pid_key, {})
        if isinstance(cfg_all, dict):
            cfg = cfg_all.get(str(int(q_total)), None)
            if isinstance(cfg, dict):
                try:
                    n = int(cfg.get("n", 1))
                except Exception:
                    n = 1
                n = max(1, n)
                modo = str(cfg.get("modo", "igual")).lower().strip()
                partes = cfg.get("partes", [])
                if isinstance(partes, list):
                    try:
                        partes = [int(x) for x in partes if int(x) > 0]
                    except Exception:
                        partes = []
                else:
                    partes = []

                if n == 1:
                    return [int(q_total)]
                if modo == "manual" and partes and sum(partes) == int(q_total) and len(partes) == n:
                    return partes
                return _split_equal(int(q_total), int(n))

    # Legacy global (por si venimos de JSON antiguo)
    return obtener_partes_impresion_por_cantidad(int(q_total))
# =========================================================
# EMBALAJES (múltiples)
# =========================================================
TIPOS_EMB = ["Manual", "Embalaje Guaina (Automático)", "Embalaje en Plano", "Embalaje en Volumen", "Aros de refuerzo"]
EMB_MATS = ["Canal 5", "D/D"]

def _tarifa(categoria: str, campo: str, bloque: str = None) -> float:
    base = PRECIOS_BASE[categoria]
    actual = st.session_state.get("db_precios", {}).get(categoria, {})
    if bloque is not None:
        base = base[bloque]
        actual = actual.get(bloque, {})
    return float(actual.get(campo, base[campo]))


def emb_mult(material: str) -> float:
    return _tarifa("embalajes", "multiplicador_dd") if material == "D/D" else 1.0


# =========================================================
# AROS DE REFUERZO - TARIFA (C/5) + conversión a D/D
# Derivado de MAINSA.pdf (A2 Kartro) - Tarifa A26
# Modelo: precio_ud(C/5) ≈ a0 + a_area*area_m2 + a_invQ/(Q**p)
# - area_m2 = (L*W) en m² (medidas máximas en plano)
# - Q = nº de aros (se calcula como ceil(cantidad / uds_por_caja))
# Para D/D: multiplicador emb_mult (1.5)
# =========================================================
_AROS_REF_A0 = 0.120838225
_AROS_REF_AAREA = 0.469363762
_AROS_REF_AINVQ = 1600.52632
_AROS_REF_P = 1.48

def _aros_refuerzo_precio_ud_c5(L_mm: float, W_mm: float, Q_aros: int) -> float:
    """Precio unitario (€/aro) en Canal 5 (C/5), estimado por fórmula ajustada."""
    try:
        L = float(L_mm or 0.0)
        W = float(W_mm or 0.0)
    except Exception:
        L, W = 0.0, 0.0
    Q = max(0, int(Q_aros or 0))
    if L <= 0 or W <= 0 or Q <= 0:
        return 0.0
    area_m2 = (L / 1000.0) * (W / 1000.0)
    return float(_tarifa("embalajes", "precio_ud", "aros") + _tarifa("embalajes", "precio_m2", "aros") * area_m2 + _tarifa("embalajes", "arreglo", "aros") / (Q ** _tarifa("embalajes", "exponente", "aros")))

def aros_refuerzo_precio_ud(L_mm: float, W_mm: float, Q_aros: int, material: str) -> float:
    """Precio unitario (€/aro) según material (Canal 5 o D/D)."""
    return float(_aros_refuerzo_precio_ud_c5(L_mm, W_mm, Q_aros) * emb_mult(material))

def embalaje_plano_unit(L_mm, W_mm, H_mm, Q):
    if Q <= 0 or L_mm <= 0 or W_mm <= 0 or H_mm <= 0:
        return 0.0, 0.0
    L = L_mm / 1000.0
    W = W_mm / 1000.0
    H = H_mm / 1000.0
    S = (L * W) + 2.0 * H * (L + W)
    P = ((_tarifa("embalajes", "arreglo", "plano") + (_tarifa("embalajes", "arreglo_m2", "plano") * S)) / float(Q)) + _tarifa("embalajes", "precio_ud", "plano") + (_tarifa("embalajes", "precio_m2", "plano") * S)
    return float(P), float(S)

def embalaje_volumen_unit(L_mm, A_mm, H_mm, Q):
    if Q <= 0 or L_mm <= 0 or A_mm <= 0 or H_mm <= 0:
        return 0.0, 0.0
    L = L_mm / 1000.0
    A = A_mm / 1000.0
    H = H_mm / 1000.0
    S = (2.0 * L + 2.0 * A + 0.05) * (H + A)
    P = ((_tarifa("embalajes", "arreglo", "volumen") + (_tarifa("embalajes", "arreglo_m2", "volumen") * S)) / float(Q)) + (_tarifa("embalajes", "precio_m2", "volumen") * S)
    return float(P), float(S)

def crear_embalaje_vacio(idx):
    return {
        "id": f"emb_{idx}",
        "nombre": f"Embalaje {idx+1}",
        "tipo": "Manual",
        "material": "Canal 5",
        "dims": {"L": 0.0, "W": 0.0, "H": 0.0},
        "uds_por_caja": 1,
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
        return _tarifa("offset", "minimo_tinta")
    if n <= 500:
        extra = (n - 100) * _tarifa("offset", "extra_101_500")
        return _tarifa("offset", "minimo_tinta") + extra
    base = _tarifa("offset", "base_501_2000")
    if n > 2000:
        base += (n - 2000) * _tarifa("offset", "extra_2001")
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
        "fr24": False,
        "fr24_rate": 0.05,
        "cor_default": "Troquelado",
        "cor_by_qty": {},
        "cobrar_arreglo": True,
        "pv_troquel": 0.0,
        "troquel_piezas": 0,
        "stamping": False,
        "stamping_w": 0,
        "stamping_h": 0,
        "stamping_cobrar_arreglo": True,
        "flexografia": False,
    }

def es_digital_en_proyecto(piezas_dict):
    for p in piezas_dict.values():
        if p.get("im") == "Digital" or p.get("im_d") == "Digital":
            return True
    return False

# =========================================================
# SESSION STATE INIT
# =========================================================
def _completar_tarifas_editables(db: dict) -> None:
    """Añade campos editables ausentes sin sustituir las tarifas del proyecto.

    Para stamping histórico se conservan los fallbacks que aplicaba el motor.
    No se rellenan calidades ni precios de materiales históricos.
    """
    defaults = {k: deepcopy(PRECIOS_BASE[k]) for k in (
        "stamping", "flexografia", "plotter", "narba", "offset", "impresion_digital",
        "mano_obra", "embalajes", "flexico", "extras_base")}
    defaults["stamping"] = {"arreglo": 168.0, "pisada": 0.21, "pelicula_m2": 0.39}
    def completar(actual, base):
        for key, value in base.items():
            if key not in actual:
                actual[key] = deepcopy(value)
            elif isinstance(value, dict) and isinstance(actual[key], dict):
                completar(actual[key], value)
    completar(db, defaults)
    db.setdefault("laminado_digital", 3.5)


if "db_precios" not in st.session_state: st.session_state.db_precios = deepcopy(PRECIOS_BASE)
_completar_tarifas_editables(st.session_state.db_precios)

# Compatibilidad en caliente: "Poliéster" equivale a "Poliéster oro".
# Actualiza los precios existentes sin crear opciones duplicadas.
if isinstance(st.session_state.get("db_precios"), dict):
    if "peliculado" not in st.session_state.db_precios or not isinstance(st.session_state.db_precios.get("peliculado"), dict):
        st.session_state.db_precios["peliculado"] = deepcopy(PRECIOS_BASE["peliculado"])
    else:
        # Los precios de proyecto prevalecen incluso después de un rerun.
        _pel = st.session_state.db_precios["peliculado"]
        for _old, _new in (("Poliéster oro brillo", "Poliéster brillo"),
                           ("Poliéster oro+mate", "Poliéster mate")):
            if _old in _pel:
                _pel.setdefault(_new, _pel[_old])
        _pel.setdefault("Poliéster brillo", 0.53)
        _pel.setdefault("Poliéster mate", 0.79)

def _asegurar_bb_test_planchas_en_sesion() -> None:
    """Asegura la nueva calidad B/B TEST sin reiniciar tarifas ni proyecto.

    Esto permite que una sesión ya abierta o un JSON antiguo puedan ver la nueva
    calidad sin perder los precios/materiales que el usuario ya tuviera cargados.
    """
    db = st.session_state.get("db_precios")
    if not isinstance(db, dict):
        st.session_state.db_precios = deepcopy(PRECIOS_BASE)
        return

    planchas = db.setdefault("planchas", {})
    if not isinstance(planchas, dict):
        db["planchas"] = deepcopy(PRECIOS_BASE.get("planchas", {}))
        return

    for nombre, tarifas in PRECIOS_BASE["planchas"].items():
        planchas.setdefault(nombre, deepcopy(tarifas))

    if isinstance(planchas.get("Ninguna"), dict):
        planchas["Ninguna"].setdefault("C/C", 0.0)
        planchas["Ninguna"].setdefault("B/C", 0.0)
        planchas["Ninguna"].setdefault("B/B", 0.0)
        planchas["Ninguna"].setdefault("B/B TEST", 0.0)
        planchas["Ninguna"].setdefault("peg", 0.0)
    if isinstance(planchas.get("Microcanal / Canal 3"), dict):
        planchas["Microcanal / Canal 3"].setdefault("B/B TEST", 1.038)
    if isinstance(planchas.get("Doble Micro / Doble Doble"), dict):
        planchas["Doble Micro / Doble Doble"].setdefault("B/B TEST", 1.334)


_asegurar_bb_test_planchas_en_sesion()

# =========================================================
# TARIFA MATERIA PRIMA (comparación vs proyectos importados)
# =========================================================
_TARIFA_MATERIA_PRIMA_CATS = ("cartoncillo", "planchas", "rigidos", "peliculado")

def _subset_materia_prima(db: dict) -> dict:
    """Devuelve un subconjunto estable de db_precios para comparar tarifas de materia prima.
    Solo incluye categorías de materia prima (no procesos).
    """
    out: dict = {}
    if not isinstance(db, dict):
        return out
    for cat in _TARIFA_MATERIA_PRIMA_CATS:
        v = db.get(cat, None)
        if isinstance(v, dict):
            out[cat] = deepcopy(v)
    return out


def _normalizar_mp_para_hash(v: object) -> object:
    """Normaliza valores para comparar tarifas con tolerancia a floats."""
    if isinstance(v, float):
        return round(v, 6)
    if isinstance(v, (int, bool)) or v is None:
        return v
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return [_normalizar_mp_para_hash(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _normalizar_mp_para_hash(val) for k, val in v.items()}
    try:
        return round(float(v), 6)
    except Exception:
        return str(v)


def _hash_materia_prima(db: dict) -> str:
    """Hash estable (ordenado) del subconjunto de materia prima."""
    subset_norm = _normalizar_mp_para_hash(_subset_materia_prima(db))
    try:
        blob = json.dumps(subset_norm, sort_keys=True, ensure_ascii=False)
    except Exception:
        blob = str(subset_norm)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()

def _limpiar_widgets_tarifas(incluir_descuentos=False) -> None:
    # Streamlit prioriza la clave del widget sobre su valor inicial.
    prefixes = ("cost_cart_", "cost_pl_", "cost_rig_", "rigw_", "righ_", "cost_pel_", "cost_peg_")
    for key in list(st.session_state):
        if str(key).startswith(prefixes) or (incluir_descuentos and (str(key).startswith(("db_desc_", "cost_", "trq_", "tarifa_", "fr24r_")) or key == "plotter_precio")):
            del st.session_state[key]


def _invalidar_calculo() -> None:
    for key in ("_calc_cache", "_calc_last_signature", "_export_blob", "_export_hash",
                "_imported_compras_legible", "_imported_resumen_costes"):
        st.session_state[key] = None
    st.session_state.compras_legible_export = {}
    st.session_state.resumen_costes_export = {}
    st.session_state._calc_requested = False
    st.session_state._calc_status = "Pendiente"
    st.session_state._json_downloaded = False


def _aplicar_tarifa_actual_materia_prima() -> None:
    """Actualiza SOLO materia prima (cartoncillo/planchas/rigidos/peliculado) a la tarifa actual (PRECIOS_BASE).

    Importante:
    - NO reinicia el proyecto ni toca piezas/cantidades/extras/embalajes/externos.
    - Actualiza EN SITIO (in-place) para minimizar efectos colaterales en widgets que lean de db_precios.
    - Mantiene cualquier material "custom" que ya existiese en el proyecto.
    """
    db = st.session_state.get("db_precios")
    if not isinstance(db, dict):
        # Si por algún motivo viene corrupto, creamos un dict basado en lo actual para no perder claves.
        db = deepcopy(PRECIOS_BASE)
        st.session_state.db_precios = db

    base = PRECIOS_BASE  # referencia (no mutar)

    for cat in _TARIFA_MATERIA_PRIMA_CATS:
        base_cat = base.get(cat)
        if not isinstance(base_cat, dict):
            continue

        cur_cat = db.get(cat)
        if not isinstance(cur_cat, dict):
            cur_cat = {}
            db[cat] = cur_cat

        # Reemplazamos/actualizamos solo las entradas de la tarifa actual (manteniendo posibles claves extra del proyecto)
        for k, v in base_cat.items():
            if isinstance(v, dict) and isinstance(cur_cat.get(k), dict):
                cur_cat[k].update(deepcopy(v))
            else:
                cur_cat[k] = deepcopy(v)

    # Dejamos constancia de que ya está actualizado respecto a la tarifa actual
    st.session_state._tarifa_mp_import_hash = _hash_materia_prima(st.session_state.db_precios)
    st.session_state._tarifa_mp_mismatch = False
    _limpiar_widgets_tarifas()
    _invalidar_calculo()

if "piezas_dict" not in st.session_state: st.session_state.piezas_dict = {1: crear_forma_vacia(1)}
if "lista_extras_grabados" not in st.session_state: st.session_state.lista_extras_grabados = []
if "embalajes" not in st.session_state: st.session_state.embalajes = [crear_embalaje_vacio(0)]
if "externos" not in st.session_state: st.session_state.externos = [crear_externo_vacio(0)]
if "mermas_imp_manual" not in st.session_state: st.session_state.mermas_imp_manual = {}
if "mermas_imp_digital_manual" not in st.session_state: st.session_state.mermas_imp_digital_manual = {}
if "mermas_proc_manual" not in st.session_state: st.session_state.mermas_proc_manual = {}
if "impresiones_by_qty" not in st.session_state: st.session_state.impresiones_by_qty = {}  # {str(cantidad): {"n": int, "modo": "igual"|"manual", "partes": [int,...]}}
if "impresiones_by_qty_fmt" not in st.session_state: st.session_state.impresiones_by_qty_fmt = {}  # {str(pid): {str(cantidad): {"n": int, "modo": "igual"|"manual", "partes": [int,...]}}}
if "impresiones_by_qty_fmt_enabled" not in st.session_state: st.session_state.impresiones_by_qty_fmt_enabled = {}  # {str(pid): bool}

if "brf" not in st.session_state: st.session_state.brf = ""
if "version_presupuesto" not in st.session_state: st.session_state.version_presupuesto = ""
if "cli" not in st.session_state: st.session_state.cli = ""
if "desc" not in st.session_state: st.session_state.desc = ""
if "notas" not in st.session_state: st.session_state.notas = ""
if "cants_str_saved" not in st.session_state: st.session_state.cants_str_saved = ""

if "unidad_t" not in st.session_state: st.session_state.unidad_t = "Segundos"
if "t_input" not in st.session_state: st.session_state.t_input = 0.0

if "rell_enabled" not in st.session_state: st.session_state.rell_enabled = False
if "rell_t_input" not in st.session_state: st.session_state.rell_t_input = 0.0
if "arm_enabled" not in st.session_state: st.session_state.arm_enabled = False
if "arm_t_input" not in st.session_state: st.session_state.arm_t_input = 0.0

if "dif_ud" not in st.session_state: st.session_state.dif_ud = 0.091
if "dif_preset_sel" not in st.session_state: st.session_state.dif_preset_sel = "0,091 (standard)"
if "imp_fijo_pvp" not in st.session_state: st.session_state.imp_fijo_pvp = 500.0
if "repeticion_proyecto" not in st.session_state: st.session_state.repeticion_proyecto = False
if "imp_fijo_pvp_prev" not in st.session_state: st.session_state.imp_fijo_pvp_prev = None
if "margen" not in st.session_state: st.session_state.margen = 2.2
if "comercial_1" not in st.session_state: st.session_state.comercial_1 = ""
if "comercial_2" not in st.session_state: st.session_state.comercial_2 = ""
if "last_auto_margen" not in st.session_state: st.session_state.last_auto_margen = float(st.session_state.margen)


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
if "_tarifa_mp_import_hash" not in st.session_state: st.session_state._tarifa_mp_import_hash = None
if "_tarifa_mp_mismatch" not in st.session_state: st.session_state._tarifa_mp_mismatch = False
if "_export_blob" not in st.session_state: st.session_state._export_blob = None
if "_export_filename" not in st.session_state: st.session_state._export_filename = "oferta.json"
if "_imported_compras_legible" not in st.session_state: st.session_state._imported_compras_legible = None
if "_imported_resumen_costes" not in st.session_state: st.session_state._imported_resumen_costes = None
if "_json_downloaded" not in st.session_state: st.session_state._json_downloaded = False
if "_json_downloaded_filename" not in st.session_state: st.session_state._json_downloaded_filename = ""
if "_import_lock_margen" not in st.session_state: st.session_state._import_lock_margen = False

# =========================================================
# MODO CÁLCULO MANUAL (PERFORMANCE)
# - El motor de cálculo es pesado. En local (Windows) puede ir lento si recalcula en cada rerun.
# - Con este modo, solo recalculamos al pulsar el botón "🧮 Calcular" en la barra lateral.
# =========================================================
if "_calc_requested" not in st.session_state:
    st.session_state._calc_requested = False
if "_calc_cache" not in st.session_state:
    # Guarda: {"res_final":..., "desc_full":..., "compras_legible":..., "resumen_costes_export":..., "oferta_html":..., "fname_html":...}
    st.session_state._calc_cache = None
if "_calc_status" not in st.session_state:
    st.session_state._calc_status = "Pendiente"

if "_calc_last_signature" not in st.session_state:
    st.session_state._calc_last_signature = None

def _calc_project_signature() -> str:
    """Firma estable de los datos que afectan al cálculo.

    Se usa para avisar cuando hay cambios introducidos que aún no se han recalculado.
    No incluye cachés, blobs de descarga ni flags internos.
    """
    keys = [
        "brf", "version_presupuesto", "cli", "desc", "notas", "cants_str_saved",
        "piezas_dict", "lista_extras_grabados", "embalajes", "externos",
        "mermas_imp_manual", "mermas_imp_digital_manual", "mermas_proc_manual",
        "impresiones_by_qty", "impresiones_by_qty_fmt", "impresiones_by_qty_fmt_enabled",
        "unidad_t", "t_input", "rell_enabled", "rell_t_input", "arm_enabled", "arm_t_input",
        "dif_ud", "dif_preset_sel", "imp_fijo_pvp", "repeticion_proyecto",
        "margen", "margen_extras", "margen_embalajes", "descuento_procesos",
        "db_descuentos", "db_precios",
    ]
    snap = {}
    for k in keys:
        try:
            snap[k] = deepcopy(st.session_state.get(k))
        except Exception:
            snap[k] = str(st.session_state.get(k))
    try:
        payload = json.dumps(_normalizar_mp_para_hash(snap), sort_keys=True, ensure_ascii=False)
    except Exception:
        payload = repr(snap)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# =========================================================
# MERMAS: SINCRONIZACIÓN CENTRALIZADA
# =========================================================
def _sync_mermas_defaults_actuales(lista_cants_actuales: list[int]) -> None:
    """Sincroniza defaults de mermas con las formas/cantidades actuales.

    Por qué existe:
    - Streamlit ejecuta la pantalla de arriba a abajo.
    - Al añadir una forma o cambiar impresión/tintas, la forma puede actualizarse
      después del primer bloque de defaults.
    - Antes, la merma de impresión de una forma nueva podía no quedar inicializada
      hasta el siguiente rerun; por eso parecía que solo se colocaba al añadir otra forma.

    Reglas:
    - Respeta 0 como valor manual válido si el usuario ya editó la merma con el campo activo.
    - Si una cara/dorso acaba de pasar a Offset y venía de 0 deshabilitado, coloca el default automático.
    """
    if not lista_cants_actuales:
        return

    piezas = st.session_state.get("piezas_dict", {})
    if not isinstance(piezas, dict):
        return

    _ss_autoref_init()

    for pid, p in piezas.items():
        try:
            pid_i = int(pid)
        except Exception:
            continue

        try:
            pl = float(p.get("pliegos", 1.0) or 1.0)
        except Exception:
            pl = 1.0

        im_c = str(p.get("im", "No"))
        im_d = str(p.get("im_d", "No"))

        try:
            nt_c = int(p.get("nt", 4) or 0)
        except Exception:
            nt_c = 4
        try:
            nt_d = int(p.get("nt_d", 4) or 0)
        except Exception:
            nt_d = 4

        ba_c = bool(p.get("ba", False))
        ba_d = bool(p.get("ba_d", False))

        for q in lista_cants_actuales:
            try:
                q_i = int(q)
            except Exception:
                continue

            mp_off, _mi_ign = calcular_mermas_estandar(
                q_i,
                pliegos_por_ud=pl,
                es_digital=False,
                n_tintas=4,
                barniz=False,
            )
            _ss_autoupdate_merma_proc(pid_i, q_i, int(mp_off))

            if im_c == "Offset":
                mi_c = _merma_impresion_offset_por_pasadas(nt_c, ba_c)
                _ss_autoupdate_merma_imp(pid_i, q_i, "cara", int(mi_c))

            if im_d == "Offset":
                mi_d = _merma_impresion_offset_por_pasadas(nt_d, ba_d)
                _ss_autoupdate_merma_imp(pid_i, q_i, "dorso", int(mi_d))

    # Digital global por cantidad
    if "mermas_imp_digital_manual" not in st.session_state or not isinstance(st.session_state.get("mermas_imp_digital_manual"), dict):
        st.session_state.mermas_imp_digital_manual = {}

    for q in lista_cants_actuales:
        try:
            q_i = int(q)
        except Exception:
            continue
        _mp_dig, mi_dig = calcular_mermas_estandar(q_i, pliegos_por_ud=1.0, es_digital=True)
        if q_i not in st.session_state.mermas_imp_digital_manual and str(q_i) not in st.session_state.mermas_imp_digital_manual:
            st.session_state.mermas_imp_digital_manual[q_i] = int(mi_dig)


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
        "pd_", "gd_", "cor_def_", "arr_", "pvt_", "trqp_", "fr24_", "fr24r_", "stamp_", "stampw_", "stamph_", "stamparr_", "flexo_", "contramano_", "im_d_", "nt_d_", "ba_d_", "ld_d_", "pel_d_"
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
        for k in [f"mi_{q}", f"mp_{q}", f"mid_{q}"]:
            if k in st.session_state:
                del st.session_state[k]


    # Impresiones por cantidad (multi-tirada)
    for q in lista_cants:
        for k in [f"impn_{q}", f"impigual_{q}", f"impman_{q}"]:
            if k in st.session_state:
                del st.session_state[k]

    # Impresiones por cantidad (multi-tirada) - POR FORMATO
    for pid in list(st.session_state.get("piezas_dict", {}).keys()):
        for q in lista_cants:
            for k in [f"impact_{pid}", f"impn_{pid}_{q}", f"impigual_{pid}_{q}", f"impman_{pid}_{q}"]:
                if k in st.session_state:
                    del st.session_state[k]

    for i in range(max(0, extras_len)):
        for k in [f"exc_{i}", f"exq_{i}", f"exd_{i}"]:
            if k in st.session_state:
                del st.session_state[k]

    for ei in range(max(0, embalajes_len)):
        for k in [f"emb_name_{ei}", f"emb_tipo_{ei}", f"emb_mat_{ei}", f"embUPC_{ei}", f"embL_{ei}", f"embW_{ei}", f"embH_{ei}", f"emb_del_{ei}"]:
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
        st.session_state[f"pel_{pid}"] = _normalizar_peliculado_oro_legacy(p.get("pel", "Sin Peliculado"))

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
        st.session_state[f"stamp_{pid}"] = bool(p.get("stamping", False))
        st.session_state[f"stampw_{pid}"] = int(p.get("stamping_w", 0))
        st.session_state[f"stamph_{pid}"] = int(p.get("stamping_h", 0))
        st.session_state[f"stamparr_{pid}"] = bool(p.get("stamping_cobrar_arreglo", True))
        st.session_state[f"flexo_{pid}"] = bool(p.get("flexografia", False))
        st.session_state[f"fr24_{pid}"] = bool(p.get("fr24", False))
        st.session_state[f"fr24r_{pid}"] = float(p.get("fr24_rate", 0.05))
        st.session_state[f"contramano_{pid}"] = bool(p.get("contracolado_a_mano", False))
        st.session_state[f"trqp_{pid}"] = int(p.get("troquel_piezas", 0) or 0)

        st.session_state[f"im_d_{pid}"] = p.get("im_d", "No")
        st.session_state[f"nt_d_{pid}"] = int(p.get("nt_d", 0))
        st.session_state[f"ba_d_{pid}"] = bool(p.get("ba_d", False))
        st.session_state[f"ld_d_{pid}"] = bool(p.get("ld_d", False))
        st.session_state[f"pel_d_{pid}"] = _normalizar_peliculado_oro_legacy(p.get("pel_d", "Sin Peliculado"))
    # Impresiones por cantidad (multi-tirada)
    cfg_all = st.session_state.get("impresiones_by_qty", {})
    if not isinstance(cfg_all, dict):
        cfg_all = {}
    for q in lista_cants:
        cfg = cfg_all.get(str(int(q)), {}) if isinstance(cfg_all.get(str(int(q)), {}), dict) else {}
        try:
            n = int(cfg.get("n", 1))
        except Exception:
            n = 1
        n = max(1, n)
        modo = str(cfg.get("modo", "igual")).lower().strip()
        partes = cfg.get("partes", [])
        if not isinstance(partes, list):
            partes = []
        st.session_state[f"impn_{q}"] = n
        st.session_state[f"impigual_{q}"] = (modo != "manual")
        if modo == "manual" and partes:
            try:
                st.session_state[f"impman_{q}"] = "+".join(str(int(x)) for x in partes)
            except Exception:
                st.session_state[f"impman_{q}"] = ""
        else:
            st.session_state.setdefault(f"impman_{q}", "")

    # Impresiones por cantidad (multi-tirada) - POR FORMATO (si viene en JSON)
    cfg_fmt_all = st.session_state.get("impresiones_by_qty_fmt", {})
    en_all = st.session_state.get("impresiones_by_qty_fmt_enabled", {})
    if isinstance(cfg_fmt_all, dict) and isinstance(en_all, dict):
        for pid, _p in piezas_dict.items():
            pid_key = str(int(pid))
            st.session_state[f"impact_{pid}"] = bool(en_all.get(pid_key, False))
            cfg_fmt = cfg_fmt_all.get(pid_key, {}) if isinstance(cfg_fmt_all.get(pid_key, {}), dict) else {}
            for q in lista_cants:
                cfg = cfg_fmt.get(str(int(q)), {}) if isinstance(cfg_fmt.get(str(int(q)), {}), dict) else {}
                try:
                    n = int(cfg.get("n", 1))
                except Exception:
                    n = 1
                n = max(1, n)
                modo = str(cfg.get("modo", "igual")).lower().strip()
                partes = cfg.get("partes", [])
                if not isinstance(partes, list):
                    partes = []
                st.session_state[f"impn_{pid}_{q}"] = n
                st.session_state[f"impigual_{pid}_{q}"] = (modo != "manual")
                if modo == "manual" and partes:
                    try:
                        st.session_state[f"impman_{pid}_{q}"] = "+".join(str(int(x)) for x in partes)
                    except Exception:
                        st.session_state[f"impman_{pid}_{q}"] = ""
                else:
                    st.session_state.setdefault(f"impman_{pid}_{q}", "")


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


def _get_merma_impresion_digital_hojas(q: int, default: int | None = None) -> int:
    """Devuelve la merma de impresión DIGITAL para una cantidad, respetando 0 como valor manual válido.

    Compatibilidad:
    - Nuevo/actual: st.session_state.mermas_imp_digital_manual puede tener claves int o str.
    - Si no existe valor manual, usa el default digital calculado por calcular_mermas_estandar().
    """
    try:
        q_i = int(q)
    except Exception:
        q_i = 0

    if default is None:
        try:
            default_i = int(calcular_mermas_estandar(q_i, es_digital=True)[1])
        except Exception:
            default_i = 10
    else:
        try:
            default_i = int(default)
        except Exception:
            default_i = 10

    d = st.session_state.get("mermas_imp_digital_manual", {})
    if not isinstance(d, dict):
        return int(default_i)

    # IMPORTANTE: 0 es válido. No usar "or default".
    for k in (q_i, str(q_i)):
        if k in d:
            try:
                return int(float(d.get(k)))
            except Exception:
                return int(default_i)

    return int(default_i)

def _normalizar_peliculado_oro_legacy(value: object) -> str:
    """Compatibilidad con la v74: el poliéster oro no es una opción aparte."""
    s = str(value or "Sin Peliculado")
    if s == "Poliéster oro brillo":
        return "Poliéster brillo"
    if s == "Poliéster oro+mate":
        return "Poliéster mate"
    return s


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
    _allowed_cor = {"Troquelado", "Plotter", "Sin corte"}
    if base["cor_default"] not in _allowed_cor:
        base["cor_default"] = "Troquelado"
    if not isinstance(base.get("cor_by_qty", {}), dict):
        base["cor_by_qty"] = {}
    else:
        base["cor_by_qty"] = {
            str(k): (str(vv) if str(vv) in _allowed_cor else base["cor_default"])
            for k, vv in base["cor_by_qty"].items()
        }
    base["cobrar_arreglo"] = _coerce_bool(base.get("cobrar_arreglo", True), True)
    base["pv_troquel"] = _coerce_float(base.get("pv_troquel", 0.0), 0.0)
    base["stamping"] = _coerce_bool(base.get("stamping", False), False)
    base["stamping_w"] = _coerce_int(base.get("stamping_w", 0), 0)
    base["stamping_h"] = _coerce_int(base.get("stamping_h", 0), 0)
    base["stamping_cobrar_arreglo"] = _coerce_bool(base.get("stamping_cobrar_arreglo", True), True)

    base["flexografia"] = _coerce_bool(base.get("flexografia", False), False)
    base["contracolado_a_mano"] = _coerce_bool(base.get("contracolado_a_mano", False), False)

    base["troquel_piezas"] = max(0, _coerce_int(base.get("troquel_piezas", 0), 0))

    return base

def normalizar_import(di: dict):
    _limpiar_widgets_tarifas(incluir_descuentos=True)
    _invalidar_calculo()
    prev_cants = parse_cantidades(st.session_state.get("cants_str_saved", ""))
    prev_piezas_ids = list(st.session_state.get("piezas_dict", {}).keys()) if isinstance(st.session_state.get("piezas_dict", None), dict) else []
    prev_extras_len = len(st.session_state.get("lista_extras_grabados", [])) if isinstance(st.session_state.get("lista_extras_grabados", None), list) else 0
    prev_emb_len = len(st.session_state.get("embalajes", [])) if isinstance(st.session_state.get("embalajes", None), list) else 0
    prev_ext_len = len(st.session_state.get("externos", [])) if isinstance(st.session_state.get("externos", None), list) else 0

    st.session_state.brf = str(di.get("brf", st.session_state.brf))
    st.session_state.version_presupuesto = str(di.get("version", di.get("version_presupuesto", st.session_state.get("version_presupuesto", ""))))
    st.session_state.comercial_1 = str(di.get("comercial_1", st.session_state.get("comercial_1", "")))
    st.session_state.comercial_2 = str(di.get("comercial_2", st.session_state.get("comercial_2", "")))
    st.session_state.cli = str(di.get("cli", st.session_state.cli))
    st.session_state.desc = str(di.get("desc", st.session_state.desc))
    st.session_state.notas = str(di.get("notas", st.session_state.get("notas","")))
    if isinstance(di.get("cants_str", None), str):
        st.session_state.cants_str_saved = di["cants_str"]

    manip = di.get("manip", {})
    if isinstance(manip, dict):
        if "unidad_t" in manip:
            st.session_state.unidad_t = str(manip["unidad_t"])
        if "t_input" in manip:
            st.session_state.t_input = float(manip["t_input"])

        # ✅ Opcionales (compatibles hacia atrás)
        rell = manip.get("rellenado", {})
        if isinstance(rell, dict):
            if "enabled" in rell:
                st.session_state.rell_enabled = bool(rell.get("enabled", False))
            if "t_input" in rell:
                st.session_state.rell_t_input = float(rell.get("t_input", 0.0))
        arm = manip.get("armado", {})
        if isinstance(arm, dict):
            if "enabled" in arm:
                st.session_state.arm_enabled = bool(arm.get("enabled", False))
            if "t_input" in arm:
                st.session_state.arm_t_input = float(arm.get("t_input", 0.0))

    # ✅ FIX: al importar, limpiamos keys de widgets globales para que Streamlit no
    # fuerce valores antiguos (p.ej. preset dificultad "standard").
    for _k in ("dif_preset_sel", "dif_ud", "repeticion_proyecto", "imp_fijo_pvp"):
        if _k in st.session_state:
            del st.session_state[_k]

    st.session_state.dif_ud = 0.091
    st.session_state.repeticion_proyecto = False
    st.session_state.imp_fijo_pvp = 500.0

    params = di.get("params", {})
    if isinstance(params, dict):
        if "dif_ud" in params: st.session_state.dif_ud = float(params["dif_ud"])
        # ✅ Importar también el preset visible (para que no vuelva a "standard" por culpa del widget)
        if "dif_preset_sel" in params:
            st.session_state.dif_preset_sel = str(params.get("dif_preset_sel", ""))
        else:
            # Compat: si no viene, intentamos inferirlo a partir de dif_ud
            try:
                _v = float(st.session_state.dif_ud)
            except Exception:
                _v = 0.091
            _presets = [("0,000", 0.0), ("0,020", 0.02), ("0,050", 0.05), ("0,091 (standard)", 0.091), ("0,120", 0.12), ("0,150", 0.15)]
            _label = "Personalizado"
            for _l, _vv in _presets:
                if abs(float(_vv) - float(_v)) < 1e-9:
                    _label = _l
                    break
            st.session_state.dif_preset_sel = _label

        if "repeticion_proyecto" in params:
            st.session_state.repeticion_proyecto = bool(params.get("repeticion_proyecto", False))
        if "imp_fijo_pvp" in params: st.session_state.imp_fijo_pvp = float(params["imp_fijo_pvp"])
        # Si es repetición de proyecto, el desarrollo se anula.
        if bool(st.session_state.get("repeticion_proyecto", False)):
            st.session_state.imp_fijo_pvp = 0.0
        if "margen" in params: st.session_state.margen = float(params["margen"])
        # ✅ Lock: al importar, no auto-ajustar margen en el primer render (evita diferencias de precio tras importar)
        st.session_state._import_lock_margen = True
        # Evita que el autómata interprete el margen importado como "auto" del proyecto anterior
        try:
            st.session_state.last_auto_margen = float("nan")
        except Exception:
            st.session_state.last_auto_margen = -999999.0
        # ✅ Nuevos (compatibles hacia atrás)
        if "descuento_procesos" in params: st.session_state.descuento_procesos = float(params["descuento_procesos"])
        if "margen_extras" in params: st.session_state.margen_extras = float(params["margen_extras"])
        if "margen_embalajes" in params: st.session_state.margen_embalajes = float(params["margen_embalajes"])


    if isinstance(di.get("db_precios", None), dict):
        # Importamos SIEMPRE la base de precios del proyecto (compatibilidad hacia atrás)
        st.session_state.db_precios = deepcopy(di["db_precios"])
        _completar_tarifas_editables(st.session_state.db_precios)
        # Anadir nuevas familias a proyectos historicos sin modificar sus tarifas guardadas.
        _import_planchas = st.session_state.db_precios.setdefault("planchas", {})
        if isinstance(_import_planchas, dict):
            for _nombre, _tarifas in PRECIOS_BASE["planchas"].items():
                _import_planchas.setdefault(_nombre, deepcopy(_tarifas))

        # ✅ Aviso de tarifa: si el proyecto importado trae materia prima distinta a la tarifa actual
        try:
            st.session_state._tarifa_mp_import_hash = _hash_materia_prima(st.session_state.db_precios)
            st.session_state._tarifa_mp_mismatch = (st.session_state._tarifa_mp_import_hash != _hash_materia_prima(PRECIOS_BASE))
        except Exception:
            st.session_state._tarifa_mp_import_hash = None
            st.session_state._tarifa_mp_mismatch = False
    else:
        # JSON antiguo sin db_precios: usamos la tarifa actual, pero dejamos flags coherentes
        st.session_state.db_precios = deepcopy(PRECIOS_BASE)
        st.session_state._tarifa_mp_import_hash = None
        st.session_state._tarifa_mp_mismatch = False
    st.session_state._import_sin_tarifas = not isinstance(di.get("db_precios"), dict)

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

    # ✅ Snapshots de costes (para preservar proyectos antiguos con precios vendidos)
    if isinstance(di.get("compras_legible", None), dict):
        st.session_state._imported_compras_legible = di["compras_legible"]
    if isinstance(di.get("resumen_costes", None), dict):
        st.session_state._imported_resumen_costes = di["resumen_costes"]


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
        # Compatibilidad robusta:
        # - Legacy: {"1000": 250, "1500": 250}
        # - Nuevo: {"1": {"1000": {"cara": 100, "dorso": 0}}}
        # - Mixto: ambos formatos a la vez (muy habitual en JSON antiguos exportados por versiones intermedias).
        #
        # IMPORTANTE:
        # Antes se decidía entre "todo nuevo" o "todo legacy" con all(isinstance(v, dict)).
        # Si venía mixto, intentaba hacer int(dict) y fallaba al importar.
        mi = di.get("mermas_imp", {})
        out = {}
        for k, v in mi.items():
            k_str = str(k)

            if isinstance(v, dict):
                # Tratamos la clave como ID de forma/pieza.
                pid_key = k_str
                out.setdefault(pid_key, {})
                for qk, vv in v.items():
                    q_key = str(qk)
                    if isinstance(vv, dict):
                        out[pid_key][q_key] = {
                            "cara": _coerce_int(vv.get("cara", 0), 0),
                            "dorso": _coerce_int(vv.get("dorso", 0), 0),
                        }
                    else:
                        val = _coerce_int(vv, 0)
                        out[pid_key][q_key] = {"cara": val, "dorso": val}
            else:
                # Legacy global por cantidad. Solo aceptamos claves numéricas.
                if k_str.isdigit():
                    out[k_str] = _coerce_int(v, 0)

        st.session_state.mermas_imp_manual = out

    if isinstance(di.get("mermas_imp_digital", None), dict):
        # Digital sigue siendo global por cantidad; ignoramos cualquier estructura no numérica.
        out_dig = {}
        for k, v in di["mermas_imp_digital"].items():
            k_str = str(k)
            if k_str.isdigit() and not isinstance(v, dict):
                out_dig[int(k_str)] = _coerce_int(v, 0)
        st.session_state.mermas_imp_digital_manual = out_dig

    if isinstance(di.get("mermas_proc", None), dict):
        # Compatibilidad robusta:
        # - Legacy: {"1000": 50, "1500": 50}
        # - Nuevo: {"1": {"1000": 60, "1500": 60}}
        # - Mixto: ambos formatos a la vez.
        mp = di.get("mermas_proc", {})
        out = {}
        for k, v in mp.items():
            k_str = str(k)

            if isinstance(v, dict):
                pid_key = k_str
                out.setdefault(pid_key, {})
                for qk, vv in v.items():
                    if isinstance(vv, dict):
                        # Tolerancia por si alguna versión guardó cara/dorso por error.
                        val = _coerce_int(vv.get("valor", vv.get("proc", vv.get("cara", 0))), 0)
                    else:
                        val = _coerce_int(vv, 0)
                    out[pid_key][str(qk)] = val
            else:
                if k_str.isdigit():
                    out[k_str] = _coerce_int(v, 0)

        st.session_state.mermas_proc_manual = out
# Impresiones por cantidad (multi-tirada) - opcional en JSON
    if isinstance(di.get("impresiones_by_qty", None), dict):
        cfg_new = {}
        for k, v in di["impresiones_by_qty"].items():
            try:
                qk = int(k)
            except Exception:
                continue
            if not isinstance(v, dict):
                continue
            try:
                n = int(v.get("n", 1))
            except Exception:
                n = 1
            n = max(1, n)
            modo = str(v.get("modo", "igual")).lower().strip()
            partes = v.get("partes", [])
            if isinstance(partes, list):
                try:
                    partes = [int(x) for x in partes if int(x) > 0]
                except Exception:
                    partes = []
            else:
                partes = []
            if n == 1:
                modo = "igual"
                partes = [qk]
            elif modo == "manual" and (not partes or sum(partes) != qk or len(partes) != n):
                # Normalizamos a reparto igual si el manual no cuadra
                modo = "igual"
                partes = _split_equal(qk, n)
            elif modo != "manual":
                partes = _split_equal(qk, n)
            cfg_new[str(qk)] = {"n": n, "modo": modo, "partes": partes}
        st.session_state.impresiones_by_qty = cfg_new


    # Impresiones por cantidad (multi-tirada) - POR FORMATO (nuevo, opcional en JSON)
    if isinstance(di.get("impresiones_by_qty_fmt", None), dict):
        cfg_fmt_new = {}
        for pid_k, cfg_pid in di["impresiones_by_qty_fmt"].items():
            try:
                pid_int = int(pid_k)
            except Exception:
                continue
            if not isinstance(cfg_pid, dict):
                continue
            cfg_q_new = {}
            for k, v in cfg_pid.items():
                try:
                    qk = int(k)
                except Exception:
                    continue
                if not isinstance(v, dict):
                    continue
                try:
                    n = int(v.get("n", 1))
                except Exception:
                    n = 1
                n = max(1, n)
                modo = str(v.get("modo", "igual")).lower().strip()
                partes = v.get("partes", [])
                if isinstance(partes, list):
                    try:
                        partes = [int(x) for x in partes if int(x) > 0]
                    except Exception:
                        partes = []
                else:
                    partes = []
                if n == 1:
                    modo = "igual"
                    partes = [qk]
                elif modo == "manual" and (not partes or sum(partes) != qk or len(partes) != n):
                    modo = "igual"
                    partes = _split_equal(qk, n)
                elif modo != "manual":
                    partes = _split_equal(qk, n)
                cfg_q_new[str(qk)] = {"n": n, "modo": modo, "partes": partes}
            cfg_fmt_new[str(pid_int)] = cfg_q_new
        st.session_state.impresiones_by_qty_fmt = cfg_fmt_new

    if isinstance(di.get("impresiones_by_qty_fmt_enabled", None), dict):
        en_new = {}
        for k, v in di["impresiones_by_qty_fmt_enabled"].items():
            try:
                pid_int = int(k)
            except Exception:
                continue
            en_new[str(pid_int)] = bool(v)
        st.session_state.impresiones_by_qty_fmt_enabled = en_new

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
            try:
                upc = int(float(e.get("uds_por_caja", e.get("uds_caja", e.get("unidades_por_caja", 1))) or 1))
            except Exception:
                upc = 1
            base["uds_por_caja"] = max(1, int(upc))
            dims_in = e.get("dims", {}) if isinstance(e.get("dims", None), dict) else {}
            # ✅ Import robusto de dimensiones (compat JSON antiguos):
            # - Acepta claves en dims: "L","W","H" o en minúscula ("l","w","h").
            # - Acepta claves planas en el embalaje: L/W/H o largo/ancho/alto.
            def _get_dim(_k: str, _aliases: list[str]):
                for kk in [_k, _k.lower(), *_aliases]:
                    if kk in dims_in:
                        return _coerce_float(dims_in.get(kk, 0.0), 0.0)
                    if kk in e:
                        return _coerce_float(e.get(kk, 0.0), 0.0)
                return 0.0
            base["dims"] = {
                "L": _get_dim("L", ["largo", "LARGO", "len", "length"]),
                "W": _get_dim("W", ["ancho", "ANCHO", "wid", "width"]),
                "H": _get_dim("H", ["alto", "ALTO", "hei", "height"]),
            }
            if isinstance(e.get("costes", None), dict):
                costes_new = {}
                for k, v in e["costes"].items():
                    try:
                        kk = int(float(k))
                    except Exception:
                        continue
                    try:
                        vv = float(v)
                    except Exception:
                        vv = 0.0
                    costes_new[kk] = vv
                base["costes"] = costes_new
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

    # Comercial: exportamos el número si es interpretable (p.ej. "Comercial 52" -> "52").
    # Mantiene compatibilidad: si no se puede interpretar, se exporta el texto tal cual.
    _c1_raw = st.session_state.get("comercial_1", "")
    _c2_raw = st.session_state.get("comercial_2", "")
    _c1_num = _parse_comercial_num(_c1_raw)
    _c2_num = _parse_comercial_num(_c2_raw)

    c1_out = (str(_c1_num) if _c1_num is not None else str(_c1_raw or ""))
    c2_out = (str(_c2_num) if _c2_num is not None else str(_c2_raw or ""))

    data = {
        "brf": st.session_state.brf,
        "version": st.session_state.get("version_presupuesto", ""),
        "comercial_1": c1_out,
        "comercial_2": c2_out,
        "cli": st.session_state.cli,
        "desc": st.session_state.desc,
        "notas": st.session_state.get("notas",""),
        "_schema": {"app": "MAINSA ADMIN V45", "piezas_index_base": 1},
        "cants_str": st.session_state.cants_str_saved,
        "manip": {"unidad_t": st.session_state.unidad_t, "t_input": float(st.session_state.t_input), "rellenado": {"enabled": bool(st.session_state.rell_enabled), "t_input": float(st.session_state.rell_t_input)}, "armado": {"enabled": bool(st.session_state.arm_enabled), "t_input": float(st.session_state.arm_t_input)}},
        "params": {"dif_ud": float(st.session_state.dif_ud), "dif_preset_sel": str(st.session_state.get("dif_preset_sel","")), "repeticion_proyecto": bool(st.session_state.get("repeticion_proyecto", False)), "imp_fijo_pvp": float(st.session_state.imp_fijo_pvp), "margen": float(st.session_state.margen), "descuento_procesos": float(st.session_state.descuento_procesos), "margen_extras": float(st.session_state.margen_extras), "margen_embalajes": float(st.session_state.margen_embalajes)},
        "db_precios": deepcopy(st.session_state.db_precios),
        "db_descuentos": deepcopy(st.session_state.db_descuentos),
        "piezas": piezas_out,
        "extras": deepcopy(st.session_state.lista_extras_grabados),
        "embalajes": deepcopy(st.session_state.embalajes),
        "externos": deepcopy(st.session_state.externos),
        "mermas_imp": deepcopy(st.session_state.mermas_imp_manual),
        "mermas_imp_digital": deepcopy(st.session_state.mermas_imp_digital_manual),
        "mermas_proc": deepcopy(st.session_state.mermas_proc_manual),
        "impresiones_by_qty": deepcopy(st.session_state.get("impresiones_by_qty", {})),
        "impresiones_by_qty_fmt": deepcopy(st.session_state.get("impresiones_by_qty_fmt", {})),
        "impresiones_by_qty_fmt_enabled": deepcopy(st.session_state.get("impresiones_by_qty_fmt_enabled", {})),
    }
    if resumen_compra is not None:
        data["compras_legible"] = resumen_compra
    if resumen_costes is not None:
        data["resumen_costes"] = resumen_costes
    return data

# =========================================================
# EXPORT JSON (ROBUSTO): SIEMPRE ÚLTIMO ESTADO + TICK ESTABLE
# =========================================================
def _compute_export_payload() -> tuple[dict, str]:
    """Construye el dict de export + devuelve (export_data, export_hash).
    - Usa los snapshots importados si todavía no hay cálculo (misma lógica que venías usando).
    - Hash estable para no resetear el tick al descargar oferta u otras acciones.
    """
    resumen_compra_export = st.session_state.get("compras_legible_export", None)
    resumen_costes_export = st.session_state.get("resumen_costes_export", None)

    resumen_compra_to_export = resumen_compra_export if isinstance(resumen_compra_export, dict) and len(resumen_compra_export) > 0 else st.session_state.get("_imported_compras_legible")
    resumen_costes_to_export = resumen_costes_export if isinstance(resumen_costes_export, dict) and len(resumen_costes_export) > 0 else st.session_state.get("_imported_resumen_costes")

    export_data = construir_export(
        resumen_compra=resumen_compra_to_export,
        resumen_costes=resumen_costes_to_export
    )

    # Hash estable (sin indent) para detectar cambios reales
    try:
        blob_compact = json.dumps(export_data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    except Exception:
        blob_compact = str(export_data)

    export_hash = hashlib.sha256(blob_compact.encode("utf-8")).hexdigest()
    return export_data, export_hash


def _refresh_export_cache_if_needed(force: bool = False) -> None:
    """Refresca st.session_state._export_blob solo si ha cambiado (por hash).
    Así el JSON es 100% fiable y el tick de "JSON descargado" no se cae por otras descargas.
    """
    if "_export_hash" not in st.session_state:
        st.session_state._export_hash = None

    export_data, export_hash = _compute_export_payload()

    if force or (st.session_state._export_hash != export_hash) or (st.session_state.get("_export_blob") is None):
        st.session_state._export_blob = json.dumps(export_data, indent=4, ensure_ascii=False)
        st.session_state._export_hash = export_hash
        # Si cambia el contenido, el tick vuelve a "pendiente"
        st.session_state._json_downloaded = False
        st.session_state._json_downloaded_filename = ""

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

# =========================================================
# BIBLIOTECA JSON · CARPETA SINCRONIZADA DE ONEDRIVE
# =========================================================
_OD_ROOT = Path(os.environ.get("MAINSA_JSON_DIR") or (
    Path(os.environ.get("OneDriveCommercial") or os.environ.get("OneDrive") or
         (Path.home() / "OneDrive - MAINSA PUNTO DIRECTO PLV S.L")) / "ESCANDALLOS MAINSA"))


def _od_normalizar(texto):
    return "".join(c for c in unicodedata.normalize("NFD", str(texto).casefold())
                   if unicodedata.category(c) != "Mn")


def _od_ruta_segura(raiz, relativo=""):
    raiz = Path(raiz).resolve()
    ruta = (raiz / relativo).resolve()
    if not ruta.is_relative_to(raiz):
        raise ValueError("La ruta debe estar dentro de la carpeta de escandallos.")
    return ruta


@st.cache_data(ttl=60, show_spinner=False)
def _od_inventario(raiz):
    raiz = Path(raiz).resolve()
    if not raiz.is_dir():
        raise FileNotFoundError("No se encuentra la carpeta sincronizada ESCANDALLOS MAINSA.")
    archivos, carpetas, errores = [], {"."}, []
    def error(exc):
        errores.append(str(exc))
    for directorio, subdirs, nombres in os.walk(raiz, followlinks=False, onerror=error):
        # Los marcadores de nube de OneDrive no son enlaces simbólicos.
        # Se excluyen enlaces de sistema que puedan salir de la biblioteca.
        seguras = []
        for nombre_subdir in subdirs:
            try:
                candidato = Path(directorio) / nombre_subdir
                if not candidato.is_symlink():
                    _od_ruta_segura(raiz, candidato)
                    seguras.append(nombre_subdir)
            except (OSError, ValueError) as exc:
                errores.append(str(exc))
        subdirs[:] = seguras
        carpetas.add(str(Path(directorio).relative_to(raiz)))
        for nombre in nombres:
            if not nombre.casefold().endswith(".json"):
                continue
            ruta = Path(directorio) / nombre
            try:
                if ruta.is_symlink():
                    continue
                ruta = _od_ruta_segura(raiz, ruta)
                stat = ruta.stat()
                archivos.append({"ruta": str(ruta.relative_to(raiz)), "nombre": nombre,
                                 "modificado": stat.st_mtime, "bytes": stat.st_size})
            except (OSError, ValueError) as exc:
                errores.append(f"{nombre}: {exc}")
    archivos.sort(key=lambda x: (-x["modificado"], x["ruta"].casefold()))
    return archivos, sorted(carpetas, key=str.casefold), errores


def _od_buscar(archivos, consulta):
    terminos = _od_normalizar(consulta).split()
    return [a for a in archivos if all(t in _od_normalizar(a["ruta"]) for t in terminos)]


def _od_validar_proyecto(datos):
    if not isinstance(datos, dict):
        raise ValueError("El archivo no contiene un proyecto JSON de MAINSA.")
    piezas = datos.get("piezas")
    if not isinstance(piezas, (dict, list)) or not piezas:
        raise ValueError("El JSON no contiene formas de un escandallo MAINSA.")
    valores = piezas.values() if isinstance(piezas, dict) else piezas
    if not all(isinstance(p, dict) for p in valores):
        raise ValueError("El JSON contiene formas con un formato no válido.")
    return datos


def _od_leer(raiz, relativo):
    ruta = _od_ruta_segura(raiz, relativo)
    if ruta.suffix.casefold() != ".json" or not ruta.is_file():
        raise ValueError("Selecciona un archivo JSON de la biblioteca.")
    if ruta.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("El JSON supera 64 MB; revisa el archivo antes de abrirlo.")
    contenido = ruta.read_bytes()
    return _od_validar_proyecto(json.loads(contenido.decode("utf-8-sig"))), hashlib.sha256(contenido).hexdigest()


def _od_nombre(nombre):
    nombre = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(nombre)).strip().rstrip(". ")
    if not nombre.casefold().endswith(".json"):
        nombre += ".json"
    stem = nombre[:-5].rstrip(". ")
    if not stem or stem in (".", ".."):
        raise ValueError("Escribe un nombre para el JSON.")
    if stem.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}:
        raise ValueError("Ese nombre está reservado en Windows. Elige otro nombre.")
    if len(stem) > 180:
        raise ValueError("Acorta el nombre del archivo a un máximo de 180 caracteres.")
    return stem + ".json"


def _od_guardar(raiz, carpeta, nombre, contenido):
    """Crea y verifica un archivo local exclusivo. No acredita la sincronización en nube."""
    _od_validar_proyecto(json.loads(contenido))
    destino = _od_ruta_segura(raiz, carpeta)
    if not destino.is_dir():
        raise FileNotFoundError("La carpeta de destino ya no está disponible.")
    nombre = _od_nombre(nombre)
    stem = nombre[:-5]
    prefijo = re.sub(r"_REV\d+$", "", stem, flags=re.I)
    blob = contenido.encode("utf-8")
    for numero in range(10001):
        candidato = nombre if numero == 0 else f"{prefijo}_REV{numero}.json"
        ruta = _od_ruta_segura(raiz, destino / candidato)
        try:
            archivo = ruta.open("xb")
        except FileExistsError:
            continue
        try:
            with archivo:
                archivo.write(blob)
                archivo.flush()
                os.fsync(archivo.fileno())
        except Exception:
            ruta.unlink(missing_ok=True)
            raise
        if hashlib.sha256(ruta.read_bytes()).digest() != hashlib.sha256(blob).digest():
            raise OSError("No se ha podido verificar el archivo guardado. Revisa la carpeta antes de repetir.")
        return ruta
    raise FileExistsError("Hay demasiadas revisiones con ese nombre. Elige otro nombre.")


def _od_mostrar_buscador():
    with st.expander("☁️ Buscar JSON en OneDrive", expanded=False):
        st.caption("Biblioteca: ESCANDALLOS MAINSA · carpeta sincronizada de OneDrive")
        aviso = st.session_state.pop("_od_apertura_ok", None)
        if aviso:
            st.success(aviso)
        if st.button("🔄 Actualizar archivos", key="od_actualizar"):
            _od_inventario.clear()
        try:
            archivos, carpetas, errores = _od_inventario(str(_OD_ROOT))
        except (OSError, ValueError) as exc:
            st.warning(f"La biblioteca no está disponible: {exc}")
            st.caption(f"Carpeta esperada: {_OD_ROOT}")
            return
        consulta = st.text_input("Buscar referencia, cliente o descripción", key="od_busqueda",
                                 placeholder="Ej.: 81225 Ferrero")
        encontrados = _od_buscar(archivos, consulta)
        st.caption(f"{len(encontrados)} JSON encontrados · ordenados del más reciente al más antiguo")
        if errores:
            st.warning("Algunos archivos o subcarpetas no se pudieron consultar. Comprueba el acceso a OneDrive.")
        if not encontrados:
            st.info("No hay JSON que coincidan con la búsqueda.")
            return
        consulta_clave = _od_normalizar(consulta)
        paginas = max(1, math.ceil(len(encontrados) / 50))
        if st.session_state.get("_od_ultima_busqueda") != consulta_clave or st.session_state.get("od_pagina", 1) > paginas:
            st.session_state.od_pagina = 1
        st.session_state._od_ultima_busqueda = consulta_clave
        pagina = int(st.number_input("Página de resultados", min_value=1, max_value=paginas,
                                     value=1, step=1, key="od_pagina")) if paginas > 1 else 1
        tramo = encontrados[(pagina - 1) * 50:pagina * 50]
        opciones = [a["ruta"] for a in tramo]
        if st.session_state.get("od_seleccion") not in opciones:
            st.session_state.od_seleccion = opciones[0]
        elegido = st.selectbox("JSON encontrados", opciones, key="od_seleccion")
        meta = next(a for a in tramo if a["ruta"] == elegido)
        fecha = datetime.fromtimestamp(meta["modificado"]).strftime("%d/%m/%Y %H:%M")
        st.caption(f"Modificado: {fecha} · {meta['bytes'] / 1024:.1f} KB")
        st.caption("Abrir sustituye el proyecto en pantalla. Guarda antes los cambios que quieras conservar.")
        if st.button("📂 Abrir JSON seleccionado", key="od_abrir"):
            try:
                with st.spinner("Abriendo el proyecto de OneDrive…"):
                    datos, firma = _od_leer(_OD_ROOT, elegido)
                    normalizar_import(datos)
                st.session_state._last_import_hash = firma
                st.session_state._od_origen = elegido
                st.session_state._od_carpeta_abierta = str(Path(elegido).parent)
                st.session_state._od_apertura_ok = f"Proyecto abierto: {Path(elegido).name}"
                # Cambia la identidad del uploader para que un archivo local anterior no vuelva a importarse.
                st.session_state._od_uploader_generacion = int(st.session_state.get("_od_uploader_generacion", 0)) + 1
                for clave in ("od_guardar_carpeta", "od_guardar_nombre", "_od_nombre_sugerido"):
                    st.session_state.pop(clave, None)
                st.rerun()
            except (OSError, ValueError, TypeError, KeyError) as exc:
                st.error(f"No se pudo abrir el JSON: {exc}")
                st.caption("Si el archivo está solo en la nube, comprueba que OneDrive esté conectado.")


def _od_mostrar_guardado():
    with st.sidebar.expander("☁️ Guardar JSON en OneDrive", expanded=True):
        st.caption("Guarda directamente en la carpeta sincronizada. Si el nombre existe, se crea una revisión nueva.")
        try:
            _, carpetas, _ = _od_inventario(str(_OD_ROOT))
        except (OSError, ValueError):
            st.warning("Conecta la carpeta ESCANDALLOS MAINSA de OneDrive para guardar aquí.")
            return
        abierto = st.session_state.get("_od_carpeta_abierta", ".")
        if st.session_state.get("od_guardar_carpeta") not in carpetas:
            st.session_state.od_guardar_carpeta = abierto if abierto in carpetas else carpetas[0]
        carpeta = st.selectbox("Carpeta de destino", carpetas, index=carpetas.index(abierto) if abierto in carpetas else 0,
                               format_func=lambda x: "ESCANDALLOS MAINSA" if x == "." else x, key="od_guardar_carpeta")
        sugerido = st.session_state.get("_export_filename") or "Escandallo.json"
        anterior = st.session_state.get("_od_nombre_sugerido")
        if anterior != sugerido:
            if st.session_state.get("od_guardar_nombre") in (None, anterior):
                st.session_state.od_guardar_nombre = sugerido
            st.session_state._od_nombre_sugerido = sugerido
        st.session_state.setdefault("od_guardar_nombre", sugerido)
        nombre = st.text_input("Nombre del JSON", key="od_guardar_nombre")
        cache = st.session_state.get("_calc_cache")
        listo = bool(isinstance(cache, dict) and cache.get("res_final") and
                     st.session_state.get("_calc_last_signature") == _calc_project_signature())
        if not listo:
            st.info("Pulsa 🧮 Calcular para guardar el proyecto con sus costes y auditoría actualizados.")
        if st.button("💾 Guardar nueva versión", key="od_guardar", disabled=not listo):
            try:
                datos, firma = _compute_export_payload()
                contenido = json.dumps(datos, indent=4, ensure_ascii=False)
                ruta = _od_guardar(_OD_ROOT, carpeta, nombre, contenido)
                _od_inventario.clear()
                st.session_state._od_ultimo_guardado = str(ruta)
                st.session_state._od_guardado_hash = firma
            except (OSError, ValueError, TypeError) as exc:
                st.error(f"No se pudo guardar el JSON: {exc}")
        if st.session_state.get("_od_guardado_hash") == st.session_state.get("_export_hash") and st.session_state.get("_od_ultimo_guardado"):
            st.success(f"Guardado y verificado en la carpeta OneDrive: {Path(st.session_state._od_ultimo_guardado).name}")
        st.caption("La subida a la nube la realiza OneDrive. Si está pausado o sin conexión, sincronizará al reanudarse.")


def _mark_json_download():
    """Marca en session_state que el JSON se ha descargado (para no olvidarse)."""
    st.session_state._json_downloaded = True
    st.session_state._json_downloaded_filename = st.session_state.get("_export_filename", "")

with st.sidebar:
    st.header("📦 JSON / Visualización")
    # 🌟 VISTA OFERTA siempre activa (sin toggle)
    st.session_state["modo_oferta"] = True
    modo_comercial = True
    st.caption("🌟 VISTA OFERTA activa")

    st.divider()

    # -----------------------------------------------------
    # 🧮 Cálculo manual (mejora rendimiento)
    # -----------------------------------------------------
    if st.button("🧮 Calcular", use_container_width=True, key="btn_calc_sidebar"):
        st.session_state._calc_requested = True
        st.session_state._calc_status = "Calculando…"
    st.caption(f"Estado cálculo: {st.session_state.get('_calc_status','Pendiente')}")

    try:
        _current_calc_signature = _calc_project_signature()
        _last_calc_signature = st.session_state.get("_calc_last_signature")
        _has_calc_cache = isinstance(st.session_state.get("_calc_cache"), dict)
        if _has_calc_cache and _last_calc_signature and _current_calc_signature != _last_calc_signature:
            st.warning("⚠️ Hay datos introducidos sin calcular. Pulsa 🧮 Calcular para actualizar oferta y JSON.")
        elif not _has_calc_cache:
            st.info("Pulsa 🧮 Calcular para generar la oferta y el JSON.")
    except Exception:
        pass

    # =========================================================
    # Aviso + botón (sidebar) sobre materia prima importada vs tarifa actual
    # =========================================================
    if st.session_state.get("_import_sin_tarifas", False):
        st.warning("El JSON no incluye db_precios: se usa la tarifa V45. No se pueden recuperar sus costes históricos.")
    if bool(st.session_state.get("_tarifa_mp_mismatch", False)):
        st.warning(
            "⚠️ Materia prima del proyecto ≠ tarifa actual. "
            "Puedes mantenerla (si ya enviaste oferta) o actualizar a tarifa vigente."
        )
        if st.button("🔁 Actualizar materia prima a tarifa actual", use_container_width=True, key="btn_update_mp_sidebar"):
            _aplicar_tarifa_actual_materia_prima()
            st.success("Materia prima actualizada a tarifa actual.")
        st.caption("Actualiza Cartoncillo, Planchas, Rígidos y Peliculado. Las familias históricas conservan su catálogo V44; para pasar a V45, elige expresamente una nueva familia y calidad. Después pulsa Calcular.")

    _od_mostrar_buscador()

    with st.expander("📥 Importar JSON", expanded=False):
        uploaded = st.file_uploader("Subir JSON", type=["json"], key=f"uploader_json_{st.session_state.get('_od_uploader_generacion', 0)}")
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

# =========================================================
# PESTAÑAS (SIEMPRE ADMIN)
# =========================================================
def _aud_importe(valor, decimales=2):
    return f"{float(valor):,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def _aud_linea(lineas, concepto, grupo, consumo, unidad, tarifa, descuento, coste, detalle=""):
    """Registra operandos y resultado del motor en el momento del cálculo."""
    linea = {"Concepto": str(concepto), "Grupo": grupo, "Consumo": float(consumo),
             "Unidad": unidad, "Tarifa (€)": float(tarifa), "Descuento (%)": float(descuento),
             "Coste neto (€)": float(coste), "Detalle": str(detalle)}
    lineas.append(linea)
    return linea


def _aud_tabla(lineas, key, cantidad=None):
    if not lineas:
        st.caption("Sin partidas para este apartado.")
        return
    tabla = pd.DataFrame(lineas).drop(columns=["Grupo"], errors="ignore")
    if cantidad:
        tabla["€/expositor"] = tabla["Coste neto (€)"] / float(cantidad)
    for col in ("Tarifa (€)", "Coste neto (€)", "€/expositor"):
        if col in tabla:
            tabla[col] = tabla[col].map(lambda x: _aud_importe(x, 4 if col != "Coste neto (€)" else 2))
    if "Consumo" in tabla:
        tabla["Consumo"] = tabla["Consumo"].map(lambda x: f"{x:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".").rstrip("0").rstrip(","))
    if "Descuento (%)" in tabla:
        tabla["Descuento (%)"] = tabla["Descuento (%)"].map(lambda x: f"{x:g} %")
    orden = [c for c in ("Concepto", "Consumo", "Unidad", "Tarifa (€)", "Descuento (%)", "Coste neto (€)", "€/expositor", "Detalle") if c in tabla]
    st.dataframe(tabla[orden], hide_index=True, use_container_width=True,
                 height=min(38 + 36 * len(tabla), 900), key=key)


def _aud_por_cantidad(datos, cantidad):
    if not isinstance(datos, dict):
        return {}
    return datos.get(cantidad, datos.get(str(cantidad), {})) or {}


def _mostrar_auditoria_compras(compras, resumen):
    st.subheader("🧾 Auditoría de compras")
    st.caption("Costes internos del proyecto · importes netos de compra y producción · opcionales separados")
    cache = st.session_state.get("_calc_cache")
    es_calculo = isinstance(cache, dict) and bool(compras)
    if not es_calculo:
        compras = st.session_state.get("_imported_compras_legible") or {}
        resumen = st.session_state.get("_imported_resumen_costes") or {}
    cantidades = sorted({int(k) for k in compras if str(k).isdigit() and int(k) > 0})
    if not cantidades:
        st.info("Pulsa 🧮 Calcular para ver los costes por forma y las demás partidas del proyecto.")
        return
    # El selector utiliza las cantidades calculadas, nunca las entradas aún sin calcular.
    if st.session_state.get("aud_compras_qty") not in cantidades:
        st.session_state.pop("aud_compras_qty", None)
    cantidad = st.selectbox("Cantidad de expositores a revisar", cantidades, key="aud_compras_qty")
    comp = _aud_por_cantidad(compras, cantidad)
    audit = comp.get("Auditoría compras") or {}
    res = _aud_por_cantidad(resumen, cantidad)
    firma = audit.get("firma") or (st.session_state.get("_calc_last_signature") if es_calculo else None)
    pendiente = bool(firma and firma != _calc_project_signature())
    if pendiente:
        st.warning("Hay cambios pendientes de calcular. Esta auditoría conserva los costes, formas y tarifas del último cálculo. Pulsa 🧮 Calcular para actualizarla.")
    if not es_calculo:
        st.info("Se muestran los costes guardados en el JSON importado.")
    if not audit:
        st.warning("Este proyecto conserva un desglose antiguo sin consumos ni tarifas registrados. Puedes consultar sus costes guardados; pulsa 🧮 Calcular para generar la auditoría completa con las tarifas del proyecto.")
        detalle = comp.get("Detalle piezas", [])
        if detalle:
            st.dataframe(pd.DataFrame(detalle), hide_index=True, use_container_width=True)
        with st.expander("Materiales, procesos y partidas guardadas"):
            st.json({k: v for k, v in comp.items() if k != "Detalle piezas"})
        return
    formas = audit.get("formas", [])
    otras = audit.get("otras_partidas", [])
    total_formas = sum(float(f["coste_total"]) for f in formas)
    total_otras = sum(float(l["Coste neto (€)"]) for l in otras)
    total = float(audit["coste_total"])
    cabecera = audit.get("proyecto", {})
    st.caption(f"Briefing: {cabecera.get('briefing') or '—'} · Cliente: {cabecera.get('cliente') or '—'} · {cabecera.get('descripcion') or 'Sin descripción'}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Coste total del proyecto", _aud_importe(total))
    c2.metric("Coste por expositor", _aud_importe(total / cantidad, 4))
    c3.metric("Costes de las formas", _aud_importe(total_formas))
    st.markdown("### Costes por forma")
    filas = []
    avisos = list(audit.get("avisos", []))
    for forma in formas:
        materiales = sum(l["Coste neto (€)"] for l in forma["lineas"] if l["Grupo"] == "Material")
        procesos = sum(l["Coste neto (€)"] for l in forma["lineas"] if l["Grupo"] == "Proceso")
        filas.append({"Forma": f"{forma['id']} · {forma['nombre']}", "Formato (mm)": forma["formato"],
                      "Materiales (€)": materiales, "Procesos (€)": procesos,
                      "Total (€)": forma["coste_total"], "€/expositor": forma["coste_total"] / cantidad})
        diferencia = sum(l["Coste neto (€)"] for l in forma["lineas"]) - forma["coste_total"]
        if abs(diferencia) > 0.000001:
            avisos.append(f"Forma {forma['id']}: el detalle no coincide con su coste ({_aud_importe(diferencia, 4)}).")
        avisos.extend(f"Forma {forma['id']} · {x}" for x in forma.get("avisos", []))
    if filas:
        tabla = pd.DataFrame(filas)
        for col in ("Materiales (€)", "Procesos (€)", "Total (€)", "€/expositor"):
            tabla[col] = tabla[col].map(lambda x: _aud_importe(x, 4 if col == "€/expositor" else 2))
        st.dataframe(tabla, hide_index=True, use_container_width=True, key="aud_compras_formas")
    for forma in formas:
        with st.expander(f"Forma {forma['id']} · {forma['nombre']} · {forma['formato']} mm · {_aud_importe(forma['coste_total'])}", expanded=len(formas) == 1):
            st.caption(f"Pliegos/expositor: {forma['pliegos']:g} · Hojas netas: {forma['hojas_netas']} · Merma de proceso: {forma['merma_proceso']} · Hojas de producción: {forma['hojas_produccion']} · Tiradas: {forma['tiradas']}")
            st.caption(f"Merma de impresión cara: {forma['merma_cara']} hojas/tirada · dorso: {forma['merma_dorso']} hojas/tirada · Pisadas de corte/stamping: {forma['pisadas']}")
            _aud_tabla(forma["lineas"], f"aud_lineas_{cantidad}_{forma['id']}")
            st.caption("Consumos con las mermas aplicadas. El coste neto ya incorpora el descuento mostrado. En offset, la tarifa es el importe por tinta calculado para las hojas de cada tirada.")
    st.markdown("### Otros costes del proyecto")
    _aud_tabla(otras, f"aud_otras_{cantidad}", cantidad)
    st.markdown("### Comprobación del total")
    diferencia = total_formas + total_otras - total
    st.write(f"Formas {_aud_importe(total_formas)} + otras partidas {_aud_importe(total_otras)} = {_aud_importe(total_formas + total_otras)}")
    if abs(diferencia) <= 0.000001:
        st.success("El desglose coincide con el coste total del cálculo. Diferencia: 0,00 €.")
    else:
        st.error(f"El desglose no coincide con el motor. Diferencia: {_aud_importe(diferencia, 4)}.")
    if res.get("totales"):
        diferencia_resumen = float(res["totales"].get("coste_total_compra_estimado", total)) - total
        if abs(diferencia_resumen) > 0.00011:
            st.error(f"El resumen de costes guardado difiere de esta auditoría en {_aud_importe(diferencia_resumen, 4)}.")
    if avisos:
        with st.expander(f"⚠️ Revisar {len(avisos)} observaciones", expanded=True):
            for aviso in dict.fromkeys(avisos):
                st.warning(aviso)
    opcionales = audit.get("opcionales", [])
    if opcionales:
        with st.expander("Opcionales separados · rellenado y armado"):
            _aud_tabla(opcionales, f"aud_opcionales_{cantidad}", cantidad)
            st.caption("Costes internos opcionales, fuera del total principal.")
    venta = audit.get("referencias_venta", [])
    if venta:
        with st.expander("Referencias de venta · fuera del coste de compra"):
            st.caption("Estos importes son de venta. No se suman al coste de esta auditoría.")
            tabla_venta = pd.DataFrame(venta)
            tabla_venta["Importe de venta (€)"] = tabla_venta["Importe de venta (€)"].map(_aud_importe)
            st.dataframe(tabla_venta, hide_index=True, use_container_width=True)
    with st.expander("Detalle técnico guardado del cálculo"):
        st.json(audit)


tab_calculadora, tab_costes, tab_auditoria = st.tabs(["🧮 Calculadora", "💰 Base de Datos", "🧾 Auditoría de compras"])

# =========================================================
# TAB COSTES (siempre visible)
# =========================================================
with tab_costes:
    st.caption("Edita las tarifas del proyecto. Se conservan al descargar su JSON y volver a importarlo. Después de cambiarlas, pulsa 🧮 Calcular.")
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
                        f"{k} (€/kg)", value=float(v["precio_kg"]), min_value=0.0, step=0.0001, format="%.4f", key=f"cost_cart_{k}"
                    )

        with st.expander("🧱 Ondulado (€/m²) y Rígidos (€/hoja)", expanded=True):
            st.session_state.db_descuentos["ondulado_rigidos"] = st.number_input(
                "Descuento bloque Ondulado + Rígidos (%)",
                min_value=0.0, max_value=100.0, step=0.5,
                value=float(st.session_state.db_descuentos.get("ondulado_rigidos", 0.0)),
                key="db_desc_or"
            )

            st.markdown("##### Ondulado · Costes base €/m² · Compras 28/10/2026")
            for k, v in db["planchas"].items():
                if k != "Ninguna":
                    st.markdown(f"**{k}**")
                    # ✅ 'peg' se gestiona en NARBA, aquí solo calidades de plancha
                    vv = {kk: sv for kk, sv in v.items() if kk != "peg"}
                    cols = st.columns(len(vv)) if vv else st.columns(1)
                    for idx, (sk, sv) in enumerate(vv.items()):
                        db["planchas"][k][sk] = cols[idx].number_input(
                            sk, value=float(sv), min_value=0.0, step=0.0001, format="%.4f", key=f"cost_pl_{k}_{sk}"
                        )

            st.markdown("---")
            st.markdown("##### Rígidos (Precio Hoja + Tamaño)")
            for k, v in db["rigidos"].items():
                if k != "Ninguno":
                    c1, c2, c3 = st.columns([3, 1, 1])
                    db["rigidos"][k]["precio_ud"] = c1.number_input(
                        f"{k} (€/hoja)", value=float(v["precio_ud"]), min_value=0.0, step=0.0001, format="%.4f", key=f"cost_rig_{k}"
                    )
                    db["rigidos"][k]["w"] = int(c2.number_input("w", value=int(v["w"]), key=f"rigw_{k}"))
                    db["rigidos"][k]["h"] = int(c3.number_input("h", value=int(v["h"]), key=f"righ_{k}"))

    with col_c2:
        with st.expander("✨ Acabados (otros)", expanded=True):
            # Laminado digital se mantiene aquí (no NARBA)
            db["laminado_digital"] = st.number_input(
                "Laminado Digital", value=float(db.get("laminado_digital", 3.5)), min_value=0.0, step=0.0001, format="%.4f", key="cost_lam_dig"
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

            db.setdefault("narba", {})
            db["narba"]["contracolado_a_mano_m2"] = st.number_input(
                "Contracolado a mano (€/m²)",
                value=float(db.get("narba", {}).get("contracolado_a_mano_m2", 0.6864)),
                key="cost_contracolado_a_mano_m2",
                format="%.4f"
            )

            st.markdown("---")
            st.markdown("##### Peliculado (€/m²)")
            for k, v in db["peliculado"].items():
                if k != "Sin Peliculado":
                    db["peliculado"][k] = st.number_input(f"{k}", value=float(v), min_value=0.0, step=0.0001, format="%.4f", key=f"cost_pel_{k}")

            st.markdown("---")
            st.markdown("##### Troquelado")
            for k, v in db["troquelado"].items():
                st.markdown(f"**{k}**")
                c_arr, c_tir = st.columns(2)
                db["troquelado"][k]["arranque"] = c_arr.number_input(
                    "Arranque (€)", value=float(v["arranque"]), min_value=0.0, step=0.0001, format="%.4f", key=f"trq_arr_{k}"
                )
                db["troquelado"][k]["tiro"] = c_tir.number_input(
                    "Tiro (€/hoja)", value=float(v["tiro"]), format="%.4f", key=f"trq_tir_{k}"
                )

        with st.expander("✂️ Plotter", expanded=True):
            db["plotter"]["precio_hoja"] = st.number_input(
                "Corte Plotter (€/hoja)", value=float(db["plotter"]["precio_hoja"]), min_value=0.0, step=0.0001, format="%.4f", key="plotter_precio"
            )

        with st.expander("✨ Stamping", expanded=True):
            for campo, etiqueta in (("pelicula_m2", "Película stamping (€/m²)"),
                                    ("pisada", "Pisada stamping (€/pisada)"),
                                    ("arreglo", "Arreglo stamping (€)")):
                db["stamping"][campo] = st.number_input(etiqueta, min_value=0.0,
                    value=float(db["stamping"][campo]), step=0.0001, format="%.4f", key=f"tarifa_stamping_{campo}")

        with st.expander("🖨️ Impresión y flexografía", expanded=True):
            campos = [
                ("impresion_digital", "precio_m2", "Impresión digital (€/m²)"),
                ("offset", "minimo_tinta", "Offset · mínimo hasta 100 hojas (€/tinta)"),
                ("offset", "extra_101_500", "Offset · extra hojas 101–500 (€/hoja/tinta)"),
                ("offset", "base_501_2000", "Offset · base 501–2000 hojas (€/tinta)"),
                ("offset", "extra_2001", "Offset · extra desde hoja 2001 (€/hoja/tinta)"),
                ("flexografia", "arreglo", "Arreglo flexografía (€/plancha)"),
            ]
            for categoria, campo, etiqueta in campos:
                db[categoria][campo] = st.number_input(etiqueta, min_value=0.0,
                    value=float(db[categoria][campo]), step=0.0001, format="%.4f", key=f"tarifa_{categoria}_{campo}")
            st.markdown("##### Tinta especial FR24 por forma")
            for pid, pieza in st.session_state.piezas_dict.items():
                pieza["fr24_rate"] = st.number_input(f"{pieza.get('nombre', f'Forma {pid}')} · FR24 (€/m²)",
                    min_value=0.0, value=float(pieza.get("fr24_rate", 0.05)),
                    step=0.0001, format="%.4f", key=f"fr24r_{pid}")

        with st.expander("👷 Mano de obra", expanded=True):
            for campo, etiqueta in (("manipulado_hora", "Manipulado (€/hora)"),
                                    ("rellenado_hora", "Rellenado (€/hora)"), ("armado_hora", "Armado (€/hora)")):
                db["mano_obra"][campo] = st.number_input(etiqueta, min_value=0.0,
                    value=float(db["mano_obra"][campo]), step=0.01, format="%.4f", key=f"tarifa_mano_obra_{campo}")

        with st.expander("📦 Tarifas de embalajes automáticos"):
            st.caption("Se mantienen las fórmulas de cada embalaje; puedes editar sus importes y coeficientes.")
            db["embalajes"]["multiplicador_dd"] = st.number_input("Multiplicador D/D",
                min_value=0.0, value=float(db["embalajes"]["multiplicador_dd"]),
                step=0.01, format="%.4f", key="tarifa_embalajes_multiplicador_dd")
            etiquetas = {"guaina": "Guaina", "plano": "En plano", "volumen": "En volumen", "aros": "Aros de refuerzo"}
            campos = {"arreglo": "Arreglo / coeficiente fijo (€)", "arreglo_m2": "Arreglo por superficie (€/m²)",
                      "precio_ud": "Importe por unidad (€/ud)", "precio_m2": "Importe por superficie (€/m²)",
                      "exponente": "Exponente de cantidad"}
            for bloque, titulo in etiquetas.items():
                st.markdown(f"**{titulo}**")
                for campo, valor in db["embalajes"][bloque].items():
                    db["embalajes"][bloque][campo] = st.number_input(campos.get(campo, campo),
                        min_value=0.0, value=float(valor), step=0.0001,
                        format="%.9f" if bloque == "aros" else "%.4f", key=f"tarifa_embalajes_{bloque}_{campo}")

    with col_c1:
        with st.expander("🧰 Materiales extra MAINSA"):
            st.caption("Tarifas para añadir nuevas partidas. Las partidas ya añadidas conservan su precio editable en Calculadora.")
            for nombre, valor in db["extras_base"].items():
                db["extras_base"][nombre] = st.number_input(f"{nombre} (€/ud compra)", min_value=0.0,
                    value=float(valor), step=0.0001, format="%.4f", key=f"tarifa_extras_{nombre}")
        with st.expander("🧩 Catálogo FLEXICO"):
            st.caption("Tarifas para nuevas partidas FLEXICO. Las partidas existentes conservan su precio de proyecto.")
            for codigo, valor in db["flexico"].items():
                descripcion = PRODUCTOS_FLEXICO.get(codigo, {}).get("desc", codigo)
                db["flexico"][codigo] = st.number_input(f"{codigo} · {descripcion} (€/ud compra)",
                    min_value=0.0, value=float(valor), step=0.0001, format="%.4f", key=f"tarifa_flexico_{codigo}")
        with st.expander("🗃️ Otras tarifas NARBA de referencia"):
            st.caption("Importes de referencia conservados en el JSON. El cálculo actual no los aplica como partidas adicionales.")
            for campo, etiqueta in (("peliculado_menor_50x70_hoja", "Peliculado menor de 50×70 (€/hoja)"),
                                    ("guillotina_impresion_corte", "Guillotina impresión (€/corte)"),
                                    ("guillotina_plancha_corte", "Guillotina plancha (€/corte)")):
                db["narba"][campo] = st.number_input(etiqueta, min_value=0.0,
                    value=float(db["narba"][campo]), step=0.0001, format="%.4f", key=f"tarifa_narba_{campo}")


# =========================================================
# TAB CALCULADORA
# =========================================================
with tab_calculadora:
    db = st.session_state.db_precios

    st.header("Paso 1 · Datos de oferta")

    cA, cB, cC = st.columns([2, 2, 3])
    with cA:
        st.text_input("Nº Briefing", key="brf")
        st.text_input("Versión presupuesto", key="version_presupuesto", placeholder="A, B, B2...")
        st.text_input("Nº Comercial 1", key="comercial_1")
        st.text_input("Nº Comercial 2 (opcional)", key="comercial_2")
        st.text_input("Cliente", key="cli")
        st.text_area("Notas / Comentarios", key="notas", height=180, placeholder="Escribe aquí notas internas o comentarios para incluir en la oferta comercial...")
        # ✅ Import safety: tras importar un JSON, no reescribimos el margen automáticamente en este primer render.
        if bool(st.session_state.get("_import_lock_margen", False)):
            st.session_state._import_lock_margen = False
        else:
            _aplicar_margen_auto_si_procede()
    with cB:
        st.text_input("Descripción", key="desc")
        st.text_input("Cantidades (ej: 500, 1000)", key="cants_str_saved")
    with cC:
        st.radio("Manipulación", ["Segundos", "Minutos"], horizontal=True, key="unidad_t")
        st.number_input("Tiempo/ud", min_value=0.0, value=float(st.session_state.t_input), step=1.0, key="t_input")

        st.markdown("**Opcionales (a parte)**")
        st.checkbox("Rellenado", value=bool(st.session_state.rell_enabled), key="rell_enabled")
        st.number_input("Tiempo/ud Rellenado", min_value=0.0, value=float(st.session_state.rell_t_input), step=1.0, key="rell_t_input", disabled=not bool(st.session_state.rell_enabled))
        st.checkbox("Armado", value=bool(st.session_state.arm_enabled), key="arm_enabled")
        st.number_input("Tiempo/ud Armado", min_value=0.0, value=float(st.session_state.arm_t_input), step=1.0, key="arm_t_input", disabled=not bool(st.session_state.arm_enabled))

        st.markdown("**Dificultad**")
        # Desplegable + editable: el desplegable aplica un valor rápido y el input permite afinarlo.
        _dif_presets = [
            ("0,000", 0.0),
            ("0,020", 0.02),
            ("0,050", 0.05),
            ("0,091 (standard)", 0.091),
            ("0,120", 0.12),
            ("0,150", 0.15),
            ("Personalizado", None),
        ]

        # Inicializa selección en base al valor actual si coincide con un preset
        _dif_actual = float(st.session_state.dif_ud)
        _dif_labels = [p[0] for p in _dif_presets]
        _dif_values = [p[1] for p in _dif_presets]

        _idx = None
        for i, v in enumerate(_dif_values):
            if v is None:
                continue
            if abs(float(v) - _dif_actual) < 1e-9:
                _idx = i
                break
        if _idx is None:
            _idx = _dif_labels.index("Personalizado")

        sel = st.selectbox("Preset dificultad", _dif_labels, index=_idx, key="dif_preset_sel")
        sel_val = _dif_presets[_dif_labels.index(sel)][1]
        if sel_val is not None:
            # Si eliges un preset, se aplica automáticamente
            st.session_state.dif_ud = float(sel_val)

        # Editable siempre (si está en preset, puedes ajustarlo manualmente igualmente)
        st.number_input("Dificultad (€/ud)", min_value=0.0, step=0.001, value=float(st.session_state.dif_ud), key="dif_ud")

        # Repetición de proyecto (fuera de Finanzas)
        st.checkbox("🔁 Repetición de proyecto", value=bool(st.session_state.get("repeticion_proyecto", False)), key="repeticion_proyecto")

    lista_cants = parse_cantidades(st.session_state.cants_str_saved)

    unidad_t = st.session_state.unidad_t
    t_input = float(st.session_state.t_input)
    seg_man_total = t_input * 60 if unidad_t == "Minutos" else t_input


    # Opcionales (a parte): mismas unidades que manipulación
    rell_t_input = float(st.session_state.rell_t_input)
    arm_t_input = float(st.session_state.arm_t_input)
    seg_rell_total = (rell_t_input * 60) if unidad_t == "Minutos" else rell_t_input
    seg_arm_total = (arm_t_input * 60) if unidad_t == "Minutos" else arm_t_input

    with st.expander("💰 Finanzas", expanded=False):
        # Si es repetición de proyecto, el importe de desarrollo debe ser 0€.
        if bool(st.session_state.get("repeticion_proyecto", False)):
            # Guardamos el último valor no-cero para poder recuperarlo si se desactiva.
            if st.session_state.get("imp_fijo_pvp_prev") in (None, ""):
                try:
                    st.session_state.imp_fijo_pvp_prev = float(st.session_state.get("imp_fijo_pvp", 0.0) or 0.0)
                except Exception:
                    st.session_state.imp_fijo_pvp_prev = 0.0
            st.session_state.imp_fijo_pvp = 0.0
            st.number_input("Importe de desarrollo de proyecto (€)", value=0.0, key="imp_fijo_pvp", disabled=True)
        else:
            # Si venimos de repetición y estaba a 0, restauramos el último valor guardado.
            try:
                cur = float(st.session_state.get("imp_fijo_pvp", 0.0) or 0.0)
            except Exception:
                cur = 0.0
            if cur == 0.0 and st.session_state.get("imp_fijo_pvp_prev") not in (None, ""):
                try:
                    st.session_state.imp_fijo_pvp = float(st.session_state.get("imp_fijo_pvp_prev") or 0.0)
                except Exception:
                    pass
            st.number_input("Importe de desarrollo de proyecto (€)", value=float(st.session_state.imp_fijo_pvp), key="imp_fijo_pvp")

        st.number_input("Multiplicador", step=0.1, value=float(st.session_state.margen), key="margen")

        st.markdown("---")
        st.number_input("Descuento sobre PROCESOS (%)", min_value=0.0, max_value=100.0, step=0.5, value=float(st.session_state.descuento_procesos), key="descuento_procesos")
        st.number_input("Margen materiales EXTRA", min_value=1.0, step=0.05, value=float(st.session_state.margen_extras), key="margen_extras")
        st.number_input("Margen EMBALAJES", min_value=1.0, step=0.05, value=float(st.session_state.margen_embalajes), key="margen_embalajes")

    dif_ud = float(st.session_state.dif_ud)
    imp_fijo_pvp = float(st.session_state.imp_fijo_pvp)
    if bool(st.session_state.get("repeticion_proyecto", False)):
        imp_fijo_pvp = 0.0
    margen = float(st.session_state.margen)
    descuento_procesos = float(st.session_state.descuento_procesos)
    margen_extras = float(st.session_state.margen_extras)
    margen_embalajes = float(st.session_state.margen_embalajes)

    st.divider()

    if lista_cants:
        # Primera sincronización de defaults antes de pintar la pantalla técnica.
        # Se repite justo antes del motor de cálculo para recoger formas recién creadas
        # o cambios de impresión hechos en este mismo rerun.
        _sync_mermas_defaults_actuales(lista_cants)
# -----------------------------------------------------
    # PASO 2: TÉCNICO
    # -----------------------------------------------------
    st.header("Paso 2 · Datos técnicos")

    c_btns = st.columns([2.2, 1.0, 3.0])
    ids_formas_existentes = sorted([int(x) for x in st.session_state.piezas_dict.keys()])
    opciones_copia_forma = ["Vacía"] + [f"Forma {pid}" for pid in ids_formas_existentes]

    with c_btns[0]:
        copiar_desde_forma = st.selectbox(
            "Crear nueva forma desde",
            opciones_copia_forma,
            index=0,
            key="copy_from_forma_sel",
            help="Elige una forma existente para duplicar sus datos técnicos, o 'Vacía' para crear una forma en blanco.",
        )

    with c_btns[1]:
        st.write("")
        if st.button("➕ Forma", key="btn_add_forma"):
            last_id = max(st.session_state.piezas_dict.keys())
            nid = int(last_id) + 1

            src_id = None
            if isinstance(copiar_desde_forma, str) and copiar_desde_forma.startswith("Forma "):
                try:
                    src_id = int(copiar_desde_forma.replace("Forma ", "").strip())
                except Exception:
                    src_id = None

            if src_id is not None and src_id in st.session_state.piezas_dict:
                # Copiamos la forma elegida y ajustamos el nombre para evitar confusión.
                st.session_state.piezas_dict[nid] = deepcopy(st.session_state.piezas_dict[src_id])
                st.session_state.piezas_dict[nid]["nombre"] = f"Forma {nid}"

                # Duplicamos también configuraciones asociadas al formato (si existen),
                # respetando compatibilidad con claves int/str.
                for kdict in ["mermas_proc_manual", "mermas_imp_manual", "mermas_imp_digital_manual"]:
                    d = st.session_state.get(kdict, {})
                    if isinstance(d, dict):
                        if str(src_id) in d:
                            d[str(nid)] = deepcopy(d[str(src_id)])
                        elif src_id in d:
                            d[str(nid)] = deepcopy(d[src_id])

                # Impresiones por cantidad por formato.
                en = st.session_state.get("impresiones_by_qty_fmt_enabled", {})
                if isinstance(en, dict):
                    if str(src_id) in en:
                        en[str(nid)] = bool(en.get(str(src_id), False))
                    elif src_id in en:
                        en[str(nid)] = bool(en.get(src_id, False))

                cfg_fmt = st.session_state.get("impresiones_by_qty_fmt", {})
                if isinstance(cfg_fmt, dict):
                    if str(src_id) in cfg_fmt:
                        cfg_fmt[str(nid)] = deepcopy(cfg_fmt[str(src_id)])
                    elif src_id in cfg_fmt:
                        cfg_fmt[str(nid)] = deepcopy(cfg_fmt[src_id])

            else:
                st.session_state.piezas_dict[nid] = crear_forma_vacia(nid)

            # Al añadir una forma, pasamos directamente a editarla para evitar modificar otra por error.
            # Nota Streamlit: no modificamos copy_from_forma_sel aquí porque es la key de un widget
            # ya instanciado en este rerun. Hacerlo provoca StreamlitAPIException.
            st.session_state._forma_edit_id = int(nid)
            st.rerun()
    if c_btns[2].button("🗑 Reiniciar"):

        st.session_state.piezas_dict = {1: crear_forma_vacia(1)}
        st.session_state.lista_extras_grabados = []
        st.session_state.embalajes = [crear_embalaje_vacio(0)]
        st.session_state.externos = [crear_externo_vacio(0)]
        st.session_state.mermas_imp_manual = {}
        st.session_state.mermas_proc_manual = {}
        st.rerun()

    def callback_cambio_frontal(pid):
        """Al cambiar cartoncillo cara, sincroniza widgets Y datos de la forma.

        Streamlit renderiza la columna de impresión antes que la columna de cartoncillo.
        Por eso, al cambiar cartoncillo, no basta con modificar solo las keys de widget:
        también actualizamos st.session_state.piezas_dict para que el siguiente rerun no
        pise los defaults con valores antiguos de la forma.
        """
        new_mat = st.session_state.get(f"pf_{pid}", "Ninguno")
        pieza = st.session_state.piezas_dict.get(pid, {}) if isinstance(st.session_state.get("piezas_dict", {}), dict) else {}

        if new_mat != "Ninguno":
            gramaje = int(st.session_state.db_precios["cartoncillo"].get(new_mat, {}).get("gramaje", 0))
            defaults = {
                "pf": new_mat,
                "gf": gramaje,
                "im": "Offset",
                "nt": 4,
                "ba": False,
                "ld": False,
                "pel": "Polipropileno",
            }
            st.session_state[f"gf_{pid}"] = gramaje
            st.session_state[f"im_{pid}"] = "Offset"
            st.session_state[f"nt_{pid}"] = 4
            st.session_state[f"ba_{pid}"] = False
            st.session_state[f"ld_{pid}"] = False
            st.session_state[f"pel_{pid}"] = "Polipropileno"
        else:
            defaults = {
                "pf": "Ninguno",
                "gf": 0,
                "im": "No",
                "nt": 0,
                "ba": False,
                "ld": False,
                "pel": "Sin Peliculado",
            }
            st.session_state[f"gf_{pid}"] = 0
            st.session_state[f"im_{pid}"] = "No"
            st.session_state[f"nt_{pid}"] = 0
            st.session_state[f"ba_{pid}"] = False
            st.session_state[f"ld_{pid}"] = False
            st.session_state[f"pel_{pid}"] = "Sin Peliculado"

        if isinstance(pieza, dict):
            pieza.update(defaults)

    def callback_cambio_dorso(pid):
        """Al cambiar cartoncillo dorso, sincroniza widgets Y datos de la forma."""
        new_mat = st.session_state.get(f"pd_{pid}", "Ninguno")
        pieza = st.session_state.piezas_dict.get(pid, {}) if isinstance(st.session_state.get("piezas_dict", {}), dict) else {}

        if new_mat != "Ninguno":
            gramaje = int(st.session_state.db_precios["cartoncillo"].get(new_mat, {}).get("gramaje", 0))
            defaults = {
                "pd": new_mat,
                "gd": gramaje,
                "im_d": "Offset",
                "nt_d": 4,
                "ba_d": False,
                "ld_d": False,
                "pel_d": "Polipropileno",
            }
            st.session_state[f"gd_{pid}"] = gramaje
            st.session_state[f"im_d_{pid}"] = "Offset"
            st.session_state[f"nt_d_{pid}"] = 4
            st.session_state[f"ba_d_{pid}"] = False
            st.session_state[f"ld_d_{pid}"] = False
            st.session_state[f"pel_d_{pid}"] = "Polipropileno"
        else:
            defaults = {
                "pd": "Ninguno",
                "gd": 0,
                "im_d": "No",
                "nt_d": 0,
                "ba_d": False,
                "ld_d": False,
                "pel_d": "Sin Peliculado",
            }
            st.session_state[f"gd_{pid}"] = 0
            st.session_state[f"im_d_{pid}"] = "No"
            st.session_state[f"nt_d_{pid}"] = 0
            st.session_state[f"ba_d_{pid}"] = False
            st.session_state[f"ld_d_{pid}"] = False
            st.session_state[f"pel_d_{pid}"] = "Sin Peliculado"

        if isinstance(pieza, dict):
            pieza.update(defaults)

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


    def callback_corte_default(pid, cants):
        """Sincroniza el corte por cantidad con el corte por defecto."""
        new_val = st.session_state.get(f"cor_def_{pid}", "Troquelado")
        # Actualiza widgets por cantidad
        for q in cants:
            st.session_state[f"cor_qty_{pid}_{q}"] = new_val
        # Actualiza estructura en memoria (por si se usa en cálculos sin rerun completo)
        try:
            pieza = st.session_state.piezas_dict.get(pid, None)
            if isinstance(pieza, dict):
                pieza["cor_default"] = new_val
                if not isinstance(pieza.get("cor_by_qty", {}), dict):
                    pieza["cor_by_qty"] = {}
                for q in cants:
                    pieza["cor_by_qty"][str(q)] = new_val
        except Exception:
            pass



    def _normalizar_acabados_cartoncillo(pid: int, pieza: dict) -> None:
        """Reglas de coherencia para cartoncillo/impresión/barniz/peliculado.

        - Sin cartoncillo y sin rígido imprimible: no impresión, 0 tintas, sin barniz y sin peliculado.
        - Sin cartoncillo pero con material rígido seleccionado: se permite impresión Digital en cara.
        - Con barniz: se anula el peliculado.
        - La selección de cartoncillo pone por defecto Offset 4 tintas + Polipropileno en los callbacks.
        - Primero sincroniza desde las keys de widgets para evitar que un valor antiguo de pieza
          pise el cambio recién hecho durante el rerun.
        """
        for _field, _key in {
            "pf": f"pf_{pid}", "pd": f"pd_{pid}",
            # Leer la selección nueva antes de validar el digital directo sobre rígido.
            "im": f"im_{pid}",
            "ba": f"ba_{pid}", "ba_d": f"ba_d_{pid}",
            "tipo_base": f"tb_{pid}",
            "mat_rigido": f"mrig_{pid}",
            "rig_manual": f"rigman_{pid}",
        }.items():
            if _key in st.session_state:
                pieza[_field] = st.session_state[_key]

        # Un rígido es imprimible en digital aunque no lleve cartoncillo.
        # No habilitamos Offset por defecto para rígidos: si no hay cartoncillo, solo se conserva Digital.
        rigido_imprimible = (
            pieza.get("tipo_base") == "Material Rígido"
            and (
                bool(pieza.get("rig_manual", False))
                or pieza.get("mat_rigido", "Ninguno") not in ("Ninguno", "", None)
            )
        )

        # Cara
        if pieza.get("pf", "Ninguno") == "Ninguno":
            if rigido_imprimible and str(pieza.get("im", "No")) == "Digital":
                # Permitimos impresión digital directa sobre material rígido.
                pieza["nt"] = 0
                pieza["ba"] = False
                pieza["pel"] = "Sin Peliculado"
                for k, v in {
                    f"nt_{pid}": 0,
                    f"ba_{pid}": False,
                    f"pel_{pid}": "Sin Peliculado",
                }.items():
                    st.session_state[k] = v
            else:
                pieza["im"] = "No"
                pieza["nt"] = 0
                pieza["ba"] = False
                pieza["ld"] = False
                pieza["pel"] = "Sin Peliculado"
                for k, v in {
                    f"im_{pid}": "No",
                    f"nt_{pid}": 0,
                    f"ba_{pid}": False,
                    f"ld_{pid}": False,
                    f"pel_{pid}": "Sin Peliculado",
                }.items():
                    st.session_state[k] = v
        elif bool(pieza.get("ba", False)):
            pieza["pel"] = "Sin Peliculado"
            st.session_state[f"pel_{pid}"] = "Sin Peliculado"

        # Dorso
        if pieza.get("pd", "Ninguno") == "Ninguno":
            pieza["im_d"] = "No"
            pieza["nt_d"] = 0
            pieza["ba_d"] = False
            pieza["ld_d"] = False
            pieza["pel_d"] = "Sin Peliculado"
            for k, v in {
                f"im_d_{pid}": "No",
                f"nt_d_{pid}": 0,
                f"ba_d_{pid}": False,
                f"ld_d_{pid}": False,
                f"pel_d_{pid}": "Sin Peliculado",
            }.items():
                st.session_state[k] = v
        elif bool(pieza.get("ba_d", False)):
            pieza["pel_d"] = "Sin Peliculado"
            st.session_state[f"pel_d_{pid}"] = "Sin Peliculado"
    # -----------------------------------------------------
    # FORMAS - MODO EDICIÓN INDIVIDUAL (rendimiento/estabilidad UI)
    # -----------------------------------------------------
    # Antes se renderizaban todos los widgets de todas las formas en cada rerun.
    # Con muchas formas, Streamlit reconstruía muchos widgets y podía abrir/saltar a
    # formatos anteriores. Ahora se renderiza una lista resumen y SOLO se pintan los
    # campos completos de la forma seleccionada.
    if "_forma_edit_id" not in st.session_state:
        st.session_state._forma_edit_id = None

    _forma_ids = sorted([int(x) for x in st.session_state.piezas_dict.keys()])
    if not _forma_ids:
        st.session_state.piezas_dict = {1: crear_forma_vacia(1)}
        _forma_ids = [1]

    if st.session_state._forma_edit_id not in _forma_ids:
        st.session_state._forma_edit_id = _forma_ids[0]

    st.markdown("##### Formas del proyecto")
    st.caption("Solo se editan los campos completos de una forma cada vez. Las demás quedan como resumen para evitar saltos y mejorar la velocidad.")

    def _fmt_num_resumen(v, dec=4):
        try:
            return f"{float(v):.{dec}f}"
        except Exception:
            return f"{v}"

    def _si_no_resumen(v):
        return "Sí" if bool(v) else "No"

    for _pid in _forma_ids:
        _p = st.session_state.piezas_dict.get(_pid, {})
        _is_active = int(st.session_state._forma_edit_id) == int(_pid)

        _tipo_base = str(_p.get("tipo_base", "Ondulado/Cartón"))

        def _acabado_txt(prefix: str = "") -> str:
            """Resumen limpio de impresión/acabados para cara o dorso."""
            im = str(_p.get(f"im{prefix}", "No"))
            nt = int(_p.get(f"nt{prefix}", 0) or 0)
            ba = bool(_p.get(f"ba{prefix}", False))
            pel = str(_p.get(f"pel{prefix}", "Sin Peliculado"))
            ld = bool(_p.get(f"ld{prefix}", False))

            partes = []
            if im != "No":
                partes.append(f"{im} {nt} tintas" if nt > 0 else im)
            if ba:
                partes.append("barniz")
            if pel and pel != "Sin Peliculado":
                partes.append(f"pel. {pel}")
            if ld:
                partes.append("laminado digital")
            return " · ".join(partes) if partes else "sin impresión/acabado"

        def _cartoncillo_txt(prefix: str = "") -> str:
            """Resumen de cartoncillo de cara o dorso."""
            mat_key = "pf" if prefix == "" else "pd"
            gr_key = "gf" if prefix == "" else "gd"
            mat = str(_p.get(mat_key, "Ninguno"))
            gr = int(_p.get(gr_key, 0) or 0)
            if mat == "Ninguno":
                return ""
            gr_txt = f" {gr}g" if gr > 0 else ""
            return f"{mat}{gr_txt} ({_acabado_txt(prefix)})"

        _cara_txt = _cartoncillo_txt("")
        if not _cara_txt:
            _cara_txt = "Sin cartoncillo"

        _dorso_txt = _cartoncillo_txt("_d")
        _doble_impresion_activa = (
            str(_p.get("im_d", "No")) != "No"
            or int(_p.get("nt_d", 0) or 0) > 0
            or bool(_p.get("ba_d", False))
            or str(_p.get("pel_d", "Sin Peliculado")) != "Sin Peliculado"
            or bool(_p.get("ld_d", False))
        )

        if _tipo_base == "Ondulado/Cartón":
            _soporte = str(_p.get("pl", "Ninguna"))
            _calidad = str(_p.get("ap", "B/C"))
            _soporte_txt = f"{_soporte} ({_calidad})"
            if bool(_p.get("pl_dif", False)):
                _soporte_txt += f" · plancha dif. {int(_p.get('pl_h', 0) or 0)}×{int(_p.get('pl_w', 0) or 0)} mm"
        else:
            _soporte_txt = str(_p.get("mat_rigido", "Ninguno"))
            if bool(_p.get("rig_manual", False)):
                _soporte_txt += (
                    f" · manual {int(_p.get('rig_h', 0) or 0)}×{int(_p.get('rig_w', 0) or 0)} mm"
                    f" · {float(_p.get('rig_precio_ud', 0.0) or 0.0):.4f} €/ud"
                )

        _corte_txt = str(_p.get("cor_default", "Troquelado"))
        _troquel_piezas = int(_p.get("troquel_piezas", 0) or 0)
        if _troquel_piezas > 0:
            _corte_txt += f" · {_troquel_piezas} piezas/troquel"
        if not bool(_p.get("cobrar_arreglo", True)):
            _corte_txt += " · sin arreglo"

        _cor_by_qty = _p.get("cor_by_qty", {})
        _cortes_qty_txt = ""
        if isinstance(_cor_by_qty, dict) and _cor_by_qty:
            try:
                _cortes_qty_txt = " · ".join([f"{k}: {v}" for k, v in sorted(_cor_by_qty.items(), key=lambda x: int(x[0]))])
            except Exception:
                _cortes_qty_txt = " · ".join([f"{k}: {v}" for k, v in _cor_by_qty.items()])

        _extras_tags = []
        _rigido_digital_activo = (
            _tipo_base == "Material Rígido"
            and str(_p.get("pf", "Ninguno")) == "Ninguno"
            and str(_p.get("im", "No")) == "Digital"
        )
        if _rigido_digital_activo:
            _extras_tags.append("Impresión digital sobre rígido")
        if bool(_p.get("flexografia", False)):
            _extras_tags.append("Flexografía")
        if bool(_p.get("stamping", False)):
            _extras_tags.append(
                f"Stamping {int(_p.get('stamping_w', 0) or 0)}×{int(_p.get('stamping_h', 0) or 0)} mm"
            )
        if bool(_p.get("fr24", False)):
            _extras_tags.append(f"FR24 {float(_p.get('fr24_rate', 0.05) or 0.0):.4f} €/m²")
        if bool(_p.get("contracolado_a_mano", False)):
            _extras_tags.append("Contracolado a mano")
        if _doble_impresion_activa:
            _extras_tags.append(f"Doble impresión: {_acabado_txt('_d')}")

        _dorso_line = ""
        if _dorso_txt:
            _dorso_line = f"<br><b>Cartoncillo dorso:</b> {_dorso_txt}"

        _cortes_qty_line = ""
        if _cortes_qty_txt:
            _cortes_qty_line = f"<br><b>Corte por cantidad:</b> {_cortes_qty_txt}"

        _extras_line = ""
        if _extras_tags:
            _extras_line = f"<br><b>Procesos marcados:</b> {' · '.join(_extras_tags)}"

        _card_border = "2px solid var(--primary-color)" if _is_active else "1px solid rgba(128, 128, 128, 0.45)"
        _card_shadow = "0 0 0 1px rgba(128, 128, 128, 0.10)" if _is_active else "none"

        _resumen_html = f"""
        <div style="
            border:{_card_border};
            border-radius:10px;
            padding:10px 12px;
            margin-bottom:8px;
            background:var(--secondary-background-color);
            color:var(--text-color);
            box-shadow:{_card_shadow};
        ">
            <div style="font-weight:800; margin-bottom:4px; color:var(--text-color);">
                {_p.get('nombre', f'Forma {_pid}')} · {int(_p.get('h', 0) or 0)}×{int(_p.get('w', 0) or 0)} mm · Pliegos/Ud: {_fmt_num_resumen(_p.get('pliegos', 1.0), 4)}
            </div>
            <div style="font-size:0.92em; line-height:1.35; color:var(--text-color);">
                <b>Cartoncillo cara:</b> {_cara_txt}<br>
                <b>Plancha / material rígido:</b> {_soporte_txt}{_dorso_line}<br>
                <b>Corte:</b> {_corte_txt}{_cortes_qty_line}{_extras_line}
            </div>
        </div>
        """

        c_edit, c_res = st.columns([1, 7])
        btn_label = "✅ Editando" if _is_active else "✏️ Editar"
        if c_edit.button(btn_label, key=f"edit_forma_{_pid}", disabled=_is_active):
            st.session_state._forma_edit_id = int(_pid)
            st.rerun()
        c_res.markdown(_resumen_html, unsafe_allow_html=True)

    st.divider()

    p_id = int(st.session_state._forma_edit_id)
    p = st.session_state.piezas_dict[p_id]
    _normalizar_acabados_cartoncillo(p_id, p)
    with st.container():
        st.markdown(f"##### Editando: {p.get('nombre', f'Forma {p_id}')} - {p.get('h', 0)}×{p.get('w', 0)} mm")
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
            val_im_raw = p.get("im", "No")
            val_im_norm = str(val_im_raw).strip().lower()
            if val_im_norm in ("offset", "off"):
                val_im = "Offset"
            elif val_im_norm in ("digital", "dig"):
                val_im = "Digital"
            elif val_im_norm in ("no", "ninguno", "none", ""):
                val_im = "No"
            else:
                # Compatibilidad: si viene algo raro de JSON antiguo, mantenemos "No"
                val_im = "No"
            idx_im = opts_im.index(val_im)
            p["im"] = st.selectbox("Impresión Cara", opts_im, index=idx_im, key=f"im_{p_id}")

            if p["im"] == "Offset":
                p["nt"] = st.number_input("Tintas Cara", 0, 12, int(p.get("nt", 4)), key=f"nt_{p_id}")
                p["ba"] = st.checkbox("Barniz Cara", value=bool(p.get("ba", False)), key=f"ba_{p_id}")
                if bool(p["ba"]):
                    p["pel"] = "Sin Peliculado"
                    st.session_state[f"pel_{p_id}"] = "Sin Peliculado"
            elif p["im"] == "Digital":
                p["ld"] = st.checkbox("Laminado Digital Cara", value=bool(p.get("ld", False)), key=f"ld_{p_id}")

            opts_pel = list(db["peliculado"].keys())
            val_pel = p.get("pel", "Sin Peliculado")
            idx_pel = opts_pel.index(val_pel) if val_pel in opts_pel else 0
            p["pel"] = st.selectbox("Peliculado Cara", opts_pel, index=idx_pel, key=f"pel_{p_id}")

            # -----------------------------------------------------
            # TINTA ESPECIAL FR24 (extra por m²)
            # -----------------------------------------------------
            p["fr24"] = st.checkbox("🧪 Tinta especial FR24 (extra €/m²)", value=bool(p.get("fr24", False)), key=f"fr24_{p_id}")
            if bool(p["fr24"]):
                st.caption(f"Tarifa FR24: {float(p.get('fr24_rate', 0.05)):.4f} €/m² · editable en Base de Datos → Impresión y flexografía.")

            # -----------------------------------------------------
            # STAMPING (película + calor) - proceso poco habitual
            # -----------------------------------------------------
            p["stamping"] = st.checkbox("✨ Stamping (película + pisada)", value=bool(p.get("stamping", False)), key=f"stamp_{p_id}")
            if bool(p["stamping"]):
                col_s1, col_s2, col_s3 = st.columns([1, 1, 1])
                with col_s1:
                    p["stamping_w"] = int(st.number_input("Ancho stamping (mm)", min_value=0, max_value=5000, value=int(p.get("stamping_w", 0)), step=1, key=f"stampw_{p_id}"))
                with col_s2:
                    p["stamping_h"] = int(st.number_input("Alto stamping (mm)", min_value=0, max_value=5000, value=int(p.get("stamping_h", 0)), step=1, key=f"stamph_{p_id}"))
                with col_s3:
                    p["stamping_cobrar_arreglo"] = bool(st.checkbox("Cobrar arreglo stamping", value=bool(p.get("stamping_cobrar_arreglo", True)), key=f"stamparr_{p_id}"))
                st.caption(f"Tarifa stamping: arreglo {_aud_importe(float(db.get('stamping', {}).get('arreglo', 168.0)))} · pisada {_aud_importe(float(db.get('stamping', {}).get('pisada', 0.21)), 4)}/pisada · película {_aud_importe(float(db.get('stamping', {}).get('pelicula_m2', 0.39)), 4)}/m². Pisadas ajustadas por piezas por troquel.")
            else:
                p["stamping_w"] = int(p.get("stamping_w", 0))
                p["stamping_h"] = int(p.get("stamping_h", 0))
                p["stamping_cobrar_arreglo"] = bool(p.get("stamping_cobrar_arreglo", True))

            # -----------------------------------------------------
            # IMPRESIONES POR CANTIDAD (multi-tirada) - POR FORMATO (TIC)
            # -----------------------------------------------------
            # Si una misma cantidad se imprime en varias tiradas (p.ej. 100+400+500) para ESTA forma,
            # indícalo aquí. Solo afecta a: (1) coste de impresión y (2) merma de cartoncillo (una merma extra por cada impresión).
            # El resto de procesos mantiene su merma habitual.
            pid_key = str(int(p_id))
            if "impresiones_by_qty_fmt_enabled" not in st.session_state:
                st.session_state.impresiones_by_qty_fmt_enabled = {}
            if "impresiones_by_qty_fmt" not in st.session_state:
                st.session_state.impresiones_by_qty_fmt = {}

            tic_def = bool(st.session_state.impresiones_by_qty_fmt_enabled.get(pid_key, False)) if isinstance(st.session_state.impresiones_by_qty_fmt_enabled, dict) else False
            tic = st.checkbox("🖨️ Varias impresiones por cantidad (esta forma)", value=bool(st.session_state.get(f"impact_{p_id}", tic_def)), key=f"impact_{p_id}")
            if isinstance(st.session_state.impresiones_by_qty_fmt_enabled, dict):
                st.session_state.impresiones_by_qty_fmt_enabled[pid_key] = bool(tic)

            if bool(tic) and lista_cants:
                with st.expander("🖨️ Desglose de impresiones por cantidad (esta forma)", expanded=False):
                    st.caption("Ejemplo: 1000 uds -> 3 impresiones: 100+400+500. "
                               "Solo afecta a coste de impresión y merma extra de cartoncillo por impresión.")
                    cfg_fmt_all = st.session_state.impresiones_by_qty_fmt if isinstance(st.session_state.impresiones_by_qty_fmt, dict) else {}
                    cfg_fmt = cfg_fmt_all.get(pid_key, {}) if isinstance(cfg_fmt_all.get(pid_key, {}), dict) else {}

                    for q in lista_cants:
                        cfg = cfg_fmt.get(str(int(q)), {}) if isinstance(cfg_fmt.get(str(int(q)), {}), dict) else {}
                        try:
                            n_def = int(cfg.get("n", 1))
                        except Exception:
                            n_def = 1
                        n_def = max(1, n_def)
                        modo_def = str(cfg.get("modo", "igual")).lower().strip()
                        igual_def = (modo_def != "manual")
                        partes_def = cfg.get("partes", []) if isinstance(cfg.get("partes", []), list) else []
                        try:
                            partes_def_str = "+".join(str(int(x)) for x in partes_def) if partes_def else ""
                        except Exception:
                            partes_def_str = ""

                        c1i, c2i = st.columns([1, 3])
                        with c1i:
                            n_imp = st.number_input(
                                f"{q} uds · Nº impresiones",
                                min_value=1,
                                step=1,
                                value=int(st.session_state.get(f"impn_{p_id}_{q}", n_def)),
                                key=f"impn_{p_id}_{q}",
                            )
                        with c2i:
                            igual = st.checkbox(
                                "Repartir a partes iguales",
                                value=bool(st.session_state.get(f"impigual_{p_id}_{q}", igual_def)),
                                key=f"impigual_{p_id}_{q}",
                            )

                        partes = []
                        if int(n_imp) <= 1:
                            partes = [int(q)]
                            cfg_fmt[str(int(q))] = {"n": 1, "modo": "igual", "partes": partes}
                            st.caption("Tirada única.")
                            continue

                        if bool(igual):
                            partes = _split_equal(int(q), int(n_imp))
                            cfg_fmt[str(int(q))] = {"n": int(n_imp), "modo": "igual", "partes": partes}
                            st.caption(f"Tiradas: {partes} (suma {sum(partes)})")
                        else:
                            txt = st.text_input(
                                "Desglose (ej: 100+400+500)",
                                value=str(st.session_state.get(f"impman_{p_id}_{q}", partes_def_str)),
                                key=f"impman_{p_id}_{q}",
                            )
                            partes_manual = _parse_partes_str(txt)
                            if partes_manual and len(partes_manual) == int(n_imp) and sum(partes_manual) == int(q):
                                partes = partes_manual
                                cfg_fmt[str(int(q))] = {"n": int(n_imp), "modo": "manual", "partes": partes}
                                st.caption(f"Tiradas: {partes} (suma {sum(partes)})")
                            else:
                                partes = _split_equal(int(q), int(n_imp))
                                cfg_fmt[str(int(q))] = {"n": int(n_imp), "modo": "igual", "partes": partes}
                                st.warning("El desglose manual no cuadra (nº partes o suma). Se ha aplicado reparto igual.")
                                st.caption(f"Tiradas: {partes} (suma {sum(partes)})")

                    cfg_fmt_all[pid_key] = cfg_fmt
                    st.session_state.impresiones_by_qty_fmt = cfg_fmt_all


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
                # Nuevo desplegable por familia; los materiales antiguos solo se muestran
                # cuando la forma importada los utiliza, evitando nuevas selecciones legadas.
                _legadas = {"Microcanal / Canal 3", "Doble Micro / Doble Doble", "AC (Cuero/Cuero)"}
                val_pl = p.get("pl", "Ninguna")
                opts_pl = [k for k in db["planchas"] if k not in _legadas or k == val_pl]
                if val_pl not in opts_pl and val_pl in db["planchas"]:
                    opts_pl.append(val_pl)
                idx_pl = opts_pl.index(val_pl) if val_pl in opts_pl else 0
                p["pl"] = st.selectbox("Familia de plancha", opts_pl, index=idx_pl, key=f"pl_{p_id}",
                                       format_func=lambda x: f"{x} (tarifa histórica)" if x in _legadas else x)

                if p["pl"] != "Ninguna":
                    p["pl_dif"] = st.checkbox("📏 Medida Plancha Diferente", value=bool(p.get("pl_dif", False)), key=f"pldif_{p_id}")
                    if p["pl_dif"]:
                        c_ph, c_pw = st.columns(2)
                        p["pl_h"] = c_ph.number_input("Alto Plancha", 0, 5000, value=int(p.get("pl_h", p["h"])), key=f"plh_{p_id}")
                        p["pl_w"] = c_pw.number_input("Ancho Plancha", 0, 5000, value=int(p.get("pl_w", p["w"])), key=f"plw_{p_id}")
                    else:
                        p["pl_h"] = p["h"]
                        p["pl_w"] = p["w"]

                plancha_info = db.get("planchas", {}).get(p["pl"], {})
                opts_ap = [q for q in plancha_info if q != "peg"] if isinstance(plancha_info, dict) else []
                if not opts_ap:
                    opts_ap = ["C/C"]
                val_ap = p.get("ap", "B/C")
                idx_ap = opts_ap.index(val_ap) if val_ap in opts_ap else 0
                p["ap"] = st.selectbox("Calidad de plancha", opts_ap, index=idx_ap, key=f"ap_{p_id}")
                _precio_tarifa = plancha_info.get(p["ap"], None) if isinstance(plancha_info, dict) else None
                if _precio_tarifa is not None and p["pl"] != "Ninguna":
                    st.caption(f"Materia prima: {float(_precio_tarifa):.3f} €/m² (sin descuentos ni contracolado)")
                if p["pl"] in _legadas:
                    st.warning("Esta forma utiliza una tarifa histórica. Selecciona una nueva familia y calidad si deseas actualizarla; no se convierte automáticamente.")

                p["flexografia"] = st.checkbox("🟪 Flexografía (coste fijo por plancha)", value=bool(p.get("flexografia", False)), key=f"flexo_{p_id}")

            else:
                p["rig_manual"] = st.checkbox("🧩 Rígido Manual (tamaño + precio)", value=bool(p.get("rig_manual", False)), key=f"rigman_{p_id}")

                if p["rig_manual"]:
                    c_rw, c_rh, c_rp = st.columns(3)
                    p["rig_w"] = int(c_rw.number_input("Hoja w (mm)", 0, 10000, value=int(p.get("rig_w", 0)), key=f"rigwman_{p_id}"))
                    p["rig_h"] = int(c_rh.number_input("Hoja h (mm)", 0, 10000, value=int(p.get("rig_h", 0)), key=f"righman_{p_id}"))
                    p["rig_precio_ud"] = float(c_rp.number_input("Precio hoja (€)", 0.0, 999999.0, value=float(p.get("rig_precio_ud", 0.0)), step=0.01, key=f"rigpman_{p_id}"))
                    st.caption(
                        "Este rígido manual se usa SOLO en esta pieza. "
                        "Si las medidas de la forma no caben en la hoja del rígido, "
                        "la app imputará 1 hoja rígida por hoja de producción para evitar coste 0."
                    )
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
                        st.caption("Los materiales rígidos se pueden imprimir en Digital desde el selector 'Impresión Cara'.")

            p["contracolado_a_mano"] = st.checkbox(
                f"🖐️ Contracolado a mano (NARBA · {_tarifa('narba', 'contracolado_a_mano_m2'):.4f} €/m²)",
                value=bool(p.get("contracolado_a_mano", False)),
                key=f"contramano_{p_id}",
                help="Aplica la tarifa de contracolado a mano por m², independiente del material."
            )

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
            opts_cor = ["Sin corte", "Troquelado", "Plotter"]
            val_cor = p.get("cor_default", p.get("cor", "Troquelado"))
            idx_troq = opts_cor.index("Troquelado")
            idx_cor = opts_cor.index(val_cor) if val_cor in opts_cor else idx_troq
            p["cor_default"] = st.selectbox(
                "Corte (por defecto)", opts_cor, index=idx_cor, key=f"cor_def_{p_id}",
                on_change=callback_corte_default, args=(p_id, lista_cants,)
            )

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

            # ✅ Troquelado: permitir forzar manualmente cuántas piezas salen por golpe de troquel.
            # 0 = automático (se asume 1/pliegos_por_ud cuando pliegos<1).
            p["troquel_piezas"] = int(st.number_input(
                "Piezas por troquel (0 = automático)",
                min_value=0,
                step=1,
                value=int(p.get("troquel_piezas", 0) or 0),
                key=f"trqp_{p_id}",
            ))

            if p.get("pd", "Ninguno") != "Ninguno":
                opts_imd = ["Offset", "Digital", "No"]
                val_imd_raw = p.get("im_d", "No")
                val_imd_norm = str(val_imd_raw).strip().lower()
                if val_imd_norm in ("offset", "off"):
                    val_imd = "Offset"
                elif val_imd_norm in ("digital", "dig"):
                    val_imd = "Digital"
                elif val_imd_norm in ("no", "ninguno", "none", ""):
                    val_imd = "No"
                else:
                    val_imd = "No"
                idx_imd = opts_imd.index(val_imd)
                p["im_d"] = st.selectbox("Impresión Dorso", opts_imd, index=idx_imd, key=f"im_d_{p_id}")

                if p["im_d"] == "Offset":
                    p["nt_d"] = st.number_input("Tintas Dorso", 0, 12, int(p.get("nt_d", 0)), key=f"nt_d_{p_id}")
                    p["ba_d"] = st.checkbox("Barniz Dorso", value=bool(p.get("ba_d", False)), key=f"ba_d_{p_id}")
                    if bool(p["ba_d"]):
                        p["pel_d"] = "Sin Peliculado"
                        st.session_state[f"pel_d_{p_id}"] = "Sin Peliculado"
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
                _remaining_ids = [int(x) for x in st.session_state.piezas_dict.keys() if int(x) != int(p_id)]
                del st.session_state.piezas_dict[p_id]
                st.session_state._forma_edit_id = min(_remaining_ids) if _remaining_ids else None
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
            st.session_state.lista_extras_grabados.append({"nombre": f"FLEXICO: {prod['desc']}", "coste": float(db["flexico"][cod]), "cantidad": 1.0, "tipo": "flexico"})
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
        if len(st.session_state.embalajes) < 15:
            st.session_state.embalajes.append(crear_embalaje_vacio(len(st.session_state.embalajes)))
            st.rerun()
        else:
            st.warning("Máximo 15 embalajes.")

    if cE2.button("🗑 Reset embalajes"):
        st.session_state.embalajes = [crear_embalaje_vacio(0)]
        st.rerun()

    if not lista_cants:
        st.warning("Define cantidades en Paso 1.")
    else:
        for ei, emb in enumerate(st.session_state.embalajes):
            with st.expander(f"📦 {emb.get('nombre', f'Embalaje {ei+1}')}", expanded=True):
                c0, c1, c2, c3, c4 = st.columns([2, 2, 2, 2, 1])
                emb["nombre"] = c0.text_input("Nombre", value=emb.get("nombre", f"Embalaje {ei+1}"), key=f"emb_name_{ei}")
                emb["tipo"] = c1.selectbox("Tipo", TIPOS_EMB, index=TIPOS_EMB.index(emb.get("tipo", "Manual")) if emb.get("tipo","Manual") in TIPOS_EMB else 0, key=f"emb_tipo_{ei}")
                emb["material"] = c2.selectbox("Material", EMB_MATS, index=EMB_MATS.index(emb.get("material","Canal 5")) if emb.get("material","Canal 5") in EMB_MATS else 0, key=f"emb_mat_{ei}")
                emb["uds_por_caja"] = int(c3.number_input("Uds por caja", min_value=1, step=1, value=int(emb.get("uds_por_caja", 1) or 1), key=f"embUPC_{ei}"))
                if c4.button("🗑", key=f"emb_del_{ei}"):
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
                    # Si una caja contiene varias uds, el coste automático debe calcularse por nº de cajas.
                    try:
                        uds_por_caja = int(emb.get("uds_por_caja", 1) or 1)
                    except Exception:
                        uds_por_caja = 1
                    uds_por_caja = max(1, int(uds_por_caja))
                    q_calc = int(math.ceil(int(q) / float(uds_por_caja))) if int(q) > 0 else 0
                    if emb["tipo"] == "Manual":
                        emb["costes"][q] = float(cols[idx].number_input(f"Coste compra caja ({q} uds)", value=float(emb["costes"].get(q, 0.0)), key=f"embMan_{ei}_{q}"))
                    elif emb["tipo"] == "Embalaje Guaina (Automático)":
                        L, W, H = emb["dims"]["L"], emb["dims"]["W"], emb["dims"]["H"]
                        sup_m2 = ((2*(L+W)*H) + (L*W)) / 1_000_000 if (L>0 and W>0 and H>0) else 0.0
                        coste_auto = (sup_m2 * _tarifa("embalajes", "precio_m2", "guaina")) + (_tarifa("embalajes", "arreglo", "guaina") / q_calc) if q_calc>0 else 0.0
                        coste_auto *= mult
                        emb["costes"][q] = float(coste_auto)
                        cols[idx].metric(f"{q} uds", f"{coste_auto:.3f}€")

                    elif emb["tipo"] == "Aros de refuerzo":
                        # Para aros usamos solo L y W (medidas máximas en plano). H se ignora.
                        L, W = emb["dims"]["L"], emb["dims"]["W"]
                        # Q_aros = nº de aros (tratamos uds_por_caja como 'uds por aro' para compatibilidad)
                        Q_aros = int(q_calc) if q_calc > 0 else 0
                        coste_auto = aros_refuerzo_precio_ud(L, W, Q_aros, emb.get("material", "Canal 5")) if Q_aros > 0 else 0.0
                        emb["costes"][q] = float(coste_auto)
                        cols[idx].metric(f"{q} uds", f"{coste_auto:.3f}€")

                    elif emb["tipo"] == "Embalaje en Plano":
                        L, W, H = emb["dims"]["L"], emb["dims"]["W"], emb["dims"]["H"]
                        c_plano, _S = embalaje_plano_unit(L, W, H, q_calc)
                        c_plano *= mult
                        emb["costes"][q] = float(c_plano)
                        cols[idx].metric(f"{q} uds", f"{c_plano:.3f}€")
                    elif emb["tipo"] == "Embalaje en Volumen":
                        L, W, H = emb["dims"]["L"], emb["dims"]["W"], emb["dims"]["H"]
                        c_vol, _S = embalaje_volumen_unit(L, W, H, q_calc)
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
    if not lista_cants:
        st.warning("Define cantidades en Paso 1.")
    else:
        # Digital se mantiene global por cantidad (como estaba)
        st.markdown("**Impresión DIGITAL (global por cantidad)**")
        for q in lista_cants:
            c1, c2 = st.columns([1, 3])
            c1.markdown(f"**{q} uds**")
            st.session_state.mermas_imp_digital_manual[q] = int(
                c2.number_input(
                    "Arranque impresión DIGITAL (hojas)",
                    value=_get_merma_impresion_digital_hojas(q),
                    key=f"mid_{q}",
                )
            )

        st.markdown("**OFFSET / Procesos (por Forma y cantidad)**")
        piezas = st.session_state.get("piezas_dict", {})
        if not isinstance(piezas, dict) or not piezas:
            st.info("No hay formas definidas.")
        else:
            for pid, p in piezas.items():
                nombre = p.get("nombre", f"Forma {pid}")
                with st.expander(f"🧾 Mermas - {nombre}", expanded=False):
                    # Cabecera
                    for q in lista_cants:
                        pl = float(p.get("pliegos", 1.0))
                        mp_def, _ = calcular_mermas_estandar(int(q), pliegos_por_ud=pl, es_digital=False, n_tintas=4, barniz=False)

                        # Defaults impresión por lado
                        is_offset_c = str(p.get("im", "No")).strip().lower() == "offset"
                        is_offset_d = str(p.get("im_d", "No")).strip().lower() == "offset"
                        mi_def_c = _merma_impresion_offset_por_pasadas(int(p.get("nt", 4)), bool(p.get("ba", False))) if is_offset_c else 0
                        mi_def_d = _merma_impresion_offset_por_pasadas(int(p.get("nt_d", 4)), bool(p.get("ba_d", False))) if is_offset_d else 0

                        c0, c1, c2, c3 = st.columns([1, 2, 2, 2])
                        c0.markdown(f"**{q} uds**")

                        # Proceso
                        _ss_autoupdate_merma_proc(int(pid), int(q), int(mp_def))
                        v_proc = int(_ss_get_merma_proc(int(pid), int(q), int(mp_def)))
                        # Guardamos la edición (si cambia)
                        st.session_state.mermas_proc_manual.setdefault(str(pid), {})
                        st.session_state.mermas_proc_manual[str(pid)][str(int(q))] = int(
                            c1.number_input(
                                "Rodaje proceso (hojas)",
                                min_value=0,
                                value=v_proc,
                                step=1,
                                key=f"mp_{pid}_{q}",
                            )
                        )

                        # Impresión cara/dorso (OFFSET)
                        st.session_state.mermas_imp_manual.setdefault(str(pid), {})
                        qk = str(int(q))
                        if qk not in st.session_state.mermas_imp_manual[str(pid)] or not isinstance(st.session_state.mermas_imp_manual[str(pid)][qk], dict):
                            st.session_state.mermas_imp_manual[str(pid)][qk] = {"cara": 0, "dorso": 0}

                        # Cara
                        mi_key_c = f"mi_c_{pid}_{q}"
                        if is_offset_c:
                            # Default auto según tintas/barniz (se recalcula si cambian y el usuario no lo ha tocado)
                            _ss_sync_merma_imp_widget(int(pid), int(q), "cara", mi_key_c, int(mi_def_c))
                            v_c_auto = int(_ss_get_merma_imp(int(pid), int(q), "cara", int(mi_def_c)))
                            if mi_key_c not in st.session_state:
                                st.session_state[mi_key_c] = int(v_c_auto)

                            v_c = int(st.session_state.get(mi_key_c, int(v_c_auto)))
                            v_c = int(st.session_state.get(mi_key_c, int(v_c_auto)))
                            v_c_in = int(
                                c2.number_input(
                                    "Merma impresión OFFSET (cara)",
                                    min_value=0,
                                    value=v_c,
                                    step=1,
                                    key=mi_key_c,
                                )
                            )
                            st.session_state.mermas_imp_manual[str(pid)][qk]["cara"] = v_c_in
                        else:
                            # Si no es Offset, no aplicamos merma de impresión
                            if mi_key_c not in st.session_state:
                                st.session_state[mi_key_c] = 0
                            c2.number_input(
                                "Merma impresión OFFSET (cara)",
                                min_value=0,
                                value=0,
                                step=1,
                                key=mi_key_c,
                                disabled=True,
                            )
                            st.session_state.mermas_imp_manual[str(pid)][qk]["cara"] = 0

                        # Dorso
                        mi_key_d = f"mi_d_{pid}_{q}"
                        if is_offset_d:
                            # Default auto según tintas/barniz (se recalcula si cambian y el usuario no lo ha tocado)
                            _ss_sync_merma_imp_widget(int(pid), int(q), "dorso", mi_key_d, int(mi_def_d))
                            v_d_auto = int(_ss_get_merma_imp(int(pid), int(q), "dorso", int(mi_def_d)))
                            if mi_key_d not in st.session_state:
                                st.session_state[mi_key_d] = int(v_d_auto)

                            v_d = int(st.session_state.get(mi_key_d, int(v_d_auto)))
                            v_d = int(st.session_state.get(mi_key_d, int(v_d_auto)))
                            v_d_in = int(
                                c3.number_input(
                                    "Merma impresión OFFSET (dorso)",
                                    min_value=0,
                                    value=v_d,
                                    step=1,
                                    key=mi_key_d,
                                )
                            )
                            st.session_state.mermas_imp_manual[str(pid)][qk]["dorso"] = v_d_in
                        else:
                            if mi_key_d not in st.session_state:
                                st.session_state[mi_key_d] = 0
                            c3.number_input(
                                "Merma impresión OFFSET (dorso)",
                                min_value=0,
                                value=0,
                                step=1,
                                key=mi_key_d,
                                disabled=True,
                            )
                            st.session_state.mermas_imp_manual[str(pid)][qk]["dorso"] = 0
# Segunda sincronización de mermas, ya con las formas actualizadas por la UI.
# Esto evita que una forma nueva o un cambio a Offset tenga que esperar otro rerun
# para tener su merma de impresión correcta.
if lista_cants:
    _sync_mermas_defaults_actuales(lista_cants)

# =========================================================
# MOTOR DE CÁLCULO + DESGLOSE + COMPRAS
# =========================================================
# NOTA PERFORMANCE:
# - Si NO se ha pulsado "🧮 Calcular", reutilizamos el último cálculo guardado en session_state._calc_cache.
# - Esto evita recalcular en cada cambio de widget (especialmente en "Formas").
# =========================================================
if isinstance(st.session_state.get("_calc_cache"), dict) and st.session_state._calc_cache.get("_precios_venta_version") != 1:
    st.session_state._calc_requested = True

if isinstance(st.session_state.get("_calc_cache"), dict) and not bool(st.session_state.get("_calc_requested", False)):
    _c = st.session_state._calc_cache
    res_final = _c.get("res_final", []) or []
    desc_full = _c.get("desc_full", {}) or {}
    compras_legible = _c.get("compras_legible", {}) or {}
    resumen_costes_export = _c.get("resumen_costes_export", {}) or {}
else:
    # Se recalcula a continuación (solo cuando se pulsa 🧮 Calcular o no hay caché)

# =========================================================
    res_final = []
    desc_full = {}
    compras_legible = {}
    resumen_costes_export = {}

    if bool(st.session_state.get("_calc_requested", False)):
        if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
            tot_pv_trq = sum(float(pz.get("pv_troquel", 0.0)) for pz in st.session_state.piezas_dict.values())

            for q_n in lista_cants:
                # Mermas:
                # - Digital: mermas_imp_digital_manual (fallback a regla digital si no existe)
                # - Procesos e impresión OFFSET: por forma+cantidad (ver _ss_get_* en helpers)
                merma_imp_digital_hojas = int(_get_merma_impresion_digital_hojas(q_n))

                coste_f = 0.0
                det_f = []
                aud_formas = []
                aud_otras = []
                aud_opcionales = []
                aud_venta = []
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
                        "stamping": 0.0,
                        "manipulacion": 0.0,
                        "dificultad": 0.0,
                        "externos": 0.0,
                    },
                    "embalajes_venta": []
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
                    c_stamping = 0.0
                    aud_lineas = []
                    aud_avisos = []
                    merma_cara = merma_d = 0

                    # Impresiones por cantidad (multi-tirada) - POR FORMATO:
                    # Solo afecta a coste de impresión y a la merma extra de cartoncillo por impresión.
                    partes_imp_units = obtener_partes_impresion_por_formato(int(pid), int(q_n))
                    n_impresiones_qty = len(partes_imp_units) if partes_imp_units else 1

                    pl = float(p.get("pliegos", 1.0))
                    nb = int(math.ceil(q_n * pl))
                    mp_def, _mi_ign = calcular_mermas_estandar(q_n, pliegos_por_ud=pl, es_digital=False, n_tintas=4, barniz=False)
                    _ss_autoupdate_merma_proc(int(pid), int(q_n), int(mp_def))
                    merma_proc_hojas = _ss_get_merma_proc(int(pid), int(q_n), int(mp_def))
                    hp_produccion = nb + int(merma_proc_hojas)

                    im_cara = p.get("im", "No")
                    im_dorso = p.get("im_d", "No")

                    imprime_cara = (im_cara != "No")
                    imprime_dorso = (p.get("pd", "Ninguno") != "Ninguno" and im_dorso != "No")

                    # 👇 Merma de impresión depende del tipo (Offset vs Digital)
                    # Multi-tirada: la merma extra de cartoncillo se cuenta 1 vez por impresión.
                    if imprime_cara:
                        if im_cara == "Digital":
                            merma_cara = int(merma_imp_digital_hojas)
                        elif im_cara == "Offset":
                            mi_def_c = _merma_impresion_offset_por_pasadas(int(p.get("nt", 4)), bool(p.get("ba", False)))
                            _ss_autoupdate_merma_imp(int(pid), int(q_n), "cara", int(mi_def_c))
                            merma_cara = int(_ss_get_merma_imp(int(pid), int(q_n), "cara", int(mi_def_c)))
                        else:
                            merma_cara = 0
                        hp_papel_f = hp_produccion + (merma_cara * int(n_impresiones_qty))
                    else:
                        hp_papel_f = hp_produccion

                    if imprime_dorso:
                        if im_dorso == "Digital":
                            merma_d = int(merma_imp_digital_hojas)
                        elif im_dorso == "Offset":
                            mi_def_d = _merma_impresion_offset_por_pasadas(int(p.get("nt_d", 4)), bool(p.get("ba_d", False)))
                            _ss_autoupdate_merma_imp(int(pid), int(q_n), "dorso", int(mi_def_d))
                            merma_d = int(_ss_get_merma_imp(int(pid), int(q_n), "dorso", int(mi_def_d)))
                        else:
                            merma_d = 0
                        hp_papel_d = hp_produccion + (merma_d * int(n_impresiones_qty))
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

                        rigido_manual_activo = bool(p.get("rig_manual", False))

                        # Para rígidos manuales/custom evitamos que el coste quede a 0 silenciosamente:
                        # - Si el usuario ha informado hoja y precio, pero las medidas de la forma están vacías,
                        #   usamos la hoja del rígido como medida efectiva.
                        # - Si la forma no cabe en la hoja del rígido, contamos 1 hoja rígida por hoja de producción
                        #   en vez de dejar el material sin coste. Así el supuesto no se infravalora por error de encaje.
                        w_calc = float(w)
                        h_calc = float(h)
                        fallback_rigido_manual = False
                        aviso_rigido_manual = ""

                        if rigido_manual_activo and (w_calc <= 0 or h_calc <= 0) and mw > 0 and mh > 0:
                            w_calc = mw
                            h_calc = mh
                            fallback_rigido_manual = True
                            aviso_rigido_manual = "medidas forma vacías: se usa hoja rígida como 1 unidad"

                        if w_calc > 0 and h_calc > 0 and mw > 0 and mh > 0:
                            y1 = int(mw // w_calc) * int(mh // h_calc)
                            y2 = int(mw // h_calc) * int(mh // w_calc)
                            by = max(y1, y2)
                        else:
                            by = 0

                        if by <= 0 and rigido_manual_activo and mw > 0 and mh > 0 and precio_hoja > 0:
                            by = 1
                            fallback_rigido_manual = True
                            aviso_rigido_manual = "la forma no cabe en la hoja rígida: se imputa 1 hoja rígida por hoja de producción"

                        if by > 0:
                            n_net = math.ceil(hp_produccion / by)
                            if capas_contracolado == 0:
                                n_pl = n_net + merma_rigido_fija(n_net)
                            else:
                                n_pl = math.ceil(n_net * 1.02)
                            c_rigido = n_pl * precio_hoja
                            _aud_linea(aud_lineas, "Rígido manual" if rigido_manual_activo else p.get("mat_rigido", "Rígido"),
                                "Material", n_pl, "hojas", float(p.get("rig_precio_ud", 0.0)) if rigido_manual_activo else float(info["precio_ud"]),
                                0.0 if rigido_manual_activo else float(db_desc.get("ondulado_rigidos", 0.0)), c_rigido,
                                f"Hoja {max(mw, mh):g} × {min(mw, mh):g} mm · {by} piezas/hoja · {n_net} hojas netas + {n_pl - n_net} de merma")
                            if fallback_rigido_manual:
                                aud_avisos.append(aviso_rigido_manual)

                            log_rigido = {
                                "qty": q_n,
                                "pieza": p.get("nombre",""),
                                "tipo": "rigido",
                                "by": by,
                                "hojas_netas": n_net,
                                "hojas_total": n_pl,
                                "precio_hoja": precio_hoja,
                                "coste": c_rigido,
                                "merma_regla": "fija" if capas_contracolado == 0 else "2%"
                            }
                            if fallback_rigido_manual:
                                log_rigido["aviso"] = aviso_rigido_manual
                            debug_log.append(log_rigido)
                    else:
                        if p.get("pl", "Ninguna") != "Ninguna":
                            if bool(p.get("pl_dif", False)) and float(p.get("pl_h", 0)) > 0 and float(p.get("pl_w", 0)) > 0:
                                m2_plancha = (float(p["pl_w"]) * float(p["pl_h"])) / 1_000_000
                            else:
                                m2_plancha = m2_papel
                            c_ondulado = hp_produccion * m2_plancha * float(db["planchas"][p["pl"]][p.get("ap","B/C")]) * f_or
                            _aud_linea(aud_lineas, f"Ondulado · {p['pl']} · {p.get('ap', 'B/C')}", "Material",
                                hp_produccion * m2_plancha, "m²", float(db["planchas"][p["pl"]][p.get("ap", "B/C")]),
                                float(db_desc.get("ondulado_rigidos", 0.0)), c_ondulado,
                                f"{hp_produccion} hojas × {m2_plancha:g} m²/hoja")
                            # Flexografía: coste fijo por plancha (no depende de cantidad)
                            if bool(p.get("flexografia", False)):
                                c_ondulado += float(db.get("flexografia", {}).get("arreglo", 180.0))
                                _aud_linea(aud_lineas, "Arreglo flexografía", "Proceso", 1, "arreglo",
                                    float(db.get("flexografia", {}).get("arreglo", 180.0)), 0.0,
                                    float(db.get("flexografia", {}).get("arreglo", 180.0)), "El motor lo incluye en el coste de ondulado; aquí se identifica como proceso.")

                    if p.get("pf", "Ninguno") != "Ninguno" and m2_papel > 0:
                        c_cart_cara = hp_papel_f * m2_papel * (float(p.get("gf", 0))/1000.0) * float(db["cartoncillo"][p["pf"]]["precio_kg"]) * f_cart
                        _aud_linea(aud_lineas, f"Cartoncillo cara · {p['pf']}", "Material",
                            hp_papel_f * m2_papel * (float(p.get("gf", 0)) / 1000.0), "kg",
                            float(db["cartoncillo"][p["pf"]]["precio_kg"]), float(db_desc.get("cartoncillo", 0.0)), c_cart_cara,
                            f"{hp_papel_f} hojas × {m2_papel:g} m² × {p.get('gf', 0)} g/m²")
                    if p.get("pd", "Ninguno") != "Ninguno" and m2_papel > 0:
                        c_cart_dorso = hp_papel_d * m2_papel * (float(p.get("gd", 0))/1000.0) * float(db["cartoncillo"][p["pd"]]["precio_kg"]) * f_cart
                        _aud_linea(aud_lineas, f"Cartoncillo dorso · {p['pd']}", "Material",
                            hp_papel_d * m2_papel * (float(p.get("gd", 0)) / 1000.0), "kg",
                            float(db["cartoncillo"][p["pd"]]["precio_kg"]), float(db_desc.get("cartoncillo", 0.0)), c_cart_dorso,
                            f"{hp_papel_d} hojas × {m2_papel:g} m² × {p.get('gd', 0)} g/m²")

                    peg_rate = _get_contracolado_rate_m2(p, db, f_narba)
                    if capas_contracolado > 0 and m2_papel > 0:
                        c_contracolado = hp_produccion * m2_papel * peg_rate * capas_contracolado
                        _aud_linea(aud_lineas, "Contracolado a mano" if p.get("contracolado_a_mano") else "Contracolado", "Proceso",
                            hp_produccion * m2_papel * capas_contracolado, "m²", _get_contracolado_rate_m2(p, db, 1.0),
                            float(db_desc.get("narba", 0.0)), c_contracolado, f"{capas_contracolado} capas × {hp_produccion} hojas × {m2_papel:g} m²")

                    c_imp_cara = 0.0
                    c_imp_dorso = 0.0

                    # FR24: tinta especial con coste extra por m² impreso.
                    fr24_enabled = bool(p.get("fr24", False))
                    try:
                        fr24_rate = float(p.get("fr24_rate", 0.05))
                    except Exception:
                        fr24_rate = 0.05
                    fr24_m2_total = 0.0

                    # Impresión (multi-tirada): el coste se calcula por cada impresión (tirada).
                    # La merma de impresión se aplica por tirada según la cantidad seleccionada.
                    if p.get("im","No") == "Digital":
                        for q_run in (partes_imp_units if partes_imp_units else [int(q_n)]):
                            nb_run = int(q_run) * float(p.get("pliegos", 1.0))
                            hp_imp_run = nb_run + merma_imp_digital_hojas
                            coste_tirada = hp_imp_run * m2_papel * _tarifa("impresion_digital", "precio_m2")
                            c_imp_cara += coste_tirada
                            _aud_linea(aud_lineas, "Impresión digital cara", "Proceso", hp_imp_run * m2_papel, "m²",
                                _tarifa("impresion_digital", "precio_m2"), 0.0, coste_tirada,
                                f"Tirada {q_run} expositores · {nb_run:g} hojas netas + {merma_imp_digital_hojas} de merma")
                            if fr24_enabled and m2_papel > 0:
                                fr24_m2_total += hp_imp_run * m2_papel
                            if bool(p.get("ld", False)):
                                coste_laminado = hp_imp_run * m2_papel * float(db.get("laminado_digital", 3.5))
                                c_pel_total += coste_laminado
                                _aud_linea(aud_lineas, "Laminado digital cara", "Proceso", hp_imp_run * m2_papel, "m²",
                                    float(db.get("laminado_digital", 3.5)), 0.0, coste_laminado, f"Tirada {q_run} expositores · incluye merma digital")
                    elif p.get("im","No") == "Offset":
                        tintas_cara = int(p.get("nt",0)) + (1 if bool(p.get("ba",False)) else 0)
                        for q_run in (partes_imp_units if partes_imp_units else [int(q_n)]):
                            nb_run = int(round(int(q_run) * float(p.get("pliegos", 1.0))))
                            coste_tinta = coste_offset_por_tinta(int(nb_run))
                            coste_tirada = coste_tinta * tintas_cara
                            c_imp_cara += coste_tirada
                            _aud_linea(aud_lineas, "Impresión offset cara", "Proceso", tintas_cara, "tintas/barniz",
                                coste_tinta, 0.0, coste_tirada,
                                f"Tirada {q_run} expositores · {nb_run} hojas · coste por tinta según tramo offset")
                            if fr24_enabled and m2_papel > 0:
                                fr24_m2_total += nb_run * m2_papel

                    if p.get("im_d","No") == "Digital":
                        for q_run in (partes_imp_units if partes_imp_units else [int(q_n)]):
                            nb_run = int(q_run) * float(p.get("pliegos", 1.0))
                            hp_imp_run = nb_run + merma_imp_digital_hojas
                            coste_tirada = hp_imp_run * m2_papel * _tarifa("impresion_digital", "precio_m2")
                            c_imp_dorso += coste_tirada
                            _aud_linea(aud_lineas, "Impresión digital dorso", "Proceso", hp_imp_run * m2_papel, "m²",
                                _tarifa("impresion_digital", "precio_m2"), 0.0, coste_tirada,
                                f"Tirada {q_run} expositores · {nb_run:g} hojas netas + {merma_imp_digital_hojas} de merma")
                            if fr24_enabled and m2_papel > 0:
                                fr24_m2_total += hp_imp_run * m2_papel
                            if bool(p.get("ld_d", False)):
                                coste_laminado = hp_imp_run * m2_papel * float(db.get("laminado_digital", 3.5))
                                c_pel_total += coste_laminado
                                _aud_linea(aud_lineas, "Laminado digital dorso", "Proceso", hp_imp_run * m2_papel, "m²",
                                    float(db.get("laminado_digital", 3.5)), 0.0, coste_laminado, f"Tirada {q_run} expositores · incluye merma digital")
                    elif p.get("im_d","No") == "Offset":
                        tintas_dorso = int(p.get("nt_d",0)) + (1 if bool(p.get("ba_d",False)) else 0)
                        for q_run in (partes_imp_units if partes_imp_units else [int(q_n)]):
                            nb_run = int(round(int(q_run) * float(p.get("pliegos", 1.0))))
                            coste_tinta = coste_offset_por_tinta(int(nb_run))
                            coste_tirada = coste_tinta * tintas_dorso
                            c_imp_dorso += coste_tirada
                            _aud_linea(aud_lineas, "Impresión offset dorso", "Proceso", tintas_dorso, "tintas/barniz",
                                coste_tinta, 0.0, coste_tirada,
                                f"Tirada {q_run} expositores · {nb_run} hojas · coste por tinta según tramo offset")
                            if fr24_enabled and m2_papel > 0:
                                fr24_m2_total += nb_run * m2_papel

                    c_imp_total = c_imp_cara + c_imp_dorso

                    c_fr24 = 0.0
                    if fr24_enabled and fr24_rate > 0 and fr24_m2_total > 0:
                        c_fr24 = fr24_m2_total * fr24_rate
                        c_imp_total += c_fr24
                        _aud_linea(aud_lineas, "Tinta especial FR24", "Proceso", fr24_m2_total, "m²", fr24_rate, 0.0, c_fr24)

                    c_pel_cara = 0.0
                    c_pel_dorso = 0.0
                    if p.get("pel","Sin Peliculado") != "Sin Peliculado":
                        c_pel_cara = hp_produccion * m2_papel * float(db["peliculado"][p["pel"]]) * f_narba
                        _aud_linea(aud_lineas, f"Peliculado cara · {p['pel']}", "Proceso", hp_produccion * m2_papel, "m²",
                            float(db["peliculado"][p["pel"]]), float(db_desc.get("narba", 0.0)), c_pel_cara)
                    if p.get("pd","Ninguno") != "Ninguno" and p.get("pel_d","Sin Peliculado") != "Sin Peliculado":
                        c_pel_dorso = hp_produccion * m2_papel * float(db["peliculado"][p["pel_d"]]) * f_narba
                        _aud_linea(aud_lineas, f"Peliculado dorso · {p['pel_d']}", "Proceso", hp_produccion * m2_papel, "m²",
                            float(db["peliculado"][p["pel_d"]]), float(db_desc.get("narba", 0.0)), c_pel_dorso)
                    c_pel_total += (c_pel_cara + c_pel_dorso)

                    cor_sel = p.get("cor_default", "Troquelado")
                    if isinstance(p.get("cor_by_qty", {}), dict):
                        cor_sel = p["cor_by_qty"].get(str(q_n), cor_sel)

                    cat = "Grande (> 1000x700)" if (h>1000 or w>700) else ("Pequeño (< 1000x700)" if (h<1000 and w<700) else "Mediano (Estándar)")
                    c_troquel_taller = 0.0
                    c_plotter = 0.0

                    # Pre-cálculo para corte (Troquelado/Plotter):
                    # - Evita NameError (hp_corte siempre definido).
                    # - Aplica el ajuste manual "piezas por troquel" también al Plotter.
                    hp_corte = int(math.ceil(float(hp_produccion)))
                    auto_piezas = 1
                    troquel_piezas_manual = int(p.get("troquel_piezas", 0) or 0)
                    stamping_enabled = bool(p.get("stamping", False))
                    if cor_sel in ("Troquelado", "Plotter") or stamping_enabled:
                        try:
                            _pl_tmp = float(p.get("pliegos", 1.0) or 1.0)
                            if _pl_tmp > 0 and _pl_tmp < 1.0:
                                auto_piezas = max(1, int(round(1.0 / _pl_tmp)))
                        except Exception:
                            auto_piezas = 1
                        if troquel_piezas_manual <= 0:
                            troquel_piezas_manual = auto_piezas
                        troquel_factor = float(auto_piezas) / float(max(1, troquel_piezas_manual))
                        hp_corte = int(math.ceil(float(hp_produccion) * troquel_factor))

                    if cor_sel == "Troquelado":
                        arr = float(db["troquelado"][cat]["arranque"]) * f_narba if bool(p.get("cobrar_arreglo", True)) else 0.0
                        tiro = float(db["troquelado"][cat]["tiro"]) * f_narba
                        c_troquel_taller = arr + (hp_corte * tiro)
                        if bool(p.get("cobrar_arreglo", True)):
                            _aud_linea(aud_lineas, "Troquelado · arranque", "Proceso", 1, "arranque",
                                float(db["troquelado"][cat]["arranque"]), float(db_desc.get("narba", 0.0)), arr, cat)
                        _aud_linea(aud_lineas, "Troquelado · tiro", "Proceso", hp_corte, "hojas",
                            float(db["troquelado"][cat]["tiro"]), float(db_desc.get("narba", 0.0)), hp_corte * tiro, cat)
                    elif cor_sel == "Plotter":
                        c_plotter = hp_corte * float(db["plotter"]["precio_hoja"])
                        _aud_linea(aud_lineas, "Corte plotter", "Proceso", hp_corte, "hojas", float(db["plotter"]["precio_hoja"]), 0.0, c_plotter)
                    else:
                        # "Sin corte": no suma coste de troquel ni plotter
                        pass

                    # Stamping (si aplica): arreglo + pisadas + película (m²)
                    if bool(p.get("stamping", False)):
                        try:
                            sw = float(p.get("stamping_w", 0) or 0)
                            sh = float(p.get("stamping_h", 0) or 0)
                        except Exception:
                            sw, sh = 0.0, 0.0
                        area_m2 = max(0.0, (sw/1000.0) * (sh/1000.0))
                        arr_s = float(db.get("stamping", {}).get("arreglo", 168.0)) if bool(p.get("stamping_cobrar_arreglo", True)) else 0.0
                        pisada = float(db.get("stamping", {}).get("pisada", 0.21))
                        peli = float(db.get("stamping", {}).get("pelicula_m2", 0.39))
                        c_stamping = arr_s + (hp_corte * pisada) + (hp_corte * area_m2 * peli)
                        if bool(p.get("stamping_cobrar_arreglo", True)):
                            _aud_linea(aud_lineas, "Stamping · arreglo", "Proceso", 1, "arreglo", arr_s, 0.0, arr_s)
                        _aud_linea(aud_lineas, "Stamping · pisadas", "Proceso", hp_corte, "pisadas", pisada, 0.0, hp_corte * pisada)
                        _aud_linea(aud_lineas, "Stamping · película", "Proceso", hp_corte * area_m2, "m²", peli, 0.0,
                            hp_corte * area_m2 * peli, f"{sw:g} × {sh:g} mm por pisada")
                        if sw <= 0 or sh <= 0:
                            aud_avisos.append("Stamping activo sin superficie completa: la película queda a cero.")

                    sub = c_cart_cara + c_cart_dorso + c_ondulado + c_rigido + c_contracolado + c_imp_total + c_pel_total + c_troquel_taller + c_plotter + c_stamping
                    coste_f += sub
                    if w <= 0 or h <= 0:
                        aud_avisos.append("Formato incompleto; revisar las medidas de la forma.")
                    if has_cart_cara and float(p.get("gf", 0)) <= 0:
                        aud_avisos.append("Cartoncillo cara seleccionado sin gramaje válido.")
                    if has_cart_dorso and float(p.get("gd", 0)) <= 0:
                        aud_avisos.append("Cartoncillo dorso seleccionado sin gramaje válido.")
                    if im_cara == "Offset" and int(p.get("nt", 0)) <= 0 and not p.get("ba", False):
                        aud_avisos.append("Impresión offset cara seleccionada sin tintas ni barniz.")
                    if im_dorso == "Offset" and int(p.get("nt_d", 0)) <= 0 and not p.get("ba_d", False):
                        aud_avisos.append("Impresión offset dorso seleccionada sin tintas ni barniz.")
                    if fr24_enabled and fr24_rate <= 0:
                        aud_avisos.append("FR24 activa con tarifa cero o negativa; confirmar que es intencionada.")
                    if has_base_rigido and c_rigido == 0:
                        aud_avisos.append("Rígido seleccionado sin coste: revisar hoja, encaje, tarifa y descuento.")
                    for linea in aud_lineas:
                        if linea["Consumo"] > 0 and linea["Tarifa (€)"] <= 0:
                            aud_avisos.append(f"{linea['Concepto']}: tarifa cero o negativa; confirmar que es intencionada.")
                    if float(p.get("pv_troquel", 0.0)) > 0:
                        aud_venta.append({"Concepto": f"Troquel de venta · Forma {pid} · {p.get('nombre', '')}",
                                          "Importe de venta (€)": float(p["pv_troquel"])})
                    aud_formas.append({"id": int(pid), "nombre": p.get("nombre", ""),
                        "formato": f"{max(h, w):g} × {min(h, w):g}", "pliegos": pl,
                        "hojas_netas": nb, "merma_proceso": int(merma_proc_hojas), "hojas_produccion": hp_produccion,
                        "merma_cara": merma_cara, "merma_dorso": merma_d, "tiradas": n_impresiones_qty,
                        "pisadas": hp_corte, "lineas": aud_lineas, "avisos": aud_avisos, "coste_total": sub})

                    det_f.append({
                        "Pieza": p.get("nombre",""),
                        "Cartoncillo Cara": c_cart_cara,
                        "Cartoncillo Dorso": c_cart_dorso,
                        "Plancha Ondulado": c_ondulado,
                        "Material Rígido": c_rigido,
                        "Contracolado": c_contracolado,
                        "Contracolado a mano": bool(p.get("contracolado_a_mano", False)),
                        "Impresión": c_imp_total,
                        "Peliculado": c_pel_total,
                        "Corte (Troquel/Plotter)": c_troquel_taller + c_plotter,
                        "Stamping": c_stamping,
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
                    tot_cat["procesos"]["stamping"] += c_stamping

                c_ext = sum(float(e.get("coste",0.0)) * float(e.get("cantidad",1.0)) * q_n for e in st.session_state.lista_extras_grabados)
                tot_cat["materiales"]["extras"] += c_ext
                for extra in st.session_state.lista_extras_grabados:
                    consumo_extra = float(extra.get("cantidad", 1.0)) * q_n
                    precio_extra = float(extra.get("coste", 0.0))
                    _aud_linea(aud_otras, f"Extra · {extra.get('nombre', '')}", "Material", consumo_extra,
                        "ud", precio_extra, 0.0, precio_extra * float(extra.get("cantidad", 1.0)) * q_n)

                c_mo_man = (seg_man_total/3600.0)*_tarifa("mano_obra", "manipulado_hora")*q_n
                c_mo_dif = (q_n * float(dif_ud))
                c_mo = c_mo_man + c_mo_dif
                tot_cat["procesos"]["manipulacion"] += c_mo_man
                tot_cat["procesos"]["dificultad"] += c_mo_dif
                if seg_man_total or c_mo_man:
                    _aud_linea(aud_otras, "Manipulado", "Proceso", seg_man_total / 3600.0 * q_n,
                        "horas", _tarifa("mano_obra", "manipulado_hora"), 0.0, c_mo_man)
                if dif_ud or c_mo_dif:
                    _aud_linea(aud_otras, "Dificultad", "Proceso", q_n, "expositores", float(dif_ud), 0.0, c_mo_dif)

                # Opcionales (a parte): Rellenado + Armado (se muestran como opción al cliente)
                # Se calcula un PVP opcional aplicando el mismo margen de trabajo (st.session_state.margen).
                # Se guardan también los costes base sin margen para uso interno / compatibilidad.
                margen_trabajo = float(st.session_state.margen) if "margen" in st.session_state else 1.0

                c_opt_rell_coste = (seg_rell_total/3600.0)*_tarifa("mano_obra", "rellenado_hora")*q_n if bool(st.session_state.rell_enabled) else 0.0
                c_opt_arm_coste = (seg_arm_total/3600.0)*_tarifa("mano_obra", "armado_hora")*q_n if bool(st.session_state.arm_enabled) else 0.0

                if st.session_state.rell_enabled:
                    _aud_linea(aud_opcionales, "Rellenado", "Opcional", seg_rell_total / 3600.0 * q_n,
                        "horas", _tarifa("mano_obra", "rellenado_hora"), 0.0, c_opt_rell_coste)
                if st.session_state.arm_enabled:
                    _aud_linea(aud_opcionales, "Armado", "Opcional", seg_arm_total / 3600.0 * q_n,
                        "horas", _tarifa("mano_obra", "armado_hora"), 0.0, c_opt_arm_coste)

                c_opt_rell_pvp = c_opt_rell_coste * margen_trabajo
                c_opt_arm_pvp = c_opt_arm_coste * margen_trabajo

                opcionales_cost = {
                    # Valores que se muestran al cliente (con margen)
                    "rellenado_total": float(c_opt_rell_pvp),
                    "armado_total": float(c_opt_arm_pvp),
                    "rellenado_unit": float(c_opt_rell_pvp / q_n) if q_n > 0 else 0.0,
                    "armado_unit": float(c_opt_arm_pvp / q_n) if q_n > 0 else 0.0,
                    # Costes internos sin margen
                    "rellenado_total_coste": float(c_opt_rell_coste),
                    "armado_total_coste": float(c_opt_arm_coste),
                    "rellenado_unit_coste": float(c_opt_rell_coste / q_n) if q_n > 0 else 0.0,
                    "armado_unit_coste": float(c_opt_arm_coste / q_n) if q_n > 0 else 0.0,
                    "margen_aplicado": float(margen_trabajo),
                }

                emb_compra_total = 0.0
                emb_det = []
                for emb in st.session_state.embalajes:
                    # Embalajes pueden ser por caja (varias uds dentro). En ese caso el coste es por CAJA.
                    try:
                        uds_por_caja = int(float(emb.get("uds_por_caja", 1) or 1))
                    except Exception:
                        uds_por_caja = 1
                    uds_por_caja = max(1, int(uds_por_caja))

                    cu_caja = float(emb.get("costes", {}).get(q_n, 0.0))
                    n_cajas = int(math.ceil(q_n / float(uds_por_caja))) if q_n > 0 else 0

                    emb_compra_total += cu_caja * n_cajas
                    if cu_caja or emb.get("tipo", "Manual") != "Manual" or any(float(v or 0) > 0 for v in emb.get("dims", {}).values()):
                        _aud_linea(aud_otras, f"Embalaje · {emb.get('nombre', '')}", "Material", n_cajas,
                            "cajas", cu_caja, 0.0, cu_caja * n_cajas,
                            f"{emb.get('tipo', '')} · {emb.get('material', '')} · {uds_por_caja} expositores/caja")
                    emb_det.append({
                        "nombre": emb.get("nombre",""),
                        "tipo": emb.get("tipo",""),
                        "material": emb.get("material",""),
                        "uds_por_caja": uds_por_caja,
                        "cajas": n_cajas,
                        "coste_caja_compra": cu_caja,
                        "coste_total_compra": float(cu_caja * n_cajas),
                        "coste_unit_compra": float((cu_caja * n_cajas) / q_n) if q_n > 0 else 0.0,
                    })

                # ✅ Venta de embalajes por opción (para mostrar en oferta si hay varias opciones)
                pv_emb_por_embalaje = []
                for j, emb in enumerate(st.session_state.embalajes):
                    nombre_emb = str(emb.get("nombre", "")).strip() or f"EMB_{j+1}"
                    try:
                        uds_por_caja = int(float(emb.get("uds_por_caja", 1) or 1))
                    except Exception:
                        uds_por_caja = 1
                    uds_por_caja = max(1, int(uds_por_caja))

                    cu_compra = float(emb.get("costes", {}).get(q_n, 0.0))  # €/caja (o €/ud si uds_por_caja=1)
                    n_cajas = int(math.ceil(q_n / float(uds_por_caja))) if q_n > 0 else 0

                    pv_caja = cu_compra * margen_embalajes
                    pv_tot = pv_caja * n_cajas
                    pv_unit = (pv_tot / q_n) if q_n > 0 else 0.0
                    nombre_key = re.sub(r"[\r\n\t]+", " ", nombre_emb)
                    pv_emb_por_embalaje.append({
                        "nombre": nombre_key,
                        "unit": pv_unit,
                        "uds_por_caja": uds_por_caja,
                        "cajas": n_cajas,
                        "pv_caja": pv_caja,
                        "total": pv_tot,
                    })

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
                    if val or str(ext.get("concepto", "")).strip() not in ("", "Externo 1"):
                        _aud_linea(aud_otras, f"Externo · {ext.get('concepto', '')}", "Proceso", q_n if tipo == "unitario" else 1,
                            "expositores" if tipo == "unitario" else "trabajo", val, 0.0, coste)
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

                # ✅ PV troquel (venta): solo debe imputarse a las cantidades que realmente van a TROQUELADO.
                # Si una cantidad va a Plotter (o Sin corte), NO debe cargar el coste del troquel en el sumatorio.
                tot_pv_trq = 0.0
                for _pid, _pz in st.session_state.piezas_dict.items():
                    _cor_sel = _pz.get("cor_default", "Troquelado")
                    if isinstance(_pz.get("cor_by_qty", {}), dict):
                        _cor_sel = _pz["cor_by_qty"].get(str(q_n), _cor_sel)
                    if str(_cor_sel) == "Troquelado":
                        try:
                            tot_pv_trq += float(_pz.get("pv_troquel", 0.0) or 0.0)
                        except Exception:
                            pass

                pvp_total_todo = pv_producido_total + pv_extras_total + pv_emb_total + tot_pv_trq
                unit_todo = pvp_total_todo / q_n

                # Unitario sin troquel: producido + embalaje + extras
                pvp_prod_emb_extras = pv_producido_total + pv_emb_total + pv_extras_total
                unit_prod_emb_extras = pvp_prod_emb_extras / q_n if q_n > 0 else 0.0

                res_final.append({
                    "Cantidad": q_n,
                    "Precio venta material (unitario)": f"{_formato_precio_venta(pv_material_unit)}",
                    "Precio venta extras (unitario)": f"{_formato_precio_venta(pv_extras_unit)}",
                    "Precio venta embalaje (unitario)": f"{_formato_precio_venta((pv_emb_total/q_n))}",
                    "Precio venta troquel (TOTAL)": f"{_formato_precio_venta(tot_pv_trq)}",
                    "Precio venta unitario (prod+emb+extras)": f"{_formato_precio_venta(unit_prod_emb_extras)}",
                    "Precio venta unitario (todo)": f"{_formato_precio_venta(unit_todo)}",
                    "Precio venta total": f"{_formato_precio_venta(pvp_total_todo)}"
                })

                desc_full[q_n] = {
                    "det_piezas": det_f,
                    "embalajes": emb_det,
                    "externos": ext_det,
                    "mermas": {"impresion_digital_hojas": merma_imp_digital_hojas, "procesos_por_forma": deepcopy(st.session_state.get("mermas_proc_manual", {})), "impresion_offset_por_forma": deepcopy(st.session_state.get("mermas_imp_manual", {}))},
                    "debug": debug_log
                }

                if imp_fijo_pvp:
                    aud_venta.append({"Concepto": "Desarrollo de proyecto (venta)", "Importe de venta (€)": float(imp_fijo_pvp)})
                aud_avisos_generales = [f"{l['Concepto']}: tarifa cero o negativa; confirmar que es intencionada."
                    for l in aud_otras + aud_opcionales if l["Consumo"] > 0 and l["Tarifa (€)"] <= 0]
                compras_legible[q_n] = {
                    "Cantidad": q_n,
                    "Materiales": tot_cat["materiales"],
                    "Procesos": tot_cat["procesos"],
                    "Detalle piezas": det_f,
                    "Detalle embalajes": emb_det,
                    "Detalle externos": ext_det,
                    "Extras (detalle)": st.session_state.lista_extras_grabados,
                    "Opcionales (a parte)": opcionales_cost,
                    "Auditoría compras": {
                        "version": 1, "cantidad": q_n, "formas": aud_formas, "otras_partidas": aud_otras,
                        "opcionales": aud_opcionales, "referencias_venta": aud_venta,
                        "avisos": aud_avisos_generales,
                        "proyecto": {"briefing": st.session_state.brf, "cliente": st.session_state.cli,
                                     "descripcion": st.session_state.desc},
                        "coste_total": float(sum(tot_cat["materiales"].values()) + sum(tot_cat["procesos"].values()))
                    }
                }

                resumen_costes_export[q_n] = {
                    "Cantidad": q_n,
                    "materiales": {k: round(v, 4) for k, v in tot_cat["materiales"].items()},
                    "procesos": {k: round(v, 4) for k, v in tot_cat["procesos"].items()},
                    "totales": {
                        "materiales_total": round(sum(tot_cat["materiales"].values()), 4),
                        "procesos_total": round(sum(tot_cat["procesos"].values()), 4),
                        "coste_total_compra_estimado": round(sum(tot_cat["materiales"].values()) + sum(tot_cat["procesos"].values()), 4)
                    },
                    "opcionales_a_parte": {
                        # Valores mostrados al cliente (con margen)
                        "rellenado_total": float(opcionales_cost.get("rellenado_total", 0.0)),
                        "armado_total": float(opcionales_cost.get("armado_total", 0.0)),
                        "rellenado_unit": float(opcionales_cost.get("rellenado_unit", 0.0)),
                        "armado_unit": float(opcionales_cost.get("armado_unit", 0.0)),
                        # Costes internos sin margen
                        "rellenado_total_coste": round(opcionales_cost.get("rellenado_total_coste", 0.0), 4),
                        "armado_total_coste": round(opcionales_cost.get("armado_total_coste", 0.0), 4),
                        "rellenado_unit_coste": round(opcionales_cost.get("rellenado_unit_coste", 0.0), 6),
                        "armado_unit_coste": round(opcionales_cost.get("armado_unit_coste", 0.0), 6),
                        "margen_aplicado": round(opcionales_cost.get("margen_aplicado", float(st.session_state.margen)), 4)
                    },
                    "embalajes_venta_por_opcion": [
                        {
                            "nombre": e.get("nombre",""),
                            "unit": float(e.get("unit", 0.0)),
                            "total": float(e.get("total", 0.0)),
                        }
                        for e in (pv_emb_por_embalaje if isinstance(pv_emb_por_embalaje, list) else [])
                    ]
                }

        for _compra in compras_legible.values():
            _compra["Auditoría compras"]["firma"] = _calc_project_signature()

        # --- Guardar caché del cálculo (para evitar recompute en cada rerun) ---
        st.session_state._calc_cache = {
            "_precios_venta_version": 1,
            "res_final": res_final,
            "desc_full": desc_full,
            "compras_legible": compras_legible,
            "resumen_costes_export": resumen_costes_export,
        }
        try:
            st.session_state._calc_last_signature = _calc_project_signature()
        except Exception:
            st.session_state._calc_last_signature = None
        st.session_state._calc_requested = False
        st.session_state._calc_status = "OK" if (isinstance(res_final
, list) and len(res_final) > 0) else "Sin datos"

safe_brf = re.sub(r'[\/*?:"<>|]', "", st.session_state.brf or "Ref").replace(" ", "_")
safe_ver = re.sub(r'[\/*?:"<>|]', "", str(st.session_state.get("version_presupuesto", "") or "")).replace(" ", "_")
safe_cli = re.sub(r'[\/*?:"<>|]', "", st.session_state.cli or "Cli").replace(" ", "_")
safe_desc = re.sub(r'[\/*?:"<>|]', "", st.session_state.desc or "Oferta").replace(" ", "_")
# Incluir nº(s) de comercial en el nombre de archivo (si están informados)
c1_num = _parse_comercial_num(st.session_state.get('comercial_1', ''))
c2_num = _parse_comercial_num(st.session_state.get('comercial_2', ''))
com_parts = []
if c1_num is not None:
    com_parts.append(f"C{c1_num}")
if c2_num is not None:
    com_parts.append(f"C{c2_num}")
com_tag = "_".join(com_parts)
brf_tag = f"{safe_brf}_{safe_ver}" if safe_ver else safe_brf
if com_tag:
    st.session_state._export_filename = f"{brf_tag}_{com_tag}_{safe_cli}_{safe_desc}.json"
else:
    st.session_state._export_filename = f"{brf_tag}_{safe_cli}_{safe_desc}.json"

resumen_compra_to_export = compras_legible if isinstance(compras_legible, dict) and len(compras_legible) > 0 else st.session_state.get("_imported_compras_legible")

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
  <div class='comercial-ref'>Ref. Briefing: {st.session_state.brf or '-'}{(' · Versión: ' + str(st.session_state.get('version_presupuesto', '')).strip()) if str(st.session_state.get('version_presupuesto', '')).strip() else ''}</div>
  {desc_html}
  {extras_html}
  {emb_html}
  {ext_html}
  {tabla_html}
</div>
</body>
</html>
"""

with tab_calculadora:
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

        # Opcionales (a parte)
        if bool(st.session_state.rell_enabled) or bool(st.session_state.arm_enabled):
            opt_lines = []
            if bool(st.session_state.rell_enabled):
                opt_lines.append(f"<span class='tag'>Rellenado</span><span class='small muted'>+ {seg_rell_total:g} seg/ud</span>")
            if bool(st.session_state.arm_enabled):
                opt_lines.append(f"<span class='tag'>Armado</span><span class='small muted'>+ {seg_arm_total:g} seg/ud</span>")
            desc_html += "<div style='margin-bottom:10px;'>"
            desc_html += "<span class='tag'>Opcionales</span> "
            desc_html += " &nbsp; ".join(opt_lines)
            desc_html += "</div>"


        # Notas / comentarios (solo si hay texto)
        _notas_txt = (st.session_state.get("notas", "") or "").strip()
        if _notas_txt:
            _notas_html = html.escape(_notas_txt).replace("\n", "<br>")
            desc_html += "<div style='margin-top:10px;'><span class='tag'>Notas</span></div>"
            desc_html += f"<div class='small' style='margin-top:6px; line-height:1.35;'>{_notas_html}</div>"

        for pid, p in st.session_state.piezas_dict.items():
            base_info = ""
            if p.get("tipo_base") == "Material Rígido":
                if bool(p.get("rig_manual", False)):
                    base_info = f"Rígido Manual: {int(p.get('rig_w',0))}×{int(p.get('rig_h',0))} mm"
                else:
                    base_info = f"Rígido: {p.get('mat_rigido','')}"
            else:
                base_info = f"Ondulado: {p.get('pl','')} ({p.get('ap','')})"

            flexo_txt = " | Flexografía" if bool(p.get("flexografia", False)) else ""
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
            trq = f"{_formato_precio_venta(float(p.get('pv_troquel',0.0)))}"

            # Varias impresiones (solo si está activado para esta forma) -> mostrar en oferta
            impresiones_info_html = ""
            enabled_all = st.session_state.get("impresiones_by_qty_fmt_enabled", {})
            enabled_fmt = False
            if isinstance(enabled_all, dict):
                enabled_fmt = bool(enabled_all.get(str(int(pid)), False))
            if enabled_fmt:
                q_list = []
                try:
                    q_list = [int(r.get("Cantidad", 0)) for r in res_final if int(r.get("Cantidad", 0)) > 0]
                except Exception:
                    q_list = []
                lines = []
                for qv in q_list:
                    partes = obtener_partes_impresion_por_formato(int(pid), int(qv))
                    if isinstance(partes, list) and len(partes) > 1:
                        try:
                            parts_txt = "+".join(str(int(x)) for x in partes)
                        except Exception:
                            parts_txt = "+".join(str(x) for x in partes)
                        lines.append(f"{int(qv)} uds → {parts_txt}")
                if lines:
                    impresiones_info_html = "<br><b>Varias impresiones:</b> " + " &nbsp;|&nbsp; ".join(lines)


            desc_html += (
                "<div style='margin-bottom:8px;'>"
                f"<span class='tag'>{p.get('nombre','')}</span>"
                f"<span class='small muted'>{int(p.get('h',0))}×{int(p.get('w',0))} mm | Pliegos/ud: {float(p.get('pliegos',1.0)):.4f}</span>"
                "<div class='small'>"
                f"<b>Soporte:</b> {base_info}{flexo_txt}<br>"
                f"<b>Cara:</b> {cara} | <b>Imp:</b> {imp_c}{tintas_c} | <b>Pel:</b> {pel_c}<br>"
                f"<b>Dorso:</b> {dorso} | <b>Imp:</b> {imp_d}{tintas_d} | <b>Pel:</b> {pel_d}<br>"
                f"<b>Corte (def):</b> {corte} | <b>Troquel (venta):</b> {trq}" + impresiones_info_html + "</div></div>"
            )
        desc_html += "</div>"

        extras_html = "<div class='sec-title'>➕ Materiales extra</div><div class='card'>"
        if st.session_state.lista_extras_grabados:
            for e in st.session_state.lista_extras_grabados:
                extras_html += f"<div class='small'>• <b>{e.get('nombre','')}</b> — {float(e.get('cantidad',1.0))} /ud</div>"
        else:
            extras_html += "<div class='small muted'>Sin extras.</div>"
        extras_html += "</div>"

        emb_html = "<div class='sec-title'>📦 Embalajes</div><div class='card'>"
        emb_html += "<div class='small muted'>El precio de embalaje mostrado en la tabla es <b>€/ud repercutido</b>. Si un embalaje es multipack (p.ej. 5 uds/caja), el <b>precio de venta por caja</b> es (€/ud × uds/caja).</div>"
        for emb in st.session_state.embalajes:
            L, W, H = emb["dims"].get("L",0), emb["dims"].get("W",0), emb["dims"].get("H",0)
            try:
                upc = int(emb.get("uds_por_caja", 1) or 1)
            except Exception:
                upc = 1
            upc = max(1, upc)
            upc_txt = f" — <b>{upc} uds/caja</b>" if upc > 1 else ""
            emb_html += (
                f"<div class='small'>• <b>{emb.get('nombre','')}</b> — {emb.get('tipo','')} — {emb.get('material','')} — "
                f"{L:.0f}×{W:.0f}×{H:.0f} mm{upc_txt}</div>"
            )
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
                f"<td>{r.get('Precio venta extras (unitario)', '0.00€')}</td>"
                f"<td>{r['Precio venta embalaje (unitario)']}</td>"
                f"<td>{r['Precio venta troquel (TOTAL)']}</td>"
                f"<td>{r.get('Precio venta unitario (prod+emb+extras)', '0.00€')}</td>"
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


        # Opciones de embalaje (si hay más de 1)
        emb_opts_html = ""
        try:
            if isinstance(st.session_state.embalajes, list) and len(st.session_state.embalajes) > 1:
                # Mapa por nombre para encontrar uds/caja
                _emb_by_name = {}
                for _e in st.session_state.embalajes:
                    try:
                        _emb_by_name[str(_e.get("nombre",""))] = _e
                    except Exception:
                        pass

                emb_opts_html += "<div class='sec-title'>📦 Opciones de embalaje</div>"
                emb_opts_html += "<div class='card'>"
                emb_opts_html += "<div class='small muted'>Precios de embalaje por opción. El valor mostrado es <b>€/ud repercutido</b>; si es multipack, también se indica el <b>€/caja</b> (€/ud × uds/caja).</div>"
                for q in sorted(resumen_costes_export.keys()):
                    emb_opts_html += f"<div style='margin-top:10px; font-weight:700;'>Cantidad: {int(q)} uds</div>"
                    emb_opts_html += "<table class='comercial-table' style='margin-top:6px;'>"
                    emb_opts_html += "<tr><th>Embalaje</th><th>Uds/caja</th><th>€/ud (repercutido)</th><th>€/caja</th><th>Total</th></tr>"
                    opts = (resumen_costes_export.get(q, {}) or {}).get("embalajes_venta_por_opcion", [])
                    if isinstance(opts, list) and opts:
                        for opt in opts:
                            nom = str(opt.get("nombre",""))
                            unit = float(opt.get("unit", 0.0) or 0.0)
                            total = float(opt.get("total", 0.0) or 0.0)
                            upc = 1
                            try:
                                e0 = _emb_by_name.get(nom, None)
                                if isinstance(e0, dict):
                                    upc = int(e0.get("uds_por_caja", 1) or 1)
                            except Exception:
                                upc = 1
                            upc = max(1, upc)
                            caja = unit * upc
                            emb_opts_html += (
                                f"<tr><td>{html.escape(nom)}</td>"
                                f"<td>{upc}</td>"
                                f"<td>{_formato_precio_venta(unit)}</td>"
                                f"<td>{_formato_precio_venta(caja)}</td>"
                                f"<td>{_formato_precio_venta(total)}</td></tr>"
                            )
                    emb_opts_html += "</table>"
                emb_opts_html += "</div>"
        except Exception:
            emb_opts_html = ""

        # Opcionales (a parte) - tabla
        opc_html = ""
        if bool(st.session_state.rell_enabled) or bool(st.session_state.arm_enabled):
            opc_html += "<div class='sec-title'>🧩 Opcionales (a parte)</div>"
            opc_html += "<div class='card'>"
            opc_html += f"<div class='small muted'>Precios opcionales NO incluidos en el precio mostrado.</div>"
            opc_html += "<table class='comercial-table' style='margin-top:10px;'>" \
                       "<tr><th>Cantidad</th><th>Rellenado (€/ud)</th><th>Rellenado (TOTAL)</th><th>Armado (€/ud)</th><th>Armado (TOTAL)</th></tr>"
            for row in resumen_costes_export.values():
                q = int(row.get("Cantidad", 0))
                op = row.get("opcionales_a_parte", {}) or {}
                opc_html += f"<tr><td>{q}</td><td>{_formato_precio_venta(float(op.get('rellenado_unit',0.0)))}</td><td>{_formato_precio_venta(float(op.get('rellenado_total',0.0)))}</td><td>{_formato_precio_venta(float(op.get('armado_unit',0.0)))}</td><td>{_formato_precio_venta(float(op.get('armado_total',0.0)))}</td></tr>"
            opc_html += "</table></div>"

    
        # PERFORMANCE: reutilizar oferta HTML del último cálculo si existe
        if isinstance(st.session_state.get("_calc_cache"), dict) and st.session_state._calc_cache.get("_salida_comercial_version") == 2 and "oferta_html" in st.session_state._calc_cache and not bool(st.session_state.get("_calc_requested", False)):
            oferta_html = st.session_state._calc_cache.get("oferta_html", "")
            fname_html = st.session_state._calc_cache.get("fname_html", "oferta.html")
        else:
            oferta_html = build_comercial_html(res_final, desc_html, extras_html, emb_html, (ext_html + emb_opts_html + opc_html), tabla)
            safe_desc = re.sub(r'[\/*?:"<>|]', "", st.session_state.desc or "Oferta").replace(" ", "_")
            safe_ver = re.sub(r'[\/*?:"<>|]', "", str(st.session_state.get("version_presupuesto", "") or "")).replace(" ", "_")
            brf_tag = f"{safe_brf}_{safe_ver}" if safe_ver else safe_brf
            # Incluir nº(s) de comercial en el nombre de archivo (si están informados)
            c1_num = _parse_comercial_num(st.session_state.get('comercial_1', ''))
            c2_num = _parse_comercial_num(st.session_state.get('comercial_2', ''))
            com_parts = []
            if c1_num is not None:
                com_parts.append(f"C{c1_num}")
            if c2_num is not None:
                com_parts.append(f"C{c2_num}")
            com_tag = "_".join(com_parts)
            if com_tag:
                fname_html = f"OFERTA_{brf_tag}_{com_tag}_{safe_cli}_{safe_desc}.html"
            else:
                fname_html = f"OFERTA_{brf_tag}_{safe_cli}_{safe_desc}.html"
        # Guardar oferta HTML en caché
        try:
            if not isinstance(st.session_state._calc_cache, dict) or st.session_state._calc_cache is None:
                st.session_state._calc_cache = {}
            st.session_state._calc_cache["oferta_html"] = oferta_html
            st.session_state._calc_cache["_salida_comercial_version"] = 2
            st.session_state._calc_cache["fname_html"] = fname_html
        except Exception:
            pass


        # Acceso rápido también en el panel lateral (sin quitar el botón de arriba)
        with st.sidebar:
            st.divider()
    

        # =========================================================
        # SIDEBAR: Descargas (OFERTA arriba, JSON abajo) - fiable 100%
        # =========================================================
    
        # Guardamos el resumen de compras y el resumen de costes en session_state para export JSON.
        # IMPORTANTE: esto debe ejecutarse en cada rerun después del cálculo, para que el JSON exportado
        # incluya siempre "compras_legible" y "resumen_costes" actualizados.
        try:
            if isinstance(globals().get("compras_legible", None), dict):
                st.session_state.compras_legible_export = deepcopy(globals().get("compras_legible", {}))
            else:
                st.session_state.compras_legible_export = {}
        except Exception:
            st.session_state.compras_legible_export = {}

        try:
            if isinstance(globals().get("resumen_costes_export", None), dict):
                st.session_state.resumen_costes_export = deepcopy(globals().get("resumen_costes_export", {}))
            else:
                st.session_state.resumen_costes_export = {}
        except Exception:
            st.session_state.resumen_costes_export = {}
    # Refrescamos caché de export antes de mostrar botones
        _refresh_export_cache_if_needed(force=False)

        _od_mostrar_guardado()

        with st.sidebar.expander("📄 Descargar oferta", expanded=True):
            st.download_button(
                "⬇️ Descargar OFERTA (HTML)",
                data=oferta_html.encode("utf-8"),
                file_name=fname_html,
                mime="text/html",
                use_container_width=True,
                key="dl_oferta_html_sidebar_top"
            )

        with st.sidebar.expander("📤 Exportar JSON", expanded=True):
            if st.session_state.get("_export_blob"):
                st.download_button(
                    "💾 Descargar JSON",
                    data=st.session_state._export_blob,
                    file_name=st.session_state._export_filename,
                    mime="application/json",
                    on_click=_mark_json_download,
                    use_container_width=True,
                    key="dl_json_sidebar_bottom"
                )
                if st.session_state.get("_json_downloaded", False):
                    st.success(f"✅ JSON descargado: {st.session_state.get('_json_downloaded_filename', '') or st.session_state._export_filename}")
            else:
                st.caption("Calcula una vez para habilitar la exportación.")

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
            f"{desc_html}{extras_html}{emb_html}{ext_html}{emb_opts_html}{opc_html}{tabla}"
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

    # =========================================================
    # TAB AUDITORÍA (SIEMPRE)
    # =========================================================
with tab_auditoria:
    _mostrar_auditoria_compras(compras_legible, resumen_costes_export)
