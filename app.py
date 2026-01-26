import streamlit as st
import pandas as pd
import json # Librería para gestionar el archivo de guardado

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

# --- 2. INICIALIZACIÓN DE SESIÓN ---
st.set_page_config(page_title="MAINSA PLV - PRO", layout="wide")

def crear_forma_vacia(index):
    return {
        "nombre": f"Forma {index + 1}", "pliegos": 1.0, "w": 0, "h": 0, 
        "pf": "Ninguno", "gf": 0, "pl": "Ninguna", "ap": "C/C", 
        "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, 
        "im_d": "No", "nt_d": 1, "ba_d": False, "pel": "Sin Peliculado", 
        "pel_d": "Sin Peliculado", "ld": False, "ld_d": False, 
        "cor": "Troquelado", "cobrar_arreglo": True
    }

if 'piezas_dict' not in st.session_state:
    st.session_state.piezas_dict = {0: crear_forma_vacia(0)}
if 'lista_extras_grabados' not in st.session_state:
    st.session_state.lista_extras_grabados = []

st.markdown("""<style>
    .comercial-box { background-color: white; padding: 30px; border: 2px solid #1E88E5; border-radius: 10px; color: #333; font-family: sans-serif; }
    .comercial-header { color: #1E88E5; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .comercial-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.9em; }
    .comercial-table th { background-color: #1E88E5; color: white; padding: 10px; }
    .comercial-table td { padding: 10px; border: 1px solid #ddd; text-align: center; }
</style>""", unsafe_allow_html=True)

st.title("📦 Escandallos Profesionales MAINSA PLV")

# --- 3. PANEL LATERAL (CON GESTIÓN DE ARCHIVOS) ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    
    # Identificación del proyecto
    num_proy = st.text_input("Nº Proyecto", "PROY-001")
    cliente = st.text_input("Cliente", "Nombre Cliente")
    
    st.divider()
    cants_str = st.text_input("Cantidades", "0")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    
    st.divider()
    unidad_tiempo = st.radio("Unidad de manipulación:", ["Segundos", "Minutos"], horizontal=True)
    tiempo_input = st.number_input(f"Tiempo de montaje ({unidad_tiempo})", value=0)
    seg_man_total = tiempo_input * 60 if unidad_tiempo == "Minutos" else tiempo_input
    
    dif_ud = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], index=2)
    margen = st.number_input("Multiplicador Comercial", value=2.2, step=0.1)
    
    st.divider()
    modo_comercial = st.checkbox("🌟 VISTA OFERTA COMERCIAL", value=False)

    st.divider()
    st.header("📂 Gestión de Proyecto")
    
    # Lógica de Exportación (Guardar)
    datos_exportar = {
        "num_proy": num_proy, "cliente": cliente,
        "piezas_dict": st.session_state.piezas_dict,
        "lista_extras": st.session_state.lista_extras_grabados,
        "globales": {"unidad_tiempo": unidad_tiempo, "tiempo_input": tiempo_input, "dif_ud": dif_ud, "margen": margen}
    }
    json_str = json.dumps(datos_exportar, indent=4)
    st.download_button(label="💾 Descargar Proyecto (.json)", data=json_str, file_name=f"{num_proy}_{cliente}.json", mime="application/json")

    # Lógica de Importación (Abrir)
    archivo_subido = st.file_uploader("📂 Abrir Proyecto Existente", type=["json"])
    if archivo_subido is not None:
        datos_importados = json.load(archivo_subido)
        # Forzar actualización de session_state
        st.session_state.piezas_dict = {int(k): v for k, v in datos_importados["piezas_dict"].items()}
        st.session_state.lista_extras_grabados = datos_importados["lista_extras"]
        st.success("Proyecto cargado. La página se actualizará.")
        st.button("Confirmar Carga") # Botón para disparar el rerun manualmente si el navegador no lo hace

