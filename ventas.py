import streamlit as st
import pandas as pd
import json

# --- 1. BASE DE DATOS DE PRECIOS (IDÉNTICA A PRODUCCIÓN) ---
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
    "peliculado": {"Sin Peliculado": 0, "Polipropileno": 0.26, "Poliéster brillo": 0.38, "Poliéster mate": 0.64},
    "laminado_digital": 3.5,
    "extras_base": {
        "CINTA D/CARA": 0.26, "CINTA LOHMAN": 0.49, "CINTA GEL": 1.2,
        "GOMA TERMINALES": 0.079, "IMAN 20x2mm": 1.145, "TUBOS": 1.06,
        "REMACHES": 0.049, "VELCRO": 0.43, "PUNTO ADHESIVO": 0.08
    }
}

# --- 2. MOTORES DE CÁLCULO ---

def calcular_mermas(n, es_digital=False):
    if es_digital: return n * 0.10, 0 
    if n < 100: return 15, 135
    if n < 200: return 30, 150
    if n < 600: return 40, 160
    if n < 1000: return 50, 170
    if n < 2000: return 60, 170
    return 120, 170

def motor_embalajes(tipo, largo, ancho, alto, q):
    if q <= 0: return 0.0
    if tipo == "Plano (Canal 5)":
        dims = sorted([largo, ancho, alto], reverse=True)
        area_base = dims[0] * dims[1]
        coste_250 = (0.00000091 * area_base) + 1.00
        if q >= 250: return coste_250 * ((q / 250) ** -0.32)
        elif q == 100: return 2.69
        elif 100 < q < 250:
            progreso = (q - 100) / (250 - 100)
            return 2.69 + progreso * (coste_250 - 2.69)
        return 2.69
    return 0.0

# --- 3. CONFIGURACIÓN Y SESIÓN ---
st.set_page_config(page_title="MAINSA VENTAS", layout="wide")

def crear_forma_vacia(index):
    return {
        "nombre": f"Pieza {index + 1}", "pliegos": 1.0, "w": 0, "h": 0, 
        "pf": "Ninguno", "gf": 0, "pl": "Ninguna", "ap": "C/C", 
        "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, 
        "im_d": "No", "nt_d": 0, "ba_d": False, "pel": "Sin Peliculado", 
        "pel_d": "Sin Peliculado", "ld": False, "ld_d": False, 
        "cor": "Troquelado", "cobrar_arreglo": True
    }

for key, default in [('piezas_dict', {0: crear_forma_vacia(0)}), ('lista_extras_grabados', []), 
                     ('lista_embalajes', []), ('brf', ""), ('cli', ""), ('com', ""), 
                     ('ver', "1.0"), ('des', ""), ('imp_fijo', 500)]:
    if key not in st.session_state: st.session_state[key] = default

# Estilos Oferta Comercial
st.markdown("""<style>
    .quote-box { background-color: white; padding: 35px; border: 1px solid #ddd; border-radius: 8px; color: #222; }
    .quote-header { color: #1E88E5; border-bottom: 2px solid #1E88E5; margin-bottom: 20px; }
    .quote-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    .quote-table th { background-color: #f8f9fa; padding: 12px; border: 1px solid #ddd; text-align: left; }
    .quote-table td { padding: 12px; border: 1px solid #ddd; }
    .unit-price { font-weight: bold; color: #1E88E5; font-size: 1.1em; }
</style>""", unsafe_allow_html=True)

st.title("💼 GESTIÓN COMERCIAL MAINSA")

