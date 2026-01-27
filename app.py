import streamlit as st
import pandas as pd  # <--- CORREGIDO: Ahora sí cargará correctamente
import json

# --- 1. BASE DE DATOS Y LÓGICA DE CAJAS ---
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
    "extras_base": {
        "CINTA D/CARA": 0.26, "CINTA LOHMAN": 0.49, "CINTA GEL": 1.2,
        "GOMA TERMINALES": 0.079, "IMAN 20x2mm": 1.145, "TUBOS": 1.06,
        "REMACHES": 0.049, "VELCRO": 0.43, "PUNTO ADHESIVO": 0.08
    }
}

def calcular_coste_caja_plano(largo, ancho, alto, q):
    if q <= 0: return 0.0
    dimensiones = sorted([largo, ancho, alto], reverse=True)
    area_base = dimensiones[0] * dimensiones[1]
    coste_250 = (0.00000091 * area_base) + 1.00
    if q >= 250: return coste_250 * ((q / 250) ** -0.32)
    elif q == 100: return 2.69
    elif 100 < q < 250:
        progreso = (q - 100) / (250 - 100)
        return 2.69 + progreso * (coste_250 - 2.69)
    return 2.69

def calcular_mermas(n, es_digital=False):
    if es_digital: return n * 0.10, 0 
    if n < 100: return 15, 135
    if n < 200: return 30, 150
    if n < 600: return 40, 160
    if n < 1000: return 50, 170
    if n < 2000: return 60, 170
    return 120, 170

# --- 2. INICIALIZACIÓN ---
st.set_page_config(page_title="ESCANDALLO MAINSA", layout="wide")

if 'piezas_dict' not in st.session_state: 
    st.session_state.piezas_dict = {0: {"nombre": "Forma 1", "pliegos": 1.0, "w": 0, "h": 0, "pf": "Ninguno", "gf": 0, "pl": "Ninguna", "ap": "C/C", "im": "Offset", "cor": "Troquelado", "cobrar_arreglo": True}}
if 'lista_extras_grabados' not in st.session_state: st.session_state.lista_extras_grabados = []
if 'lista_cajas_grabadas' not in st.session_state: st.session_state.lista_cajas_grabadas = []

# --- 3. PANEL LATERAL ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_str = st.text_input("Cantidades (ej: 500, 1000)", "0")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    t_input = st.number_input("Tiempo Manipulado (min)", value=0)
    seg_man_total = t_input * 60
    margen = st.number_input("Multiplicador Comercial", value=2.2, step=0.1)
    imp_fijo = st.number_input("Importe Fijo Trabajo (€)", value=500)
    modo_comercial = st.checkbox("🌟 VISTA OFERTA COMERCIAL", value=False)