# --- 4. GESTIÓN DE FORMAS Y EXTRAS ---
if not modo_comercial:
    c1, c2 = st.columns([1, 5])
    if c1.button("➕ Añadir Forma"):
        nid = max(st.session_state.piezas_dict.keys()) + 1 if st.session_state.piezas_dict else 0
        st.session_state.piezas_dict[nid] = crear_forma_vacia(nid)
        st.rerun()
    if c2.button("🗑 Reiniciar Todo"):
        st.session_state.piezas_dict = {0: crear_forma_vacia(0)}
        st.session_state.lista_extras_grabados = []
        st.rerun()

    for p_id in list(st.session_state.piezas_dict.keys()):
        p = st.session_state.piezas_dict[p_id]
        with st.expander(f"🛠 {p['nombre']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                p['nombre'] = st.text_input("Etiqueta", p['nombre'], key=f"n_{p_id}")
                p['pliegos'] = st.number_input("Pliegos/Ud", 0.0, 100.0, float(p['pliegos']), step=0.1, key=f"p_{p_id}")
                p['w'], p['h'] = st.number_input("Ancho mm", 0, 5000, int(p['w']), key=f"w_{p_id}"), st.number_input("Largo mm", 0, 5000, int(p['h']), key=f"h_{p_id}")
                st.markdown("**Impresión Cara**")
                p['im'] = st.selectbox("Sistema Cara", ["Offset", "Digital", "No"], ["Offset", "Digital", "No"].index(p['im']), key=f"im_{p_id}")
                if p['im'] == "Offset":
                    p['nt'] = st.number_input("Tintas F.", 1, 6, max(1, int(p.get('nt',4))), key=f"nt_{p_id}")
                    p['ba'] = st.checkbox("Barniz F.", p.get('ba',False), key=f"ba_{p_id}")
                elif p['im'] == "Digital":
                    p['ld'] = st.checkbox("Laminado Digital F.", p.get('ld',False), key=f"ld_{p_id}")
                p['pel'] = st.selectbox("Peliculado Cara", list(PRECIOS["peliculado"].keys()), list(PRECIOS["peliculado"].keys()).index(p.get('pel','Sin Peliculado')), key=f"pel_{p_id}")

            with col2:
                st.markdown("**Materia Prima**")
                pf_prev = p['pf']
                p['pf'] = st.selectbox("C. Frontal", list(PRECIOS["cartoncillo"].keys()), list(PRECIOS["cartoncillo"].keys()).index(p['pf']), key=f"pf_{p_id}")
                if p['pf'] != pf_prev: p['gf'] = PRECIOS["cartoncillo"][p['pf']]["gramaje"]
                if p['pf'] != "Ninguno": p['gf'] = st.number_input("Gramaje F.", value=int(p['gf']), key=f"gf_{p_id}")
                p['pl'] = st.selectbox("Plancha Base", list(PRECIOS["planchas"].keys()), list(PRECIOS["planchas"].keys()).index(p['pl']), key=f"pl_{p_id}")
                p['ap'] = st.selectbox("Calidad", ["C/C", "B/C", "B/B"], key=f"ap_{p_id}") if p['pl'] != "Ninguna" else "C/C"
                pd_prev = p['pd']
                p['pd'] = st.selectbox("C. Dorso", list(PRECIOS["cartoncillo"].keys()), list(PRECIOS["cartoncillo"].keys()).index(p['pd']), key=f"pd_{p_id}")
                if p['pd'] != pd_prev: p['gd'] = PRECIOS["cartoncillo"][p['pd']]["gramaje"]
                if p['pd'] != "Ninguno": p['gd'] = st.number_input("Gramaje D.", value=int(p['gd']), key=f"gd_{p_id}")

            with col3:
                st.markdown("**Corte y Arreglo**")
                p['cor'] = st.selectbox("Tipo de Corte", ["Troquelado", "Plotter"], key=f"cor_{p_id}")
                if p['cor'] == "Troquelado":
                    p['cobrar_arreglo'] = st.checkbox("¿Cobrar Arreglo Troquel?", value=p.get('cobrar_arreglo', True), key=f"arr_{p_id}")
                if p['pd'] != "Ninguno":
                    st.markdown("**Dorso: Impresión y Acabado**")
                    p['im_d'] = st.selectbox("Sistema Dorso", ["Offset", "Digital", "No"], ["Offset", "Digital", "No"].index(p.get('im_d','No')), key=f"imd_{p_id}")
                    if p['im_d'] == "Offset":
                        p['nt_d'] = st.number_input("Tintas D.", 1, 6, max(1, int(p.get('nt_d',1))), key=f"ntd_{p_id}")
                        p['ba_d'] = st.checkbox("Barniz D.", p.get('ba_d',False), key=f"bad_{p_id}")
                    elif p['im_d'] == "Digital":
                        p['ld_d'] = st.checkbox("Laminado Digital D.", p.get('ld_d',False), key=f"ldd_{p_id}")
                    p['pel_d'] = st.selectbox("Peliculado Dorso", list(PRECIOS["peliculado"].keys()), list(PRECIOS["peliculado"].keys()).index(p.get('pel_d','Sin Peliculado')), key=f"peld_{p_id}")

                if st.button("🗑 Eliminar", key=f"del_{p_id}"): del st.session_state.piezas_dict[p_id]; st.rerun()

    # --- SECCIÓN DE EXTRAS ---
    st.divider()
    st.subheader("📦 Almacén de Accesorios y Extras")
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        ex_sel = st.selectbox("Añadir de la lista:", ["---"] + list(PRECIOS["extras_base"].keys()))
        q_sel = st.number_input("Uds/mueble:", 1.0, 100.0, 1.0, key="q_base_extra")
        if st.button("➕ Añadir Accesorio") and ex_sel != "---":
            st.session_state.lista_extras_grabados.append({"nombre": ex_sel, "coste": PRECIOS["extras_base"][ex_sel], "cantidad": q_sel})
            st.rerun()
    with col_e2:
        en = st.text_input("Nombre Extra Manual:", key="ex_man_n")
        ec = st.number_input("Coste Unitario (€):", 0.0, 100.0, 0.0, key="ex_man_c")
        eq = st.number_input("Cant/mueble manual:", 1.0, 100.0, 1.0, key="ex_man_q")
        if st.button("➕ Añadir Manual") and en:
            st.session_state.lista_extras_grabados.append({"nombre": en, "coste": ec, "cantidad": eq})
            st.rerun()

    if st.session_state.lista_extras_grabados:
        st.markdown("### 📋 Listado de Extras Añadidos:")
        for i, ex in enumerate(st.session_state.lista_extras_grabados):
            ca, cb, cc, cd = st.columns([3, 2, 2, 1])
            ca.write(f"**{ex['nombre']}**"); cb.write(f"{ex['coste']}€/ud"); cc.write(f"x{ex['cantidad']} uds")
            if cd.button("🗑", key=f"del_gr_{i}"): st.session_state.lista_extras_grabados.pop(i); st.rerun()

# --- 5. MOTOR DE CÁLCULO ---
res_final, desc_full = [], {}
if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
    for q_n in lista_cants:
        tiene_dig = any(pz["im"] == "Digital" or pz.get("im_d") == "Digital" for pz in st.session_state.piezas_dict.values())
        mn_m, _ = calcular_mermas(q_n, es_digital=tiene_dig)
        qp_taller = q_n + mn_m
        coste_f, det_f = 0.0, []
        
        for p_id, p in st.session_state.piezas_dict.items():
            nb = q_n * p["pliegos"]
            mn, mi = calcular_mermas(nb, es_digital=(p["im"]=="Digital" or p.get("im_d")=="Digital"))
            hc, hp = nb+mn+mi, nb+mn
            m2 = (p["w"]*p["h"])/1_000_000
            
            c_cart_f = (hc*m2*(p.get('gf',0)/1000)*PRECIOS["cartoncillo"][p["pf"]]["precio_kg"])
            c_cart_d = (hc*m2*(p.get('gd',0)/1000)*PRECIOS["cartoncillo"][p["pd"]]["precio_kg"])
            c_pla, c_con = 0.0, 0.0
            if p["pl"] != "Ninguna":
                c_pla = hp * m2 * PRECIOS["planchas"][p["pl"]][p["ap"]]
                pas = (1 if p["pf"]!="Ninguno" else 0) + (1 if p["pd"]!="Ninguno" else 0)
                c_con = hp * m2 * PRECIOS["planchas"][p["pl"]]["peg"] * pas
            
            def f_o(n): return 60 if n < 100 else (120 if n > 500 else 60 + 0.15*(n-100))
            c_imp_f = (nb*m2*6.5 if p["im"]=="Digital" else (f_o(nb)*(p.get('nt',1)+(1 if p.get('ba') else 0)) if p["im"]=="Offset" else 0))
            c_imp_d = (nb*m2*6.5 if p.get("im_d")=="Digital" else (f_o(nb)*(p.get('nt_d',0)+(1 if p.get('ba_d') else 0)) if p.get("im_d")=="Offset" else 0))
            c_acab_f = (hp*m2*PRECIOS["peliculado"][p["pel"]]) + (hp*m2*3.5 if p.get("ld") else 0)
            c_acab_d = (hp*m2*PRECIOS["peliculado"][p.get("pel_d", "Sin Peliculado")]) + (hp*m2*3.5 if p.get("ld_d") else 0)
            
            c_arr = 0.0
            if p["cor"] == "Troquelado":
                if p.get('cobrar_arreglo', True):
                    c_arr = 107.7 if (p['h']>1000 or p['w']>700) else 48.19
                c_tir = (hp*(0.135 if (p['h']>1000 or p['w']>700) else 0.09))
            else: c_tir = hp * 1.5 
            
            sub = c_cart_f + c_cart_d + c_pla + c_con + c_imp_f + c_imp_d + c_acab_f + c_acab_d + c_arr + c_tir
            coste_f += sub
            det_f.append({"Pieza": p["nombre"], "Mat.F": c_cart_f, "Mat.D": c_cart_d, "Plan": c_pla, "Pegado": c_con, "Imp.F": c_imp_f, "Imp.D": c_imp_d, "Acab.F": c_acab_f, "Acab.D": c_acab_d, "Arr": c_arr, "Tir": c_tir, "Sub": sub})

        c_ext_total = sum(e["coste"] * e["cantidad"] * qp_taller for e in st.session_state.lista_extras_grabados)
        c_man_obra = ((seg_man_total/3600)*18*qp_taller) + (qp_taller*dif_ud)
        t_fab = coste_f + c_man_obra + c_ext_total
        desc_full[q_n] = {"det": det_f, "man": c_man_obra, "extras": c_ext_total, "total": t_fab, "qp": qp_taller}
        res_final.append({"Cant": q_n, "Total": f"{(t_fab*margen):.2f}€", "Ud": f"{(t_fab*margen/q_n):.2f}€"})

# --- 6. SALIDA VISUAL ---
if modo_comercial and res_final:
    p_lines = []
    for p in st.session_state.piezas_dict.values():
        line = f"<li><b>{p['nombre']}:</b> {p['w']}x{p['h']} mm<br/>"
        ac_c = []
        if p.get('pel') and p['pel'] != "Sin Peliculado": ac_c.append(p['pel'])
        if p['im'] == "Offset" and p.get('ba'): ac_c.append("Barniz")
        if p['im'] == "Digital" and p.get('ld'): ac_c.append("Laminado Digital")
        line += f"&nbsp;&nbsp;&nbsp;• Cara: {p['pf']} ({p['gf']}g) | Imp: {p['im']} | Acabado: {' + '.join(ac_c) if ac_c else 'Sin acabado'}<br/>"
        if p.get('pl') and p['pl'] != "Ninguna": line += f"&nbsp;&nbsp;&nbsp;• Soporte Base: {p['pl']} - Calidad {p['ap']}<br/>"
        if p.get('pd') and p['pd'] != "Ninguno":
            ac_d = []
            if p.get('pel_d') and p['pel_d'] != "Sin Peliculado": ac_d.append(p['pel_d'])
            if p.get('im_d') == "Offset" and p.get('ba_d'): ac_d.append("Barniz")
            if p.get('im_d') == "Digital" and p.get('ld_d'): ac_d.append("Laminado Digital")
            line += f"&nbsp;&nbsp;&nbsp;• Dorso: {p['pd']} ({p['gd']}g) | Imp: {p['im_d']} | Acabado: {' + '.join(ac_d) if ac_d else 'Sin acabado'}"
        line += "</li>"
        p_lines.append(line)
    
    ex_h = "".join([f"<li>{e['nombre']} (x{e['cantidad']})</li>" for e in st.session_state.lista_extras_grabados])
    f_h = "".join([f"<tr><td>{r['Cant']} uds</td><td>{r['Total']}</td><td><b>{r['Ud']}</b></td></tr>" for r in res_final])
    
    st.markdown(f"""<div class="comercial-box">
        <h2 class="comercial-header">OFERTA COMERCIAL - {num_proy}</h2>
        <p style="text-align:center;"><b>Cliente:</b> {cliente}</p>
        <h4>1. Especificaciones</h4><ul>{"".join(p_lines)}</ul>
        <h4>2. Accesorios y Montaje</h4><ul>{ex_h}<li>Manipulado especializado incluido ({tiempo_input} {unidad_tiempo.lower()}/ud).</li></ul>
        <table class="comercial-table"><tr><th>Cantidad</th><th>PVP Total</th><th>PVP Unitario</th></tr>{f_h}</table>
    </div>""", unsafe_allow_html=True)
else:
    if res_final:
        st.header(f"📊 Proyecto: {num_proy} - {cliente}")
        st.dataframe(pd.DataFrame(res_final), use_container_width=True)
        for q, info in desc_full.items():
            with st.expander(f"🔍 Desglose Compras {q} uds"):
                st.table(pd.DataFrame(info["det"]).style.format("{:.2f}€", subset=pd.DataFrame(info["det"]).columns[1:]))
                st.write(f"**Mano Obra:** {info['man']:.2f}€ | **Extras:** {info['extras']:.2f}€")