# --- 4. PANEL LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("📋 Datos del Proyecto")
    st.session_state.cli = st.text_input("Cliente", st.session_state.cli)
    st.session_state.brf = st.text_input("Briefing", st.session_state.brf)
    st.session_state.ver = st.text_input("Versión", st.session_state.ver)
    st.session_state.des = st.text_area("Descripción corta", st.session_state.des)
    
    st.divider()
    cants_str = st.text_input("Cantidades (ej: 500, 1000)", "0")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    
    margen = st.number_input("Multiplicador (Margen)", value=2.2, step=0.1)
    st.session_state.imp_fijo = st.number_input("Importe Fijo (€)", value=st.session_state.imp_fijo)

    st.divider()
    st.header("📂 Archivos")
    partes_nombre = [st.session_state.brf, st.session_state.cli, st.session_state.ver]
    nombre_archivo = "P_VENTAS_" + "_".join([str(p).strip() for p in partes_nombre if str(p).strip()]) + ".json"
    
    datos_json = {
        "brf": st.session_state.brf, "cli": st.session_state.cli, "com": st.session_state.com,
        "ver": st.session_state.ver, "des": st.session_state.des, "piezas": st.session_state.piezas_dict,
        "extras": st.session_state.lista_extras_grabados, "embalajes": st.session_state.lista_embalajes,
        "imp_fijo": st.session_state.imp_fijo
    }
    st.download_button("💾 Guardar Proyecto", json.dumps(datos_json, indent=4), file_name=nombre_archivo)
    
    subida = st.file_uploader("📂 Cargar Proyecto", type=["json"])
    if subida:
        d = json.load(subida)
        st.session_state.piezas_dict = {int(k): v for k, v in d["piezas"].items()}
        st.session_state.lista_extras_grabados = d.get("extras", [])
        st.session_state.lista_embalajes = d.get("embalajes", [])
        st.rerun()

# --- 5. INTERFAZ POR PASOS ---
tabs = st.tabs(["1. Configurar Producto", "2. Accesorios y Embalaje", "3. Oferta para Cliente"])

