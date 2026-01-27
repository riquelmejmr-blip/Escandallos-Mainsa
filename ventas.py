import streamlit as st
import pandas as pd
import json

# --- 1. MOTOR INTERNO (Idéntico a Producción para total precisión) ---
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

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="COMERCIAL MAINSA", layout="wide")

def crear_forma_vacia(index):
    return {
        "nombre": f"Pieza {index + 1}", "pliegos": 1.0, "w": 0, "h": 0, 
        "pf": "Ninguno", "gf": 0, "pl": "Ninguna", "ap": "C/C", 
        "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, 
        "im_d": "No", "nt_d": 0, "ba_d": False, "pel": "Sin Peliculado", 
        "pel_d": "Sin Peliculado", "ld": False, "ld_d": False, 
        "cor": "Troquelado", "cobrar_arreglo": True
    }

# Sesión
for key, default in [('piezas_dict', {0: crear_forma_vacia(0)}), ('lista_extras_grabados', []), 
                     ('lista_embalajes', []), ('brf', ""), ('cli', ""), ('com', ""), 
                     ('ver', "1.0"), ('des', ""), ('imp_fijo', 500)]:
    if key not in st.session_state: st.session_state[key] = default

# Estilos Visuales
st.markdown("""<style>
    .comercial-box { background-color: #ffffff; padding: 40px; border: 1px solid #e0e0e0; border-radius: 5px; color: #1a1a1a; box-shadow: 2px 2px 15px rgba(0,0,0,0.05); }
    .comercial-header { color: #0D47A1; border-bottom: 3px solid #0D47A1; padding-bottom: 10px; margin-bottom: 25px; }
    .comercial-table { width: 100%; border-collapse: collapse; margin-top: 25px; }
    .comercial-table th { background-color: #f5f5f5; color: #333; padding: 12px; text-align: left; border-bottom: 2px solid #0D47A1; }
    .comercial-table td { padding: 12px; border-bottom: 1px solid #eee; }
    .price-tag { font-size: 1.2em; font-weight: bold; color: #0D47A1; }
</style>""", unsafe_allow_html=True)

st.title("🚀 GESTOR COMERCIAL MAINSA")

# --- 3. PANEL LATERAL: CONFIGURACIÓN DE VENTA ---
with st.sidebar:
    st.header("📋 Información del Cliente")
    st.session_state.cli = st.text_input("Nombre del Cliente", st.session_state.cli)
    st.session_state.brf = st.text_input("Nº de Briefing / Oferta", st.session_state.brf)
    st.session_state.com = st.text_input("Vendedor", st.session_state.com)
    st.session_state.des = st.text_area("Descripción del proyecto", st.session_state.des)
    
    st.divider()
    st.header("💰 Parámetros de Precio")
    cants_str = st.text_input("Cantidades a presupuestar", "500, 1000, 2000")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    
    margen = st.number_input("Multiplicador Comercial", value=2.2, step=0.1, help="Multiplicador sobre el coste de taller")
    
    st.divider()
    st.header("📂 Gestión de Archivos")
    partes_nombre = [st.session_state.brf, st.session_state.cli]
    nombre_archivo = "P_COMERCIAL_" + "_".join([str(p).strip() for p in partes_nombre if str(p).strip()]) + ".json"
    
    datos_exportar = {
        "brf": st.session_state.brf, "cli": st.session_state.cli, "com": st.session_state.com,
        "ver": st.session_state.ver, "des": st.session_state.des, "piezas": st.session_state.piezas_dict,
        "extras": st.session_state.lista_extras_grabados, "embalajes": st.session_state.lista_embalajes,
        "imp_fijo": st.session_state.imp_fijo
    }
    st.download_button("💾 Guardar Presupuesto", json.dumps(datos_exportar, indent=4), file_name=nombre_archivo)
    
    archivo_subido = st.file_uploader("📂 Cargar Presupuesto", type=["json"])
    if archivo_subido:
        data = json.load(archivo_subido)
        st.session_state.brf, st.session_state.cli, st.session_state.piezas_dict = data.get("brf"), data.get("cli"), {int(k): v for k, v in data["piezas"].items()}
        st.session_state.lista_extras_grabados, st.session_state.lista_embalajes = data.get("extras"), data.get("embalajes")
        st.rerun()

# --- 4. ÁREA DE DISEÑO DEL PRODUCTO ---
tabs = st.tabs(["🏗️ Estructura del Producto", "📦 Extras y Embalajes", "📄 VISTA PREVIA OFERTA"])

with tabs[0]:
    st.subheader("Definición de Piezas")
    if st.button("➕ Añadir otra pieza"):
        nid = max(st.session_state.piezas_dict.keys()) + 1
        st.session_state.piezas_dict[nid] = crear_forma_vacia(nid); st.rerun()

    for p_id, p in st.session_state.piezas_dict.items():
        with st.expander(f"💎 {p['nombre']} - {p['h']}x{p['w']} mm", expanded=True):
            c1, c2, c3 = st.columns(3)
            p['nombre'] = c1.text_input("Nombre de la pieza", p['nombre'], key=f"n_{p_id}")
            p['h'] = c2.number_input("Largo (mm)", 0, 5000, int(p['h']), key=f"h_{p_id}")
            p['w'] = c3.number_input("Ancho (mm)", 0, 5000, int(p['w']), key=f"w_{p_id}")
            
            p['pf'] = c1.selectbox("Material Principal", list(PRECIOS["cartoncillo"].keys()), key=f"pf_{p_id}")
            p['pl'] = c2.selectbox("Soporte Base", list(PRECIOS["planchas"].keys()), key=f"pl_{p_id}")
            p['im'] = c3.selectbox("Tipo Impresión", ["Offset", "Digital", "No"], key=f"im_{p_id}")
            
            if c3.button("🗑 Quitar pieza", key=f"del_{p_id}"):
                del st.session_state.piezas_dict[p_id]; st.rerun()

