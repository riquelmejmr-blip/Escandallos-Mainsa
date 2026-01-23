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

# --- 2. INICIALIZACIÓN DE ESTADO ---
st.set_page_config(page_title="Escandallos MAINSA PLV", layout="wide")

if 'piezas_dict' not in st.session_state:
    st.session_state.piezas_dict = {0: {"nombre": "Parte 1", "pliegos": 1.0, "w": 700, "h": 1000, "pf": "Reverso Gris", "gf": 220, "pl": "Ninguna", "ap": "C/C", "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, "ld": False, "pel": "Polipropileno", "cor": "Troquelado"}}

# Lista única persistente para todos los extras (predeterminados y manuales)
if 'lista_extras_grabados' not in st.session_state:
    st.session_state.lista_extras_grabados = []

st.markdown("""<style>
    .comercial-box { background-color: white; padding: 30px; border: 2px solid #1E88E5; border-radius: 10px; color: #333; }
    .comercial-header { color: #1E88E5; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; }
</style>""", unsafe_allow_html=True)

st.title("📦 Escandallos Profesionales MAINSA PLV")

# --- 3. PANEL LATERAL ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_str = st.text_input("Cantidades", "200, 500, 1000")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    st.divider()
    seg_man = st.number_input("Segundos Manipulación / Ud", value=300)
    dif_ud = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], index=2)
    margen = st.number_input("Multiplicador Comercial", value=2.2, step=0.1)
    st.divider()
    modo_comercial = st.checkbox("🌟 VISTA OFERTA COMERCIAL", value=False)

