import streamlit as st

# --- TABLAS DE PRECIOS ---
PRECIOS = {
    "cartoncillo": {
        "Reverso Gris": {"precio_kg": 0.93, "gramaje": 220},
        "Zenith": {"precio_kg": 1.55, "gramaje": 350},
        "Reverso Madera": {"precio_kg": 0.95, "gramaje": 400},
        "Folding Kraft": {"precio_kg": 1.90, "gramaje": 340},
        "Folding Blanco": {"precio_kg": 1.82, "gramaje": 350}
    },
    "planchas": {
        "Microcanal": {"C/C": 0.684, "B/C": 0.726, "B/B": 0.819, "peg": 0.217},
        "Canal 3": {"C/C": 0.684, "B/C": 0.726, "B/B": 0.819, "peg": 0.217},
        "Doble de Micro": {"C/C": 1.129, "B/C": 1.149, "B/B": 1.251, "peg": 0.263},
        "Doble Doble": {"C/C": 1.129, "B/C": 1.149, "B/B": 1.251, "peg": 0.263},
        "AC (Cuero/Cuero)": {"C/C": 2.505, "peg": 0.217}
    },
    "extras": {
        "CINTA D/CARA normal": 0.26, "CINTA LOHMAN 20mm": 0.33, "CINTA LOHMAN 35mm": 0.49,
        "CINTA GEL ROJA": 0.45, "CINTA GEL TESA": 1.2, "GOMA TERMINALES": 0.079,
        "IMAN 20x2mm": 1.145, "Tubos 30mm": 0.93, "Tubos 60mm": 1.06,
        "Bridas": 0.13, "REMACHES": 0.049, "VELCRO TIRA": 0.43, "PUNTO ADHESIVO": 0.08,
        "PIEZA Harrison 867696": 0.09, "PIEZA Harrison 867702": 0.172
    }
}

def calcular_mermas(n):
    if n < 100: return 15, 135
    if n < 200: return 30, 150
    if n < 600: return 40, 160
    if n < 1000: return 50, 170
    if n < 2000: return 60, 170
    return 120, 170

# --- INTERFAZ ---
st.set_page_config(page_title="PLV Calc", layout="wide")
st.title("📦 Calculadora de Costes PLV")

with st.sidebar:
    mult = st.number_input("Multiplicador Margen", value=2.2)
    h_op = st.number_input("Horas Totales Mano Obra", value=1.0)
    dif = st.selectbox("Dificultad", [0.02, 0.061, 0.091], format_func=lambda x: f"{x} €/ud")

if 'piezas' not in st.session_state: st.session_state.piezas = []
if st.button("➕ Añadir Formato"): st.session_state.piezas.append({})

total_fab = 0.0
for i, _ in enumerate(st.session_state.piezas):
    with st.expander(f"Pieza #{i+1}", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            muebles = st.number_input(f"Muebles", value=100, key=f"m{i}")
            pliegos = st.number_input(f"Pliegos/Mueble", value=1, key=f"p{i}")
            n_buenas = muebles * pliegos
        with c2:
            anc = st.number_input(f"Ancho (mm)", value=700, key=f"a{i}")
            lar = st.number_input(f"Largo (mm)", value=1000, key=f"l{i}")
            m2 = (anc * lar) / 1_000_000
        with c3:
            imp = st.selectbox(f"Impresión", ["Digital", "Offset", "No"], key=f"i{i}")
            t_papel = st.selectbox(f"Papel", list(PRECIOS["cartoncillo"].keys()), key=f"pa{i}")

        m_n, m_i = calcular_mermas(n_buenas)
        h_papel = n_buenas + m_n + m_i
        h_proc = n_buenas + m_n

        # Cálculo Material e Impresión
        gram = PRECIOS["cartoncillo"][t_papel]["gramaje"]
        c_pap = h_papel * m2 * (gram/1000) * PRECIOS["cartoncillo"][t_papel]["precio_kg"]
        c_imp = (h_papel * m2 * 6.5) if imp == "Digital" else 0
        if imp == "Offset":
            t_cost = 60 if h_papel < 100 else (60 + 0.15*(h_papel-100) if h_papel < 500 else (120 if h_papel <= 2000 else 120 + 0.015*(h_papel-2000)))
            c_imp = t_cost * 4 # Por defecto 4 tintas

        total_pieza = c_pap + c_imp
        total_fab += total_pieza
        st.info(f"Subtotal: {total_pieza:.2f} €")

# Resumen final
st.divider()
total_final = (total_fab + (h_op * 18) + (muebles * dif))
st.metric("PRECIO DE VENTA TOTAL", f"{total_final * mult:.2f} €")
