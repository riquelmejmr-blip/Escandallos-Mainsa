import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN Y PRECIOS ---
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
        "Microcanal": {"C/C": 0.684, "B/C": 0.726, "B/B": 0.819, "peg": 0.217},
        "Canal 3": {"C/C": 0.684, "B/C": 0.726, "B/B": 0.819, "peg": 0.217},
        "Doble de Micro": {"C/C": 1.129, "B/C": 1.149, "B/B": 1.251, "peg": 0.263},
        "Doble Doble": {"C/C": 1.129, "B/C": 1.149, "B/B": 1.251, "peg": 0.263},
        "AC (Cuero/Cuero)": {"C/C": 2.505, "peg": 0.217}
    },
    "peliculado": {
        "Sin Peliculado": 0,
        "Polipropileno": 0.26,
        "Poliéster brillo": 0.38,
        "Poliéster mate": 0.64
    },
    "extras": {
        "CINTA D/CARA normal": 0.26, "CINTA LOHMAN 20mm": 0.33, "CINTA LOHMAN 35mm": 0.49,
        "CINTA GEL ROJA": 0.45, "CINTA GEL TESA": 1.2, "GOMA TERMINALES": 0.079,
        "IMAN 20x2mm": 1.145, "Tubos 30mm": 0.93, "Tubos 60mm": 1.06,
        "Bridas": 0.13, "REMACHES": 0.049, "VELCRO TIRA": 0.43, "PUNTO ADHESIVO": 0.08,
        "PIEZA Harrison 867696": 0.09, "PIEZA Harrison 867702": 0.172
    }
}

def obtener_mermas(n):
    if n < 100: return 15, 135
    if n < 200: return 30, 150
    if n < 600: return 40, 160
    if n < 1000: return 50, 170
    if n < 2000: return 60, 170
    return 120, 170

st.set_page_config(page_title="PLV Pro Calc", layout="wide")
st.title("🛠 Calculadora PLV con Desglose de Partidas")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_str = st.text_input("Cantidades (ej: 100, 500, 1000)", "200, 500")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    
    st.divider()
    min_manip = st.number_input("Minutos Manipulación / Mueble", value=15)
    dificultad = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], format_func=lambda x: f"{x} €")
    mult = st.number_input("Multiplicador Comercial", value=2.2)

# --- PIEZAS ---
if 'piezas' not in st.session_state: st.session_state.piezas = []
if st.button("➕ Añadir Nueva Pieza"): st.session_state.piezas.append({})

datos_piezas = []
for i, _ in enumerate(st.session_state.piezas):
    with st.expander(f"Configuración Pieza #{i+1}", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            p_m = st.number_input(f"Pliegos/Mueble #{i+1}", value=1, key=f"pm{i}")
            anc = st.number_input(f"Ancho mm #{i+1}", value=700, key=f"an{i}")
            lar = st.number_input(f"Largo mm #{i+1}", value=1000, key=f"la{i}")
        with c2:
            p_f = st.selectbox(f"Cartoncillo Frontal #{i+1}", list(PRECIOS["cartoncillo"].keys()), index=1, key=f"pf{i}")
            g_f = st.number_input(f"Gramaje Frontal #{i+1}", value=PRECIOS["cartoncillo"][p_f]["gramaje"], key=f"gf{i}")
            pla = st.selectbox(f"Plancha Base #{i+1}", list(PRECIOS["planchas"].keys()), key=f"pl{i}")
            acab_pl = st.selectbox(f"Calidad Plancha #{i+1}", ["C/C", "B/C", "B/B"], key=f"ap{i}") if pla != "Ninguna" and "AC" not in pla else "C/C"
            p_d = st.selectbox(f"Cartoncillo Dorso #{i+1}", list(PRECIOS["cartoncillo"].keys()), key=f"pd{i}")
            g_d = st.number_input(f"Gramaje Dorso #{i+1}", value=PRECIOS["cartoncillo"][p_d]["gramaje"], key=f"gd{i}")
        with c3:
            imp = st.selectbox(f"Impresión #{i+1}", ["Digital", "Offset", "No"], key=f"im{i}")
            n_t = st.number_input(f"Tintas", 1, 6, 4, key=f"nt{i}") if imp == "Offset" else 0
            bar = st.checkbox(f"Barniz", key=f"ba{i}") if imp == "Offset" else False
            pel = st.selectbox(f"Peliculado #{i+1}", list(PRECIOS["peliculado"].keys()), key=f"pe{i}")
            cor = st.selectbox(f"Corte #{i+1}", ["Troquelado", "Plotter"], key=f"co{i}")
        
        datos_piezas.append({"p": p_m, "w": anc, "h": lar, "pf": p_f, "gf": g_f, "pla": pla, "acab": acab_pl, "pd": p_d, "gd": g_d, "imp": imp, "nt": n_t, "bar": bar, "pel": pel, "cor": cor})

# --- EXTRAS ---
st.divider()
extras_sel = st.multiselect("Accesorios de Manipulación", list(PRECIOS["extras"].keys()))
datos_extras = []
if extras_sel:
    cols = st.columns(len(extras_sel))
    for idx, ex in enumerate(extras_sel):
        cant_ex = cols[idx].number_input(f"Uds {ex}/mueble", value=1.0, key=f"ex{idx}")
        datos_extras.append({"n": ex, "q": cant_ex})

# --- CÁLCULOS Y RESUMEN PARTIDAS ---
resultados_escalado = []
desgloses_por_cantidad = {}

for q_f in lista_cants:
    partidas = {"Materiales": 0.0, "Impresión": 0.0, "Acabado": 0.0, "Corte": 0.0, "Manipulación": 0.0}
    
    for pz in datos_piezas:
        n_b = q_f * pz["p"]
        m_n, m_i = obtener_mermas(n_b)
        h_pap = n_b + m_n + m_i
        h_pro = n_b + m_n
        m2_u = (pz["w"] * pz["h"]) / 1_000_000
        
        # Partida Materiales
        c_p1 = h_pap * m2_u * (pz["gf"]/1000) * PRECIOS["cartoncillo"][pz["pf"]]["precio_kg"]
        c_p2 = h_pap * m2_u * (pz["gd"]/1000) * PRECIOS["cartoncillo"][pz["pd"]]["precio_kg"]
        c_pla = (h_pro * m2_u * PRECIOS["planchas"][pz["pla"]][pz["acab"]]) if pz["pla"] != "Ninguna" else 0
        pasadas = (1 if pz["pf"] != "Ninguno" else 0) + (