# --- 4. GESTIÓN DE DATOS (Solo en modo edición) ---
if not modo_comercial:
    # Gestión de Formas
    c1, c2 = st.columns([1, 5])
    if c1.button("➕ Añadir Forma"):
        new_id = max(st.session_state.piezas_dict.keys()) + 1 if st.session_state.piezas_dict else 0
        st.session_state.piezas_dict[new_id] = {"nombre": f"Parte {new_id+1}", "pliegos": 1.0, "w": 700, "h": 1000, "pf": "Reverso Gris", "gf": 220, "pl": "Ninguna", "ap": "C/C", "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, "ld": False, "pel": "Polipropileno", "cor": "Troquelado"}
        st.rerun()
    if c2.button("🗑 Reiniciar Todo"):
        st.session_state.piezas_dict = {0: {"nombre": "Parte 1", "pliegos": 1.0, "w": 700, "h": 1000, "pf": "Reverso Gris", "gf": 220, "pl": "Ninguna", "ap": "C/C", "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, "ld": False, "pel": "Polipropileno", "cor": "Troquelado"}}
        st.session_state.lista_extras_grabados = []
        st.rerun()

    for p_id in list(st.session_state.piezas_dict.keys()):
        p = st.session_state.piezas_dict[p_id]
        with st.expander(f"🛠 Configuración: {p['nombre']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                p['nombre'] = st.text_input("Nombre", p['nombre'], key=f"n_{p_id}")
                p['pliegos'] = st.number_input("Pliegos/Ud", 0.0, 100.0, float(p['pliegos']), step=0.1, key=f"p_{p_id}")
                p['w'], p['h'] = st.number_input("Ancho", 1, 5000, int(p['w']), key=f"w_{p_id}"), st.number_input("Largo", 1, 5000, int(p['h']), key=f"h_{p_id}")
            with col2:
                p['pf'] = st.selectbox("C. Frontal", list(PRECIOS["cartoncillo"].keys()), list(PRECIOS["cartoncillo"].keys()).index(p['pf']), key=f"pf_{p_id}")
                p['pl'] = st.selectbox("Plancha", list(PRECIOS["planchas"].keys()), list(PRECIOS["planchas"].keys()).index(p['pl']), key=f"pl_{p_id}")
                p['ap'] = st.selectbox("Calidad", ["C/C", "B/C", "B/B"], 1, key=f"ap_{p_id}") if p['pl'] != "Ninguna" else "C/C"
            with col3:
                p['im'] = st.selectbox("Impresión", ["Offset", "Digital", "No"], list(["Offset", "Digital", "No"]).index(p['im']), key=f"im_{p_id}")
                p['ld'] = st.checkbox("Laminado Digital", value=p['ld'], key=f"ld_{p_id}") if p['im'] == "Digital" else False
                p['cor'] = st.selectbox("Corte", ["Troquelado", "Plotter"], key=f"cor_{p_id}")
                if st.button("🗑 Borrar", key=f"del_{p_id}"): del st.session_state.piezas_dict[p_id]; st.rerun()

    # --- SECCIÓN DE EXTRAS PERSISTENTE ---
    st.divider()
    st.subheader("📦 Almacén de Accesorios y Extras")
    
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        st.markdown("**Añadir desde la lista:**")
        ex_sel = st.selectbox("Selecciona accesorio:", ["---"] + list(PRECIOS["extras_base"].keys()))
        cant_sel = st.number_input("Cantidad por mueble:", 1.0, 1000.0, 1.0, key="q_ex_base")
        if st.button("➕ Añadir Accesorio"):
            if ex_sel != "---":
                st.session_state.lista_extras_grabados.append({"nombre": ex_sel, "coste": PRECIOS["extras_base"][ex_sel], "cantidad": cant_sel})
                st.rerun()
    
    with col_ex2:
        st.markdown("**Añadir Extra Manual:**")
        e_nom = st.text_input("Nombre (ej: Bolsa)", key="ex_man_n")
        e_cost = st.number_input("Coste Unitario (€)", 0.0, 100.0, 0.0, key="ex_man_c")
        e_q = st.number_input("Cantidad por mueble:", 1.0, 1000.0, 1.0, key="ex_man_q")
        if st.button("➕ Añadir Manual"):
            if e_nom:
                st.session_state.lista_extras_grabados.append({"nombre": e_nom, "coste": e_cost, "cantidad": e_q})
                st.rerun()

    # --- LISTADO DE EXTRAS AÑADIDOS ---
    if st.session_state.lista_extras_grabados:
        st.markdown("### 📋 Extras añadidos actualmente:")
        for i, extra in enumerate(st.session_state.lista_extras_grabados):
            c_a, c_b, c_c, c_d = st.columns([3, 2, 2, 1])
            c_a.write(f"**{extra['nombre']}**")
            c_b.write(f"{extra['coste']}€/ud")
            c_c.write(f"x{extra['cantidad']} uds/mueble")
            if c_d.button("🗑", key=f"del_gr_{i}"):
                st.session_state.lista_extras_grabados.pop(i)
                st.rerun()

# --- 5. MOTOR DE CÁLCULO (Usa session_state siempre) ---
res_final, desc_full = [], {}
if lista_cants and st.session_state.piezas_dict:
    for q_n in lista_cants:
        tiene_dig = any(pz["im"] == "Digital" for pz in st.session_state.piezas_dict.values())
        mn_m, _ = calcular_mermas(q_n, es_digital=tiene_dig)
        qp_taller = q_n + mn_m
        
        coste_f, det_f = 0.0, []
        for p_id, p in st.session_state.piezas_dict.items():
            nb = q_n * p["pliegos"]
            mn, mi = calcular_mermas(nb, es_digital=(p["im"]=="Digital"))
            hc, hp = nb+mn+mi, nb+mn
            m2 = (p["w"]*p["h"])/1_000_000
            c_mat = (hc*m2*(p.get('gf',220)/1000)*PRECIOS["cartoncillo"][p["pf"]]["precio_kg"])
            c_pla = (hp*m2*PRECIOS["planchas"][p["pl"]][p["ap"]]) if p["pl"] != "Ninguna" else 0
            c_imp = (nb*m2*6.5) if p["im"] == "Digital" else (0.0 if p["im"]=="No" else (120 if nb>500 else 60)*4)
            c_acab = (hp*m2*3.5 if p.get('ld',False) else hp*m2*0.26)
            c_trq = 107.7 + (hp*0.135) if p["cor"]=="Troquelado" else hp*1.5
            coste_f += (c_mat + c_pla + c_imp + c_acab + c_trq)
            det_f.append({"Pieza": p["nombre"], "Mat": c_mat, "Plancha": c_pla, "Imp": c_imp, "Acab": c_acab, "Corte": c_trq, "Total": c_mat+c_pla+c_imp+c_acab+c_trq})

        # Cálculo de todos los extras grabados en session_state
        c_extras_total = sum(e["coste"] * e["cantidad"] * qp_taller for e in st.session_state.lista_extras_grabados)
        
        c_man = ((seg_man/3600)*18*qp_taller) + (qp_taller*dif_ud) + c_extras_total
        t_fab = coste_f + c_man
        desc_full[q_n] = {"det": det_f, "man": c_man, "total": t_fab, "qp": qp_taller}
        res_final.append({"Cant": q_n, "Ud": f"{(t_fab*margen/q_n):.2f}€", "Total": f"{(t_fab*margen):.2f}€"})

# --- 6. VISTA COMERCIAL ---
if modo_comercial:
    p_html = "".join([f"<li><b>{p['nombre']}:</b> {p['w']}x{p['h']} mm - {p['im']}</li>" for p in st.session_state.piezas_dict.values()])
    # Recuperamos extras de la lista grabada
    ex_nombres = [f"{e['nombre']} (x{e['cantidad']})" for e in st.session_state.lista_extras_grabados]
    ex_html = f"<li><b>Accesorios:</b> {', '.join(ex_nombres)}</li>" if ex_nombres else ""
    filas_html = "".join([f"<tr><td style='border:1px solid #ddd;padding:10px;'>{r['Cant']} uds</td><td style='border:1px solid #ddd;padding:10px;'>{r['Total']}</td><td style='border:1px solid #ddd;padding:10px;'><b>{r['Ud']}</b></td></tr>" for r in res_final])
    
    st.markdown(f"""<div class="comercial-box">
        <h2 class="comercial-header">OFERTA COMERCIAL - MAINSA PLV</h2>
        <div style="margin-top:20px;">
            <h4>1. Especificaciones</h4>
            <ul>{p_html}{ex_html}<li><b>Montaje:</b> Incluido ({seg_man} seg/ud).</li></ul>
        </div>
        <table style="width:100%;border-collapse:collapse;margin-top:20px;text-align:center;">
            <tr style="background:#1E88E5;color:white;"><th>Cantidad</th><th>PVP Total</th><th>PVP Unitario</th></tr>
            {filas_html}
        </table>
    </div>""", unsafe_allow_html=True)
else:
    if res_final:
        st.header("📊 Resultados")
        st.dataframe(pd.DataFrame(res_final), use_container_width=True)
        for q, info in desc_full.items():
            with st.expander(f"🔍 Desglose {q} uds"):
                st.table(pd.DataFrame(info["det"]))
                st.write(f"**Montaje y Extras Totales:** {info['man']:.2f}€ | **Total Fab:** {info['total']:.2f}€")
