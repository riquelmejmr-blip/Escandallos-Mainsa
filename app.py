import streamlit as st
import pandas as pd

# --- 1. BASE DE DATOS DE PRECIOS (Actualizada según tu tabla) ---
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
        "Doble Micro / Doble Doble": {"C/C": 1.046, "B/C": 1.100, "B/B": 1.276, "peg": 0.263},
        "AC (Cuero/Cuero)": {"C/C": 2.505, "peg": 0.217}
    },
    "peliculado": {
        "Sin Peliculado": 0, "Polipropileno": 0.26, "Poliéster brillo": 0.38, "Poliéster mate": 0.64
    },
    "laminado_digital": 3.5,
    "extras": {
        "CINTA D/CARA": 0.26, "CINTA LOHMAN": 0.49, "CINTA GEL": 1.2,
        "GOMA TERMINALES": 0.079, "IMAN 20x2mm": 1.145, "TUBOS": 1.06,
        "REMACHES": 0.049, "VELCRO": 0.43, "PUNTO ADHESIVO": 0.08
    }
}

def calcular_mermas(n, es_digital=False):
    if es_digital: return n * 0.10, 0 # Merma 10% fija para digital
    if n < 100: return 15, 135
    if n < 200: return 30, 150
    if n < 600: return 40, 160
    if n < 1000: return 50, 170
    if n < 2000: return 60, 170
    return 120, 170

# --- 2. CONFIGURACIÓN ---
st.set_page_config(page_title="Escandallos MAINSA PLV", layout="wide")