with tabs[1]:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Accesorios Adicionales")
        ex_sel = st.selectbox("Seleccionar Accesorio:", ["---"] + list(PRECIOS["extras_base"].keys()))
        if st.button("➕ Añadir Accesorio") and ex_sel != "---":
            st.session_state.lista_extras_grabados.append({"nombre": ex_sel, "coste": PRECIOS["extras_base"][ex_sel], "cantidad": 1.0}); st.rerun()
        for i, ex in enumerate(st.session_state.lista_extras_grabados):
            st.caption(f"**{ex['nombre']}**")
            cx1, cx2, cx3 = st.columns([2, 2, 1])
            ex['cantidad'] = cx1.number_input("Cant/Ud", value=float(ex['cantidad']), key=f"exq_{i}")
            if cx3.button("🗑", key=f"exd_{i}"): st.session_state.lista_extras_grabados.pop(i); st.rerun()

    with col_b:
        st.subheader("Cajas de Envío")
        tipo_em = st.selectbox("Tipo de Caja:", ["Plano (Canal 5)", "En Volumen", "Guainas"])
        if st.button("➕ Añadir Caja"):
            st.session_state.lista_embalajes.append({"tipo": tipo_em, "l": 0, "w": 0, "a": 0, "uds": 1}); st.rerun()
        for i, em in enumerate(st.session_state.lista_embalajes):
            st.caption(f"**Caja {i+1}: {em['tipo']}**")
            ce1, ce2, ce3, ce4, ce5 = st.columns(5)
            em['l'], em['w'], em['a'], em['uds'] = ce1.number_input("L", value=em['l'], key=f"el_{i}"), ce2.number_input("W", value=em['w'], key=f"ew_{i}"), ce3.number_input("A", value=em['a'], key=f"ea_{i}"), ce4.number_input("Cant", value=em['uds'], key=f"eu_{i}")
            if ce5.button("🗑", key=f"ed_{i}"): st.session_state.lista_embalajes.pop(i); st.rerun()

# --- 5. CÁLCULO Y VISTA COMERCIAL ---
res_final = []
if lista_cants and sum(lista_cants) > 0:
    for q_n in lista_cants:
        coste_f = 0.0
        mn_m, _ = calcular_mermas(q_n); qp_taller = q_n + mn_m
        for p in st.session_state.piezas_dict.values():
            m2 = (p['w']*p['h'])/1_000_000
            # Triple Criterio Arreglo 1000x700
            if p['h'] > 1000 or p['w'] > 700: v_arr, v_tir = 107.80, 0.135
            elif p['h'] < 1000 and p['w'] < 700: v_arr, v_tir = 48.19, 0.06
            else: v_arr, v_tir = 80.77, 0.09
            coste_f += (v_arr if p['cobrar_arreglo'] else 0) + (q_n * v_tir)
            # Sumar material simplificado
            coste_f += (qp_taller * m2 * 0.5) # Estimación rápida para ventas
        
        c_ex = sum(e["coste"] * e["cantidad"] * qp_taller for e in st.session_state.lista_extras_grabados)
        c_em = sum(motor_embalajes(em['tipo'], em['l'], em['w'], em['a'], q_n*em['uds']) * (q_n*em['uds']) for em in st.session_state.lista_embalajes)
        
        total_taller = coste_f + c_ex + c_em + st.session_state.imp_fijo
        res_final.append({"Cant": q_n, "Total": f"{(total_taller*margen):.2f}€", "Ud": f"{(total_taller*margen/q_n):.2f}€"})

with tabs[2]:
    st.markdown(f"""<div class="comercial-box">
        <h1 class="comercial-header">PRESUPUESTO COMERCIAL - {st.session_state.cli}</h1>
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <span><b>Referencia:</b> {st.session_state.brf}</span>
            <span><b>Fecha:</b> 2026</span>
            <span><b>Comercial:</b> {st.session_state.com}</span>
        </div>
        <p><b>Descripción del Proyecto:</b><br/>{st.session_state.des}</p>
        <h4>1. Especificaciones Técnicas</h4>
        <ul>
            {"".join([f"<li><b>{p['nombre']}:</b> {p['h']}x{p['w']} mm en {p['pf']}</li>" for p in st.session_state.piezas_dict.values()])}
        </ul>
        <h4>2. Logística y Embalaje</h4>
        <ul>
            {"".join([f"<li>Caja {em['tipo']} {em['l']}x{em['w']}x{em['a']} mm</li>" for em in st.session_state.lista_embalajes]) or "<li>Estándar Mainsa</li>"}
        </ul>
        <table class="comercial-table">
            <tr><th>Cantidad</th><th>Precio Total (PVP)</th><th>Precio Unitario</th></tr>
            {"".join([f"<tr><td>{r['Cant']} unidades</td><td class='price-tag'>{r['Total']}</td><td><b>{r['Ud']}</b></td></tr>" for r in res_final])}
        </table>
        <p style="margin-top: 30px; font-size: 0.8em; color: #666;">* Precios sujetos a revisión tras recepción de artes finales. IVA no incluido.</p>
    </div>""", unsafe_allow_html=True)
