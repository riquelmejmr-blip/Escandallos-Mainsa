import streamlit as st
import pandas as pd

# --- 1. BASE DE DATOS DE PRECIOS ---
PRECIOS = {
    "cartoncillo": {
        "Ninguno": {"precio_kg": 0, "gramaje": 0},
        "Reverso Gris": {"precio_kg": 0.93, "gramaje": 220},
        "Zenith": {"precio_kg": 1.55, "gramaje": 350},
        "Reverso Madera": {"precio_kg": 0.95, "gramaje": 400},
        "Folding Kraft": {"precio_kg": 1.90, "gramaje": 340},
        "Folding Blanco": {"precio_kg": 1.82, "gramaje": 350}
    },
    "planchas": {
        "Ninguna": {"C/C": 0, "peg": 0},
        "Microcanal / Canal 3": {"C/C": 0.659, "B/C": 0.672, "B/B": 0.758, "peg": 0.217},
        "Doble Micro / Doble Doble": {"C/C": 1.046, "B/C": 1.1, "B/B": 1.276, "peg": 0.263},
        "AC (Cuero/Cuero)": {"C/C": 2.505, "peg": 0.217}
    },
    "peliculado": {
        "Sin Peliculado": 0, "Polipropileno": 0.26, "Poliéster brillo": 0.38, "Poliéster mate": 0.64
    },
    "laminado_digital": 3.5,
    "extras_base": ["CINTA D/CARA", "CINTA LOHMAN", "CINTA GEL", "GOMA TERMINALES", "IMAN 20x2mm", "TUBOS", "REMACHES", "VELCRO", "PUNTO ADHESIVO"]
}

def calcular_mermas(n, es_digital=False):
    if es_digital: return n * 0.10, 0 # Merma 10% fija Digital
    if n < 100: return 15, 135
    if n < 200: return 30, 150
    if n < 600: return 40, 160
    if n < 1000: return 50, 170
    if n < 2000: return 60, 170
    return 120, 170

# --- 2. INICIALIZACIÓN ---
st.set_page_config(page_title="Escandallos MAINSA PLV", layout="wide")

if 'piezas_dict' not in st.session_state:
    st.session_state.piezas_dict = {0: {"nombre": "Cuerpo Principal", "pliegos": 1.0, "w": 700, "h": 1000, "pf": "Reverso Gris", "gf": 220, "pl": "Ninguna", "ap": "C/C", "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, "ld": False, "pel": "Polipropileno", "cor": "Troquelado"}}

if 'extras_manuales' not in st.session_state:
    st.session_state.extras_manuales = []

# Estilos CSS
st.markdown("""<style>
    .comercial-box { background-color: white; padding: 30px; border: 2px solid #1E88E5; border-radius: 10px; color: #333; font-family: sans-serif; }
    .comercial-header { color: #1E88E5; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .comercial-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    .comercial-table th { background-color: #1E88E5; color: white; padding: 12px; }
    .comercial-table td { padding: 12px; border: 1px solid #ddd; text-align: center; }
</style>""", unsafe_allow_html=True)

st.title("📦 Escandallos Profesionales MAINSA PLV")

# --- 3. PANEL LATERAL ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_str = st.text_input("Cantidades", "200,
