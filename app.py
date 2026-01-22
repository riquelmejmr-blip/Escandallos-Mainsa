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

# --- SIDEBAR (Cantidades y Mano de Obra) ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_str = st.text_input("Cantidades a fabricar (separadas por coma)", "100, 500, 1000")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    
    st.divider()
    minutos_manip = st.number_input("Tiempo Manipulación (Minutos/Mueble)", value=10)
    dificultad = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], format_func=lambda x: f"{x} €")
    mult = st.number_input("Multiplicador Comercial", value=2.2)

# --- GESTIÓN DE PIEZAS ---
if 'piezas' not in st.session_state: st.session_state.piezas = []
if st.button("➕ Añadir Nueva Pieza/Formato"): st.session_state.piezas.append({})

# --- CÁLCULOS ---
resultados = []

for q_final in lista_cants:
    coste_total_proyecto = 0.0
    
    for i, _ in enumerate(st.session_state.piezas):
        with st.expander(f"Configuración Pieza #{i+1}", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                pliegos_mueble = st.number_input(f"Pliegos por Mueble #{i+1}", value=1, key=f"p{i}")
                anc = st.number_input(f"Ancho (mm) #{i+1}", value=700, key=f"a{i}")
                lar = st.number_input(f"Largo (mm) #{i+1}", value=1000, key=f"l{i}")
                m2 = (anc * lar) / 1_000_000
            
            with col2:
                # Capas
                p_front = st.selectbox(f"Cartoncillo Frontal #{i+1}", list(PRECIOS["cartoncillo"].keys()), index=1, key=f"pf{i}")
                plancha = st.selectbox(f"Plancha Base #{i+1}", list(PRECIOS["planchas"].keys()), key=f"pl{i}")
                acab_pl = "C/C"
                if plancha != "Ninguna" and "AC" not in plancha:
                    acab_pl = st.selectbox(f"Calidad Plancha #{i+1}", ["C/C", "B/C", "B/B"], key=f"ac{i}")
                p_dorso = st.selectbox(f"Cartoncillo Dorso #{i+1}", list(PRECIOS["cartoncillo"].keys()), key=f"pd{i}")
                
            with col3:
                # Impresión y Acabados
                imp = st.selectbox(f"Sistema Impresión #{i+1}", ["Digital", "Offset", "No Impreso"], key=f"im{i}")
                n_tintas = 0
                barniz = False
                if imp == "Offset":
                    n_tintas = st.number_input(f"Nº Tintas #{i+1}", 1, 6, 4, key=f"ti{i}")
                    barniz = st.checkbox(f"¿Lleva Barniz? #{i+1}", key=f"ba{i}")
                
                tipo_pel = st.selectbox(f"Peliculado #{i+1}", list(PRECIOS["peliculado"].keys()), key=f"pe{i}")
                corte = st.selectbox(f"Método de Corte #{i+1}", ["Troquelado", "Plotter"], key=f"co{i}")

        # Lógica Matemática
        n_buenas = q_final * pliegos_mueble
        m_norm, m_imp = obtener_mermas(n_buenas)
        h_papel = n_buenas + m_norm + m_imp
        h_proc = n_buenas + m_norm

        # 1. Coste Papeles (Frontal + Dorso)
        def calc_pap(tipo, cant):
            return cant * m2 * (PRECIOS["cartoncillo"][tipo]["gramaje"]/1000) * PRECIOS["cartoncillo"][tipo]["precio_kg"]
        
        c_material = calc_pap(p_front, h_papel) + calc_pap(p_dorso, h_papel)
        
        # 2. Coste Plancha y Contracolado
        c_plancha = 0
        c_contra = 0
        if plancha != "Ninguna":
            c_plancha = h_proc * m2 * PRECIOS["planchas"][plancha][acab_pl]
            pasadas = 0
            if p_front != "Ninguno": pasadas += 1
            if p_dorso != "Ninguno": pasadas += 1
            c_contra = h_proc * m2 * PRECIOS["planchas"][plancha]["peg"] * pasadas

        # 3. Impresión y Peliculado
        c_imp = 0
        if imp == "Digital": c_imp = h_papel * m2 * 6.5
        elif imp == "Offset":
            t_offset = n_tintas + (1 if barniz else 0)
            base = 60 if h_papel < 100 else (60 + 0.15*(h_papel-100) if h_papel < 500 else (120 if h_papel <= 2000 else 120 + 0.015*(h_papel-2000)))
            c_imp = base * t_offset
        
        c_pel = h_proc * m2 * PRECIOS["peliculado"][tipo_pel]

        # 4. Corte
        c_corte = 0
        if corte == "Troquelado":
            f_trq = 107.7 if (lar > 1000 or anc > 700) else (80.77 if (lar == 1000 and anc == 700) else 48.19)
            v_trq = 0.135 if (lar > 1000 or anc > 700) else (0.09 if (lar == 1000 and anc == 700) else 0.06)
            c_corte = f_trq + (h_proc * v_trq)
        else: c_corte = h_proc * 1.5

        coste_total_proyecto += (c_material + c_plancha + c_contra + c_imp + c_pel + c_corte)

    # 5. Extras y Manipulación (Se suma una vez por cantidad del escalado)
    c_manip = ((minutos_manip / 60) * 18 * q_final) + (q_final * dificultad)
    
    # Extras (Dropdown)
    st.divider()
    st.subheader("📦 Accesorios de Manipulación")
    extras_sel = st.multiselect("Añadir elementos extra", list(PRECIOS["extras"].keys()), key=f"ex_sel_{q_final}")
    c_extras = 0
    for ex in extras_sel:
        cant_ex = st.number_input(f"Cantidad/Metros de {ex} por mueble", value=1.0, key=f"ex_{ex}_{q_final}")
        c_extras += PRECIOS["extras"][ex] * cant_ex * q_final

    total_coste_fab = coste_total_proyecto + c_manip + c_extras
    pvp_total = total_coste_fab * mult
    
    resultados.append({
        "Cantidad": q_final,
        "Coste Fab. Total": f"{total_coste_fab:.2f} €",
        "PVP Total": f"{pvp_total:.2f} €",
        "PVP Unidad": f"{(pvp_total / q_final):.2f} €"
    })

# --- TABLA DE RESULTADOS FINAL ---
st.divider()
st.header("📊 Escalado de Precios (Resumen por Unidad)")
if resultados:
    df = pd.DataFrame(resultados)
    st.table(df)
