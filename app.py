import streamlit as st
import pandas as pd

# --- 1. BASE DE DATOS DE PRECIOS (Valores exactos de tu tabla) ---
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
st.set_page_config(page_title="MAINSA PLV - PRO", layout="wide")

if 'piezas_dict' not in st.session_state:
    st.session_state.piezas_dict = {0: {"nombre": "Pieza Principal", "pliegos": 1.0, "w": 700, "h": 1000, "pf": "Reverso Gris", "gf": 220, "pl": "Ninguna", "ap": "C/C", "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, "ld": False, "pel": "Polipropileno", "cor": "Troquelado"}}

if 'extras_manuales' not in st.session_state:
    st.session_state.extras_manuales = []

# Estilos CSS corregidos para el Modo Comercial
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
    cants_str = st.text_input("Cantidades (separadas por comas)", "200, 500, 1000")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    st.divider()
    seg_man = st.number_input("Segundos Manipulación / Ud", value=300)
    dif_ud = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], index=2)
    margen = st.number_input("Multiplicador Comercial", value=2.2, step=0.1)
    st.divider()
    modo_comercial = st.checkbox("🌟 VISTA OFERTA COMERCIAL", value=False)

# --- 4. GESTIÓN DE DATOS ---
if not modo_comercial:
    # Botones de control
    c1, c2 = st.columns([1, 5])
    if c1.button("➕ Añadir Forma"):
        new_id = max(st.session_state.piezas_dict.keys()) + 1 if st.session_state.piezas_dict else 0
        st.session_state.piezas_dict[new_id] = {"nombre": f"Parte {new_id+1}", "pliegos": 1.0, "w": 700, "h": 1000, "pf": "Reverso Gris", "gf": 220, "pl": "Ninguna", "ap": "C/C", "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, "ld": False, "pel": "Polipropileno", "cor": "Troquelado"}
        st.rerun()
    if c2.button("🗑 Reiniciar Todo"):
        st.session_state.piezas_dict = {0: {"nombre": "Parte 1", "pliegos": 1.0, "w": 700, "h": 1000, "pf": "Reverso Gris", "gf": 220, "pl": "Ninguna", "ap": "C/C", "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, "ld": False, "pel": "Polipropileno", "cor": "Troquelado"}}
        st.session_state.extras_manuales = []
        st.rerun()

    # Configuración de piezas
    for p_id in list(st.session_state.piezas_dict.keys()):
        p = st.session_state.piezas_dict[p_id]
        with st.expander(f"🛠 Configuración: {p['nombre']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                p['nombre'] = st.text_input("Nombre Pieza", p['nombre'], key=f"n_{p_id}")
                p['pliegos'] = st.number_input("Pliegos/Mueble", 0.0, 100.0, float(p['pliegos']), step=0.1, key=f"p_{p_id}")
                p['w'] = st.number_input("Ancho (mm)", 1, 5000, int(p['w']), key=f"w_{p_id}")
                p['h'] = st.number_input("Largo (mm)", 1, 5000, int(p['h']), key=f"h_{p_id}")
            with col2:
                p['pf'] = st.selectbox("C. Frontal", list(PRECIOS["cartoncillo"].keys()), list(PRECIOS["cartoncillo"].keys()).index(p['pf']), key=f"pf_{p_id}")
                p['gf'] = st.number_input("G. Frontal", PRECIOS["cartoncillo"][p['pf']]["gramaje"], key=f"gf_{p_id}") if p['pf'] != "Ninguno" else 0
                p['pl'] = st.selectbox("Plancha", list(PRECIOS["planchas"].keys()), list(PRECIOS["planchas"].keys()).index(p['pl']), key=f"pl_{p_id}")
                p['ap'] = st.selectbox("Calidad", ["C/C", "B/C", "B/B"], 1, key=f"ap_{p_id}") if p['pl'] != "Ninguna" else "C/C"
            with col3:
                p['im'] = st.selectbox("Impresión", ["Offset", "Digital", "No"], list(["Offset", "Digital", "No"]).index(p['im']), key=f"im_{p_id}")
                p['ld'] = st.checkbox("Laminado Digital (3.5€)", value=p['ld'], key=f"ld_{p_id}") if p['im'] == "Digital" else False
                p['cor'] = st.selectbox("Corte", ["Troquelado", "Plotter"], key=f"cor_{p_id}")
                if st.button("🗑 Eliminar Pieza", key=f"del_{p_id}"): 
                    del st.session_state.piezas_dict[p_id]
                    st.rerun()

    # --- ACCESORIOS Y MANIPULACIÓN ---
    st.divider()
    st.subheader("📦 Accesorios y Piezas Extra")
    
    # 1. Extras Predeterminados (Solo informativos para la oferta)
    extras_pred = st.multiselect("Accesorios estándar incluidos:", PRECIOS["extras_base"], key="ex_pred_sel")
    
    # 2. Extras Manuales con Coste
    st.markdown("**Añadir Extra Manual con Coste Unitario:**")
    ce1, ce2, ce3 = st.columns([3, 2, 1])
    e_nom = ce1.text_input("Nombre elemento (ej: Bolsa tornillos)", key="new_ex_nom")
    e_cost = ce2.number_input("Coste Unitario (€)", 0.0, 100.0, 0.0, step=0.01, key="new_ex_cost")
    if ce3.button("➕ Añadir"):
        if e_nom
