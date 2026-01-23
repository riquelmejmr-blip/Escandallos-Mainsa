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
st.set_page_config(page_title="MAINSA PLV - PRO", layout="wide")

if 'piezas_dict' not in st.session_state:
    st.session_state.piezas_dict = {0: {"nombre": "Pieza 1", "pliegos": 1.0, "w": 700, "h": 1000, "pf": "Reverso Gris", "gf": 220, "pl": "Ninguna", "ap": "C/C", "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, "ld": False, "pel": "Polipropileno", "cor": "Troquelado"}}

if 'extras_manuales' not in st.session_state:
    st.session_state.extras_manuales = []

# Estilos CSS para el Modo Comercial
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
    c1, c2 = st.columns([1, 5])
    if c1.button("➕ Añadir Forma"):
        new_id = max(st.session_state.piezas_dict.keys()) + 1 if st.session_state.piezas_dict else 0
        st.session_state.piezas_dict[new_id] = {"nombre": f"Parte {new_id+1}", "pliegos": 1.0, "w": 700, "h": 1000, "pf": "Reverso Gris", "gf": 220, "pl": "Ninguna", "ap": "C/C", "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, "ld": False, "pel": "Polipropileno", "cor": "Troquelado"}
        st.rerun()
    if c2.button("🗑 Reiniciar Todo"):
        st.session_state.piezas_dict = {0: {"nombre": "Parte 1", "pliegos": 1.0, "w": 700, "h": 1000, "pf": "Reverso Gris", "gf": 220, "pl": "Ninguna", "ap": "C/C", "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, "ld": False, "pel": "Polipropileno", "cor": "Troquelado"}}
        st.session_state.extras_manuales = []
        st.rerun()

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
                p['pel'] = st.selectbox("Peliculado", list(PRECIOS["peliculado"].keys()), index=(0 if p['im']=="Digital" else 1), key=f"pel_{p_id}")
                p['nt'] = st.number_input("Tintas F.", 1, 6, int(p['nt']), key=f"nt_{p_id}") if p['im'] == "Offset" else 0
                p['ba'] = st.checkbox("Barniz", value=p['ba'], key=f"ba_{p_id}") if p['im'] == "Offset" else False
                p['cor'] = st.selectbox("Corte", ["Troquelado", "Plotter"], key=f"cor_{p_id}")
                if st.button("🗑 Eliminar pieza", key=f"del_{p_id}"): 
                    del st.session_state.piezas_dict[p_id]
                    st.rerun()

    # --- EXTRAS ---
    st.divider()
    st.subheader("📦 Accesorios y Piezas Extra")
    extras_pred = st.multiselect("Seleccionar de la lista:", PRECIOS["extras_base"], key="ex_pred_sel")
    
    st.markdown("**Añadir Extra Manual con Coste Unitario:**")
    ce1, ce2, ce3 = st.columns([3, 2, 1])
    e_nom = ce1.text_input("Nombre elemento (ej: Bolsa tornillos)", key="new_ex_nom")
    e_cost = ce2.number_input("Coste Unitario (€)", 0.0, 100.0, 0.0, step=0.01, key="new_ex_cost")
    if ce3.button("➕ Añadir"):
        if e_nom:
            st.session_state.extras_manuales.append({"nombre": e_nom, "coste": e_cost})
            st.rerun()

    if st.session_state.extras_manuales:
        for i, ex in enumerate(st.session_state.extras_manuales):
            st.info(f"Extra: **{ex['nombre']}** - {ex['coste']}€/ud")
            if st.button(f"Eliminar {ex['nombre']}", key=f"del_ex_{i}"):
                st.session_state.extras_manuales.pop(i)
                st.rerun()

# --- 5. MOTOR DE CÁLCULO ---
res_final = []; desc_full = {}
if lista_cants and st.session_state.piezas_dict:
    for q_n in lista_cants:
        tiene_dig = any(pz["im"] == "Digital" for pz in st.session_state.piezas_dict.values())
        mn_mueble, _ = calcular_mermas(q_n, es_digital=tiene_dig)
        qp_taller = q_n + mn_mueble
        
        det_partidas = []; total_fab = 0.0
        for p_id, p in st.session_state.piezas_dict.items():
            nb = q_n * p["pliegos"]
            is_dig = p["im"] == "Digital"
            mn, mi = calcular_mermas(nb, es_digital=is_dig)
            hc, hp = nb+mn+mi, nb+mn
            m2 = (p["w"]*p["h"])/1_000_000
            
            # Costes por partida
            c_cart = (hc*m2*(p["gf"]/1000)*PRECIOS["cartoncillo"][p["pf"]]["precio_kg"])
            c_plan = (hp * m2 * PRECIOS["planchas"][p["pl"]][p["ap"]]) if p["pl"] != "Ninguna" else 0
            pasadas = (1 if p["pf"]!="Ninguno" else 0) + (1 if p["pd"]!="Ninguno" else 0)
            c_con = (hp * m2 * PRECIOS["planchas"][p["pl"]]["peg"] * pasadas) if p["pl"] != "Ninguna" else 0
            
            c_imp = (nb*m2*6.5) if p["im"] == "Digital" else (0.0 if p["im"] == "No" else (60 if nb<100 else (60+0.15*(nb-100) if nb<500 else (120 if nb<=2000 else 120+0.015*(nb-2000)))) * (p['nt'] + (1 if p['ba'] else 0)))
            c_acab = (hp*m2*PRECIOS["peliculado"][p["pel"]]) + (hp*m2*3.5 if p['ld'] else 0)
            
            c_arr = 107.7 if p["cor"]=="Troquelado" and (p['h']>1000 or p['w']>700) else 48.19 if p["cor"]=="Troquelado" else 0
            c_tir = hp * (0.135 if (p['h']>1000 or p['w']>700) else 0.09) if p["cor"]=="Troquelado" else hp * 1.5
            
            det_partidas.append({"Pieza": p["nombre"], "Carton": c_cart, "Plancha": c_plan, "Contra": c_con, "Imp": c_imp, "Acab": c_acab, "Arreglo": c_arr, "Tiraje": c_tir})

        c_ex_total = sum(ex["coste"] * qp_taller for ex in st.session_state.extras_manuales)
        c_man = ((seg_man/3600)*18*qp_taller) + (qp_taller*dif_ud) + c_ex_total
        t_fab = sum(sum(v for k,v in part.items() if k!="Pieza") for part in det_partidas) + c_man
        desc_full[q_n] = {"det": det_partidas, "man": c_man, "total": t_fab, "qp": qp_taller, "ex_list": extras_pred + [ex['nombre'] for ex in st.session_state.extras_manuales]}
        res_final.append({"Cant": q_n, "Ud": f"{(t_fab*margen/q_n):.2f}€", "Total": f"{(t_fab*margen):.2f}€"})

# --- 6. SALIDA VISUAL ---
if modo_comercial:
    p_html = "".join([f"<li><b>{p['nombre']}:</b> {p['w']}x{p['h']} mm - Imp: {p['im']}</li>" for p in st.session_state.piezas_dict.values()])
    # Recuperamos la información de manipulación para la oferta comercial
    info_q = res_final[0] # Usamos la primera cantidad como referencia de descripción
    ex_nombres = desc_full[info_q['Cant']]['ex_list']
    ex_html = f"<li><b>Accesorios incluidos:</b> {', '.join(ex_nombres)}</li>" if ex_nombres else ""
    filas_html = "".join([f"<tr><td>{r['Cant']} uds</td><td>{r['Total']}</td><td><b>{r['Ud']}</b></td></tr>" for r in res_final])
    
    st.markdown(f"""<div class="comercial-box">
        <h2 class="comercial-header">OFERTA COMERCIAL - MAINSA PLV</h2>
        <div style="margin-top:20px;">
            <h4>1. Descripción del Proyecto</h4>
            <ul>
                {p_html}
                <li><b>Manipulación:</b> Incluye montaje especializado ({seg_man} seg/ud) y mermas de taller.</li>
                {ex_html}
            </ul>
        </div>
        <div style="margin-top:20px;">
            <h4>2. Escala de Precios</h4>
            <table class="comercial-table">
                <tr><th>Cantidad</th><th>PVP Total</th><th>PVP Unitario</th></tr>
                {filas_html}
            </table>
        </div>
        <p style="font-size:0.8em; color:gray; margin-top:30px;">* Precios sin IVA. Validez: 15 días.</p>
    </div>""", unsafe_allow_html=True)
else:
    if res_final:
        st.header("📊 Resumen de Resultados")
        st.dataframe(pd.DataFrame(res_final), use_container_width=True)
        for q, info in desc_full.items():
            with st.expander(f"🔍 Desglose Técnico {q} uds (Taller: {info['qp']} uds)"):
                st.table(pd.DataFrame(info["det"]).style.format("{:.2f}€", subset=pd.DataFrame(info["det"]).columns[1:]))
                st.write(f"**Montaje y Extras Manuales:** {info['man']:.2f}€ | **Coste Fab. Total:** {info['total']:.2f}€")
