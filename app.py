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

st.set_page_config(page_title="PLV Expert Calc", layout="wide")
st.title("🛠 Calculadora PLV con Escalado")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_str = st.text_input("Cantidades a fabricar (ej: 100, 500, 1000)", "100, 500, 1000")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    
    st.divider()
    minutos_manip = st.number_input("Tiempo Manipulación (Minutos/Mueble)", value=10)
    dificultad = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], format_func=lambda x: f"{x} €")
    mult = st.number_input("Multiplicador Comercial", value=2.2)

# --- GESTIÓN DE PIEZAS ---
if 'piezas' not in st.session_state: st.session_state.piezas = []
if st.button("➕ Añadir Nueva Pieza/Formato"): 
    st.session_state.piezas.append({})

# --- CONFIGURACIÓN DE PIEZAS ---
datos_piezas = []
for i, _ in enumerate(st.session_state.piezas):
    with st.expander(f"Configuración Pieza #{i+1}", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            p_m = st.number_input(f"Pliegos por Mueble", value=1, key=f"p_m_{i}")
            anc = st.number_input(f"Ancho (mm)", value=700, key=f"anc_{i}")
            lar = st.number_input(f"Largo (mm)", value=1000, key=f"lar_{i}")
        
        with col2:
            # Frontal
            p_f = st.selectbox(f"Cartoncillo Frontal", list(PRECIOS["cartoncillo"].keys()), index=1, key=f"p_f_{i}")
            g_f = PRECIOS["cartoncillo"][p_f]["gramaje"]
            if p_f != "Ninguno":
                g_f = st.number_input(f"Gramaje Frontal (g)", value=g_f, key=f"g_f_{i}")
            
            # Plancha
            pla = st.selectbox(f"Plancha Base", list(PRECIOS["planchas"].keys()), key=f"pla_{i}")
            acab_pl = "C/C"
            if pla != "Ninguna" and "AC" not in pla:
                acab_pl = st.selectbox(f"Calidad Plancha", ["C/C", "B/C", "B/B"], key=f"acab_pl_{i}")
            
            # Dorso
            p_d = st.selectbox(f"Cartoncillo Dorso", list(PRECIOS["cartoncillo"].keys()), key=f"p_d_{i}")
            g_d = PRECIOS["cartoncillo"][p_d]["gramaje"]
            if p_d != "Ninguno":
                g_d = st.number_input(f"Gramaje Dorso (g)", value=g_d, key=f"g_d_{i}")
        
        with col3:
            imp = st.selectbox(f"Sistema Impresión", ["Digital", "Offset", "No Impreso"], key=f"imp_{i}")
            n_t = 0
            bar = False
            if imp == "Offset":
                n_t = st.number_input(f"Nº Tintas", 1, 6, 4, key=f"n_t_{i}")
                bar = st.checkbox(f"¿Lleva Barniz?", key=f"bar_{i}")
            pel = st.selectbox(f"Peliculado", list(PRECIOS["peliculado"].keys()), key=f"pel_{i}")
            cor = st.selectbox(f"Método de Corte", ["Troquelado", "Plotter"], key=f"cor_{i}")
            
        datos_piezas.append({
            "pliegos": p_m, "ancho": anc, "largo": lar, "p_frontal": p_f, "g_frontal": g_f,
            "plancha": pla, "acabado_pl": acab_pl, "p_dorso": p_d, "g_dorso": g_d,
            "impresion": imp, "tintas": n_t, "barniz": bar, "peliculado": pel, "corte": cor, 
            "m2": (anc * lar) / 1_000_000
        })

# --- ACCESORIOS ---
st.divider()
st.subheader("📦 Accesorios de Manipulación")
extras_sel = st.multiselect("Seleccionar elementos extra", list(PRECIOS["extras"].keys()))
datos_extras = []
if extras_sel:
    cols_ex = st.columns(len(extras_sel))
    for idx, ex in enumerate(extras_sel):
        cant_ex = cols_ex[idx].number_input(f"Cant. {ex} / mueble", value=1.0, key=f"cant_ex_{idx}")
        datos_extras.append({"nombre": ex, "cantidad": cant_ex})

# --- BUCLE DE CÁLCULO ---
resultados = []

for q_final in lista_cants:
    coste_total_fabricacion = 0.0
    
    for pieza in datos_piezas:
        n_buenas = q_final * pieza["pliegos"]
        m_norm, m_imp = obtener_mermas(n_buenas)
        h_papel = n_buenas + m_norm + m_imp
        h_proc = n_buenas + m_norm
        m2 = pieza["m2"]

        # 1. Coste Papeles (Usando el gramaje editado)
        def calc_pap(tipo, gram_manual, cant):
            if tipo == "Ninguno": return 0
            return cant * m2 * (gram_manual/1000) * PRECIOS["cartoncillo"][tipo]["precio_kg"]
        
        c_mat = calc_pap(pieza["p_frontal"], pieza["g_frontal"], h_papel) + \
                calc_pap(pieza["p_dorso"], pieza["g_dorso"], h_papel)
        
        # 2. Plancha y Contracolado
        c_pla = 0
        c_cnt = 0
        if pieza["plancha"] != "Ninguna":
            c_pla = h_proc * m2 * PRECIOS["planchas"][pieza["plancha"]][pieza["acabado_pl"]]
            pasadas = (1 if pieza["p_frontal"] != "Ninguno" else 0) + (1 if pieza["p_dorso"] != "Ninguno" else 0)
            c_cnt = h_proc * m2 * PRECIOS["planchas"][pieza["plancha"]]["peg"] * pasadas

        # 3. Impresión y Peliculado
        c_imp = 0
        if pieza["impresion"] == "Digital": c_imp = h_papel * m2 * 6.5
        elif pieza["impresion"] == "Offset":
            t_off = pieza["tintas"] + (1 if pieza["barniz"] else 0)
            base = 60 if h_papel < 100 else (60 + 0.15*(h_papel-100) if h_papel < 500 else (120 if h_papel <= 2000 else 120 + 0.015*(h_papel-2000)))
            c_imp = base * t_off
        c_pel = h_proc * m2 * PRECIOS["peliculado"][pieza["peliculado"]]

        # 4. Corte
        if pieza["corte"] == "Troquelado":
            f_trq = 107.7 if (pieza["largo"] > 1000 or pieza["ancho"] > 700) else (80.77 if (pieza["largo"] == 1000 and pieza["ancho"] == 700) else 48.19)
            v_trq = 0.135 if (pieza["largo"] > 1000 or pieza["ancho"] > 700) else (0.09 if (pieza["largo"] == 1000 and pieza["ancho"] == 700) else 0.06)
            c_cor = f_trq + (h_proc * v_trq)
        else: c_cor = h_proc * 1.5

        coste_total_fabricacion += (c_mat + c_pla + c_cnt + c_imp + c_pel + c_cor)

    # 5. Manipulación y Extras
    c_man = ((minutos_manip / 60) * 18 * q_final) + (q_final * dificultad)
    c_ext = sum(PRECIOS["extras"][ex["nombre"]] * ex["cantidad"] * q_final for ex in datos_extras)

    total_proy = coste_total_fabricacion + c_man + c_ext
    pvp_proy = total_proy * mult
    
    resultados.append({
        "Cantidad": q_final,
        "Coste Fab. Total": f"{total_proy:.2f} €",
        "PVP Total": f"{pvp_proy:.2f} €",
        "PVP Unidad": f"{(pvp_proy / q_final):.2f} €"
    })

# --- TABLA FINAL ---
st.divider()
st.header("📊 Resumen de Escalado (PV Unidad)")
if resultados:
    st.table(pd.DataFrame(resultados))