# Estilos CSS para el Modo Comercial
st.markdown("""
<style>
    .comercial-box { background-color: white; padding: 30px; border: 2px solid #1E88E5; border-radius: 10px; color: #333; }
    .comercial-header { color: #1E88E5; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .comercial-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    .comercial-table th { background-color: #1E88E5; color: white; padding: 10px; text-align: center; }
    .comercial-table td { padding: 10px; border: 1px solid #ddd; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("📦 Escandallos Profesionales MAINSA PLV")

# Gestión de piezas con IDs únicos para evitar errores al borrar
if 'piezas_dict' not in st.session_state:
    st.session_state.piezas_dict = {0: {"nombre": "Parte 1"}}

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

# --- 4. ENTRADA DE DATOS ---
if not modo_comercial:
    c1, c2 = st.columns([1, 5])
    if c1.button("➕ Añadir Forma"):
        new_id = max(st.session_state.piezas_dict.keys()) + 1 if st.session_state.piezas_dict else 0
        st.session_state.piezas_dict[new_id] = {"nombre": f"Parte {new_id+1}"}
        st.rerun()
    if c2.button("🗑 Reiniciar Todo"):
        st.session_state.piezas_dict = {0: {"nombre": "Parte 1"}}
        st.rerun()

datos_pz = []
ids_a_borrar = []

for p_id, p_info in st.session_state.piezas_dict.items():
    if not modo_comercial:
        with st.expander(f"🛠 Configuración: {p_info['nombre']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                nombre = st.text_input("Nombre Pieza", p_info['nombre'], key=f"n_{p_id}")
                pliegos = st.number_input("Pliegos/Mueble (decimal ok)", 0.0, 100.0, 1.0, step=0.1, key=f"p_{p_id}")
                w = st.number_input("Ancho (mm)", 1, 5000, 700, key=f"w_{p_id}")
                h = st.number_input("Largo (mm)", 1, 5000, 1000, key=f"h_{p_id}")
            with col2:
                pf = st.selectbox("C. Frontal", list(PRECIOS["cartoncillo"].keys()), 1, key=f"pf_{p_id}")
                gf = st.number_input("G. Frontal", PRECIOS["cartoncillo"][pf]["gramaje"], key=f"gf_{p_id}") if pf != "Ninguno" else 0
                pl = st.selectbox("Plancha Base", list(PRECIOS["planchas"].keys()), key=f"pl_{p_id}")
                ap = st.selectbox("Calidad Plancha", ["C/C", "B/C", "B/B"], 1, key=f"ap_{p_id}") if pl != "Ninguna" else "C/C"
                pd_s = st.selectbox("C. Dorso", list(PRECIOS["cartoncillo"].keys()), index=0, key=f"pd_{p_id}")
                gd = st.number_input("G. Dorso", PRECIOS["cartoncillo"][pd_s]["gramaje"], key=f"gd_{p_id}") if pd_s != "Ninguno" else 0
            with col3:
                im = st.selectbox("Impresión", ["Offset", "Digital", "No"], key=f"im_{p_id}")
                ld = st.checkbox("Laminado Digital (3.5€)", key=f"ld_{p_id}") if im == "Digital" else False
                pel = st.selectbox("Peliculado", list(PRECIOS["peliculado"].keys()), index=(0 if im=="Digital" else 1), key=f"pel_{p_id}")
                nt = st.number_input("Tintas F.", 1, 6, 4, key=f"nt_{p_id}") if im == "Offset" else 0
                ba = st.checkbox("Barniz", key=f"ba_{p_id}") if im == "Offset" else False
                cor = st.selectbox("Corte", ["Troquelado", "Plotter"], key=f"cor_{p_id}")
                if st.button("🗑 Eliminar esta pieza", key=f"del_{p_id}"): ids_a_borrar.append(p_id)
            
            datos_pz.append({"nombre": nombre, "pliegos": pliegos, "w": w, "h": h, "pf": pf, "gf": gf, "pl": pl, "ap": ap, "pd": pd_s, "gd": gd, "im": im, "nt": nt, "ba": ba, "ld": ld, "pel": pel, "cor": cor})
    else:
        # En modo comercial, solo cargamos los datos ya guardados sin mostrar editores
        datos_pz.append({"nombre": p_info['nombre'], "pliegos": 1.0, "w": 700, "h": 1000, "pf": "Zenith", "gf": 350, "pl": "Ninguna", "ap": "C/C", "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, "ld": False, "pel": "Polipropileno", "cor": "Troquelado"})

for b_id in ids_a_borrar:
    del st.session_state.piezas_dict[b_id]
    st.rerun()

# --- 5. MOTOR DE CÁLCULO ---
res_final = []; desc_full = {}
if lista_cants and datos_pz:
    for q_n in lista_cants:
        tiene_dig = any(d["im"] == "Digital" for d in datos_pz)
        mn_mueble, _ = calcular_mermas(q_n, es_digital=tiene_dig)
        qp_taller = q_n + mn_mueble
        
        det_partidas = []; total_fab = 0.0
        for p in datos_pz:
            nb = q_n * p["pliegos"]
            is_dig = p["im"] == "Digital"
            mn, mi = calcular_mermas(nb, es_digital=is_dig)
            hc, hp = nb+mn+mi, nb+mn
            m2 = (p["w"]*p["h"])/1_000_000
            
            # Partidas
            c_cart = (hc*m2*(p["gf"]/1000)*PRECIOS["cartoncillo"][p["pf"]]["precio_kg"]) + (hc*m2*(p["gd"]/1000)*PRECIOS["cartoncillo"][p["pd"]]["precio_kg"])
            c_plan, c_con = 0.0, 0.0
            if p["pl"] != "Ninguna":
                c_plan = hp * m2 * PRECIOS["planchas"][p["pl"]][p["ap"]]
                pasadas = (1 if p["pf"]!="Ninguno" else 0) + (1 if p["pd"]!="Ninguno" else 0)
                c_con = hp * m2 * PRECIOS["planchas"][p["pl"]]["peg"] * pasadas
            
            c_imp = (nb*m2*6.5) if p["im"] == "Digital" else (0.0 if p["im"] == "No" else (60 if nb<100 else (60+0.15*(nb-100) if nb<500 else (120 if nb<=2000 else 120+0.015*(nb-2000)))) * (p["nt"] + (1 if p["ba"] else 0)))
            c_acab = (hp*m2*PRECIOS["peliculado"][p["pel"]]) + (hp*m2*PRECIOS["laminado_digital"] if p["ld"] else 0)
            
            c_arr, c_tir = 0.0, (hp*1.5 if p["cor"]=="Plotter" else 0.0)
            if p["cor"] == "Troquelado":
                c_arr = 107.7 if (p['h']>1000 or p['w']>700) else (80.77 if (p['h']==1000 and p['w']==700) else 48.19)
                c_tir = hp * (0.135 if (p['h']>1000 or p['w']>700) else (0.09 if (p['h']==1000 and p['w']==700) else 0.06))
            
            det_partidas.append({"Pieza": p["nombre"], "Carton": c_cart, "Plancha": c_plan, "Contra": c_con, "Imp": c_imp, "Acab": c_acab, "Arreglo": c_arr, "Tiraje": c_tir})

        c_man = ((seg_man/3600)*18*qp_taller) + (qp_taller*dif_ud)
        t_fab = sum(sum(v for k,v in part.items() if k!="Pieza") for part in det_partidas) + c_man
        desc_full[q_n] = {"det": det_partidas, "man": c_man, "total": t_fab, "qp": qp_taller}
        res_final.append({"Cant": q_n, "Ud": f"{(t_fab*margen/q_n):.2f}€", "Total": f"{(t_fab*margen):.2f}€"})

# --- 6. SALIDA VISUAL ---
if modo_comercial:
    # Construcción robusta del HTML
    lista_html = "".join([f"<li><b>{p['nombre']}:</b> {p['w']}x{p['h']} mm - Imp: {p['im']}</li>" for p in datos_pz])
    filas_tabla = "".join([f"<tr><td>{r['Cant']} uds</td><td>{r['Total']}</td><td><b>{r['Ud']}</b></td></tr>" for r in res_final])
    
    st.markdown(f"""
    <div class="comercial-box">
        <h2 class="comercial-header">OFERTA COMERCIAL - MAINSA PLV</h2>
        <div style="margin-top: 20px;">
            <h4>1. Formatos y Componentes</h4>
            <ul>{lista_html}</ul>
        </div>
        <div style="margin-top: 20px;">
            <h4>2. Manipulación y Entrega</h4>
            <p>El presupuesto incluye montaje y manipulado especializado ({seg_man} seg/ud).</p>
        </div>
        <div style="margin-top: 20px;">
            <h4>3. Escala de Precios</h4>
            <table class="comercial-table">
                <tr><th>Cantidad</th><th>PVP Total</th><th>PVP Unitario</th></tr>
                {filas_tabla}
            </table>
        </div>
        <p style="font-size: 0.8em; color: gray; margin-top: 30px;">* Precios sin IVA. Validez: 15 días.</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("💡 Consejo: Pulsa Ctrl+P (o Cmd+P) para imprimir esta oferta o guardarla como PDF.")
else:
    if res_final:
        st.header("📊 Resumen de Resultados")
        st.dataframe(pd.DataFrame(res_final), use_container_width=True)
        for q, info in desc_full.items():
            with st.expander(f"🔍 Desglose Técnico {q} uds (Procesando {info['qp']} uds)"):
                st.table(pd.DataFrame(info["det"]).style.format("{:.2f}€", subset=pd.DataFrame(info["det"]).columns[1:]))
                st.write(f"**Mano de Obra y Merma Manipulado:** {info['man']:.2f}€ | **Total Fab:** {info['total']:.2f}€")