# --- 4. CUERPO PRINCIPAL ---
if not modo_comercial:
    # SECCIÓN 1: FORMAS
    st.header("1. Fabricación de Formas")
    for p_id, p in st.session_state.piezas_dict.items():
        with st.expander(f"🛠 {p['nombre']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                p['nombre'] = st.text_input("Etiqueta", p['nombre'], key=f"n_{p_id}")
                p['h'] = st.number_input("Largo mm", 0, 5000, int(p.get('h', 0)), key=f"h_{p_id}")
                p['w'] = st.number_input("Ancho mm", 0, 5000, int(p.get('w', 0)), key=f"w_{p_id}")
            with col2:
                p['pf'] = st.selectbox("Material", list(PRECIOS["cartoncillo"].keys()), key=f"pf_{p_id}")
                p['pl'] = st.selectbox("Plancha Base", list(PRECIOS["planchas"].keys()), key=f"pl_{p_id}")
            with col3:
                p['cor'] = st.selectbox("Corte", ["Troquelado", "Plotter"], key=f"cor_{p_id}")
                p['cobrar_arreglo'] = st.checkbox("¿Arreglo?", value=p.get('cobrar_arreglo', True), key=f"arr_{p_id}")

    # SECCIÓN 2: MATERIALES EXTRA
    st.divider()
    st.header("2. Almacén de Accesorios")
    col_e1, col_e2 = st.columns(2)
    ex_sel = col_e1.selectbox("Añadir Extra:", ["---"] + list(PRECIOS["extras_base"].keys()))
    if col_e1.button("➕ Añadir Extra") and ex_sel != "---":
        st.session_state.lista_extras_grabados.append({"nombre": ex_sel, "coste": PRECIOS["extras_base"][ex_sel], "cantidad": 1.0})
    
    for i, ex in enumerate(st.session_state.lista_extras_grabados):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
        c1.write(f"**{ex['nombre']}**")
        ex['coste'] = c2.number_input("€/ud", value=float(ex['coste']), key=f"exc_{i}")
        ex['cantidad'] = c3.number_input("Cant/Ud", value=float(ex['cantidad']), key=f"exq_{i}")
        if c4.button("🗑", key=f"exd_{i}"): st.session_state.lista_extras_grabados.pop(i); st.rerun()

    # SECCIÓN 3: CÁLCULO DE CAJAS
    st.divider()
    st.header("3. Complemento de Cajas")
    col_c1, col_c2 = st.columns(2)
    tipo_caja = col_c1.selectbox("Tipo de Caja:", ["Plano (Canal 5)", "En Volumen", "Guainas"])
    if col_c1.button("➕ Añadir Caja"):
        st.session_state.lista_cajas_grabadas.append({"tipo": tipo_caja, "l": 0, "w": 0, "a": 0, "uds_por_producto": 1})

    for i, caja in enumerate(st.session_state.lista_cajas_grabadas):
        with st.info(f"📦 Caja {i+1}: {caja['tipo']}"):
            cc1, cc2, cc3, cc4, cc5 = st.columns(5)
            caja['l'] = cc1.number_input("Largo (mm)", value=caja['l'], key=f"cl_{i}")
            caja['w'] = cc2.number_input("Ancho (mm)", value=caja['w'], key=f"cw_{i}")
            caja['a'] = cc3.number_input("Alto (mm)", value=caja['a'], key=f"ca_{i}")
            caja['uds_por_producto'] = cc4.number_input("Cajas/Ud", value=caja['uds_por_producto'], key=f"cu_{i}")
            if cc5.button("🗑", key=f"cdel_{i}"): st.session_state.lista_cajas_grabadas.pop(i); st.rerun()

# --- 5. MOTOR DE CÁLCULO ---
res_final = []
if lista_cants and sum(lista_cants) > 0:
    for q_n in lista_cants:
        coste_base = 0.0
        # 1. Coste Formas
        for p in st.session_state.piezas_dict.values():
            m2 = (p['h'] * p['w']) / 1_000_000
            
            # Criterio de Medida Actualizado
            l_p, w_p = p['h'], p['w']
            if l_p > 1000 or w_p > 700: v_arr, v_tir = 107.80, 0.135
            elif l_p < 1000 and w_p < 700: v_arr, v_tir = 48.19, 0.06
            else: v_arr, v_tir = 80.77, 0.09
            
            c_arr = v_arr if p.get('cobrar_arreglo') else 0
            coste_base += c_arr + (q_n * v_tir)
            
        # 2. Coste Extras
        coste_extras = sum(e['coste'] * e['cantidad'] * q_n for e in st.session_state.lista_extras_grabados)
        
        # 3. Coste Cajas
        coste_cajas = 0.0
        for c in st.session_state.lista_cajas_grabadas:
            cant_total_cajas = q_n * c['uds_por_producto']
            if c['tipo'] == "Plano (Canal 5)":
                coste_u = calcular_coste_caja_plano(c['l'], c['w'], c['a'], cant_total_cajas)
                coste_cajas += coste_u * cant_total_cajas

        t_fab = coste_base + coste_extras + coste_cajas + (seg_man_total/3600 * 18 * q_n) + imp_fijo
        res_final.append({
            "Cantidad": q_n, 
            "Fabricación (€)": f"{t_fab:.2f}€",
            "PVP TOTAL": f"{t_fab*margen:.2f}€", 
            "PVP Unitario": f"{(t_fab*margen)/q_n:.2f}€"
        })

if res_final:
    st.divider()
    st.header("📊 Resultado Final")
    st.dataframe(pd.DataFrame(res_final), use_container_width=True)