with tabs[0]:
    st.subheader("Piezas del producto")
    if st.button("➕ Añadir Pieza"):
        nid = max(st.session_state.piezas_dict.keys()) + 1
        st.session_state.piezas_dict[nid] = crear_forma_vacia(nid); st.rerun()

    for p_id, p in st.session_state.piezas_dict.items():
        with st.expander(f"🛠 {p['nombre']} ({p['h']}x{p['w']} mm)", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                p['nombre'] = st.text_input("Etiqueta", p['nombre'], key=f"n_{p_id}")
                p['pliegos'] = st.number_input("Pliegos/Ud", 0.0, 100.0, float(p['pliegos']), key=f"p_{p_id}")
                p['h'] = st.number_input("Largo mm", 0, 5000, int(p['h']), key=f"h_{p_id}")
                p['w'] = st.number_input("Ancho mm", 0, 5000, int(p['w']), key=f"w_{p_id}")
            with col2:
                p['im'] = st.selectbox("Impresión", ["Offset", "Digital", "No"], key=f"im_{p_id}")
                p['pf'] = st.selectbox("Material Frontal", list(PRECIOS["cartoncillo"].keys()), key=f"pf_{p_id}")
                p['pl'] = st.selectbox("Soporte", list(PRECIOS["planchas"].keys()), key=f"pl_{p_id}")
            with col3:
                p['cor'] = st.selectbox("Corte", ["Troquelado", "Plotter"], key=f"cor_{p_id}")
                p['cobrar_arreglo'] = st.checkbox("Incluir Arreglo", value=p['cobrar_arreglo'], key=f"arr_{p_id}")
                if st.button("🗑 Eliminar Pieza", key=f"del_{p_id}"):
                    del st.session_state.piezas_dict[p_id]; st.rerun()

with tabs[1]:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Accesorios (Cintas, Imanes...)")
        ex_sel = st.selectbox("Elegir accesorio:", ["---"] + list(PRECIOS["extras_base"].keys()))
        if st.button("➕ Añadir"):
            st.session_state.lista_extras_grabados.append({"nombre": ex_sel, "coste": PRECIOS["extras_base"][ex_sel], "cantidad": 1.0}); st.rerun()
        for i, ex in enumerate(st.session_state.lista_extras_grabados):
            cx1, cx2 = st.columns([3, 1])
            ex['cantidad'] = cx1.number_input(f"{ex['nombre']} (Cant/Ud)", value=float(ex['cantidad']), key=f"exq_{i}")
            if cx2.button("🗑", key=f"exd_{i}"): st.session_state.lista_extras_grabados.pop(i); st.rerun()

    with col_b:
        st.subheader("Embalaje de Envío")
        tipo_em = st.selectbox("Tipo de Caja:", ["Plano (Canal 5)", "En Volumen", "Guainas"])
        if st.button("➕ Añadir Caja"):
            st.session_state.lista_embalajes.append({"tipo": tipo_em, "l": 0, "w": 0, "a": 0, "uds": 1}); st.rerun()
        for i, em in enumerate(st.session_state.lista_embalajes):
            ce1, ce2, ce3, ce4, ce5 = st.columns([1,1,1,1,0.5])
            em['l'], em['w'], em['a'], em['uds'] = ce1.number_input("L", value=em['l'], key=f"el_{i}"), ce2.number_input("W", value=em['w'], key=f"ew_{i}"), ce3.number_input("A", value=em['a'], key=f"ea_{i}"), ce4.number_input("C/U", value=em['uds'], key=f"eu_{i}")
            if ce5.button("🗑", key=f"ed_{i}"): st.session_state.lista_embalajes.pop(i); st.rerun()

# --- 6. MOTOR DE CÁLCULO (IDÉNTICO A PRODUCCIÓN) ---
oferta_datos = []
if lista_cants and sum(lista_cants) > 0:
    for q_n in lista_cants:
        coste_piezas_total = 0.0
        # Mermas globales
        mn_m, _ = calcular_mermas(q_n); qp_taller = q_n + mn_m
        
        for p in st.session_state.piezas_dict.values():
            nb = q_n * p["pliegos"]
            mn, mi = calcular_mermas(nb, p["im"]=="Digital")
            hc, hp = nb+mn+mi, nb+mn; m2 = (p["w"]*p["h"])/1_000_000
            
            # Materia Prima
            c_mat = (hc*m2*(p.get('gf',0)/1000)*PRECIOS["cartoncillo"][p["pf"]]["precio_kg"])
            if p["pl"] != "Ninguna":
                c_mat += hp * m2 * PRECIOS["planchas"][p["pl"]][p.get('ap','C/C')]
                c_mat += hp * m2 * PRECIOS["planchas"][p["pl"]]["peg"]
            
            # Impresión Offset (simplificado para motor interno)
            c_imp = 120 if p["im"]=="Offset" else (nb*m2*6.5 if p["im"]=="Digital" else 0)
            
            # --- CRITERIO 1000x700 ---
            if p['h'] > 1000 or p['w'] > 700: v_arr, v_tir = 107.80, 0.135
            elif p['h'] < 1000 and p['w'] < 700: v_arr, v_tir = 48.19, 0.06
            else: v_arr, v_tir = 80.77, 0.09
            
            c_arr = v_arr if p.get('cobrar_arreglo') else 0
            c_tir = hp * v_tir if p['cor']=="Troquelado" else hp*1.5
            
            coste_piezas_total += c_mat + c_imp + c_arr + c_tir

        # Extras y Embalajes
        c_ex = sum(e["coste"] * e["cantidad"] * qp_taller for e in st.session_state.lista_extras_grabados)
        c_em = sum(motor_embalajes(em['tipo'], em['l'], em['w'], em['a'], q_n*em['uds']) * (q_n*em['uds']) for em in st.session_state.lista_embalajes)
        
        total_fab = coste_piezas_total + c_ex + c_em + st.session_state.imp_fijo
        oferta_datos.append({"Cant": q_n, "Total": f"{(total_fab*margen):.2f}€", "Ud": f"{(total_fab*margen/q_n):.2f}€"})

with tabs[2]:
    st.subheader("Vista Previa de la Oferta")
    st.markdown(f"""
    <div class="quote-box">
        <h2 class="quote-header">OFERTA DE COLABORACIÓN - BRIEFING {st.session_state.brf}</h2>
        <p><b>Cliente:</b> {st.session_state.cli} | <b>Referencia:</b> {st.session_state.brf}</p>
        <p><b>Proyecto:</b> {st.session_state.des}</p>
        <hr/>
        <h4>Especificaciones del Producto</h4>
        <ul>
            {"".join([f"<li>{p['nombre']}: {p['h']}x{p['w']} mm en {p['pf']}</li>" for p in st.session_state.piezas_dict.values()])}
        </ul>
        <h4>Logística y Accesorios</h4>
        <ul>
            {"".join([f"<li>Caja {em['tipo']} {em['l']}x{em['w']}x{em['a']}</li>" for em in st.session_state.lista_embalajes]) or "<li>Embalaje Estándar Mainsa</li>"}
        </ul>
        <table class="quote-table">
            <tr><th>Cantidad</th><th>Inversión Total (PVP)</th><th>Precio Unitario</th></tr>
            {"".join([f"<tr><td>{r['Cant']} uds</td><td>{r['Total']}</td><td class='unit-price'>{r['Ud']}</td></tr>" for r in oferta_datos])}
        </table>
        <p style='font-size:0.8em; color:gray; margin-top:20px;'>Precios válidos por 30 días. IVA no incluido.</p>
    </div>
    """, unsafe_allow_html=True)
