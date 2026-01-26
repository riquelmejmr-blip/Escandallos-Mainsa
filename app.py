import streamlit as st
import pandas as pd
import json

# --- 1. CONFIGURACIÓN DE PRECIOS ---
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

# --- 2. INICIALIZACIÓN ---
st.set_page_config(page_title="MAINSA PLV PRO", layout="wide")

def crear_forma_vacia(index):
    return {
        "nombre": f"Forma {index + 1}", "pliegos": 1.0, "w": 0, "h": 0, 
        "pf": "Ninguno", "gf": 0, "pl": "Ninguna", "ap": "C/C", 
        "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, 
        "im_d": "No", "nt_d": 0, "ba_d": False, "pel": "Sin Peliculado", 
        "pel_d": "Sin Peliculado", "ld": False, "ld_d": False, 
        "cor": "Troquelado", "cobrar_arreglo": True
    }

# Inicialización de variables para evitar NameError
if 'piezas_dict' not in st.session_state: st.session_state.piezas_dict = {0: crear_forma_vacia(0)}
if 'lista_extras_grabados' not in st.session_state: st.session_state.lista_extras_grabados = []
if 'brf' not in st.session_state: st.session_state.brf = ""
if 'com' not in st.session_state: st.session_state.com = ""
if 'ver' not in st.session_state: st.session_state.ver = "1.0"
if 'cli' not in st.session_state: st.session_state.cli = ""
if 'des' not in st.session_state: st.session_state.des = ""
if 'cants_input' not in st.session_state: st.session_state.cants_input = "0"
if 'tiempo_val' not in st.session_state: st.session_state.tiempo_val = 0
if 'unidad_t' not in st.session_state: st.session_state.unidad_t = "Seg"

st.markdown("""<style>
    .comercial-box { background-color: white; padding: 30px; border: 2px solid #1E88E5; border-radius: 10px; color: #333; font-family: sans-serif; }
    .comercial-header { color: #1E88E5; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .comercial-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.9em; }
    .comercial-table th { background-color: #1E88E5; color: white; padding: 10px; }
    .comercial-table td { padding: 10px; border: 1px solid #ddd; text-align: center; }
    .config-block { background-color: #f1f3f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1E88E5; margin-bottom: 25px; }
    .header-info { display: flex; justify-content: space-around; background: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 20px; color: #333; }
</style>""", unsafe_allow_html=True)

st.title("📦 Escandallos Profesionales MAINSA PLV")

# --- 3. PANEL LATERAL (GESTIÓN) ---
with st.sidebar:
    st.header("🌟 Control")
    modo_comercial = st.checkbox("VISTA OFERTA COMERCIAL", value=False)
    
    st.divider()
    st.header("📂 Gestión de Archivo")
    
    nombre_archivo = f"{st.session_state.brf} {st.session_state.com} {st.session_state.ver}".strip() + ".json"
    
    datos_exportar = {
        "brf": st.session_state.brf, "cli": st.session_state.cli, "com": st.session_state.com, 
        "ver": st.session_state.ver, "des": st.session_state.des,
        "piezas_dict": st.session_state.piezas_dict, "lista_extras": st.session_state.lista_extras_grabados,
        "cants": st.session_state.cants_input, "tiempo": st.session_state.tiempo_val, "un": st.session_state.unidad_t
    }
    st.download_button("💾 Guardar Proyecto", json.dumps(datos_exportar, indent=4), file_name=nombre_archivo)

    archivo_subido = st.file_uploader("📂 Importar archivo (.json)", type=["json"])
    if archivo_subido:
        di = json.load(archivo_subido)
        st.session_state.brf = di.get("brf", ""); st.session_state.cli = di.get("cli", "")
        st.session_state.com = di.get("com", ""); st.session_state.ver = di.get("ver", "1.0")
        st.session_state.des = di.get("des", ""); st.session_state.lista_extras_grabados = di.get("lista_extras", [])
        st.session_state.piezas_dict = {int(k): v for k, v in di["piezas_dict"].items()}
        st.session_state.cants_input = di.get("cants", "0")
        st.session_state.tiempo_val = di.get("tiempo", 0)
        st.session_state.unidad_t = di.get("un", "Seg")
        st.rerun()

# --- 4. CONFIGURACIÓN SUPERIOR ---
if not modo_comercial:
    st.markdown('<div class="config-block">', unsafe_allow_html=True)
    c_i1, c_i2, c_i3, c_i4 = st.columns(4)
    st.session_state.brf = c_i1.text_input("Nº de Briefing", st.session_state.brf)
    st.session_state.cli = c_i2.text_input("Cliente", st.session_state.cli)
    st.session_state.com = c_i3.text_input("Nº de Comercial", st.session_state.com)
    st.session_state.ver = c_i4.text_input("Versión", st.session_state.ver)
    st.session_state.des = st.text_area("Descripción", st.session_state.des, height=68)
    
    st.divider()
    c_c1, c_c2, c_c3, c_c4, c_c5 = st.columns([2, 1, 2, 2, 2])
    st.session_state.cants_input = c_c1.text_input("Cantidades (ej: 100, 500)", st.session_state.cants_input)
    st.session_state.unidad_t = c_c2.radio("Unidad:", ["Seg", "Min"], index=0 if st.session_state.unidad_t=="Seg" else 1)
    st.session_state.tiempo_val = c_c3.number_input("Manipulado", value=st.session_state.tiempo_val)
    dif_ud = c_c4.selectbox("Dificultad", [0.02, 0.061, 0.091], index=2)
    margen = c_c5.number_input("Multiplicador", value=2.2, step=0.1)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Respaldo para cálculos en vista comercial
    dif_ud = 0.091
    margen = 2.2

# Procesamiento de cantidades y tiempo
lista_cants = [int(x.strip()) for x in st.session_state.cants_input.split(",") if x.strip().isdigit()]
seg_man_total = st.session_state.tiempo_val * 60 if st.session_state.unidad_t == "Min" else st.session_state.tiempo_val

# --- 5. EDICIÓN DE FORMAS Y EXTRAS ---
if not modo_comercial:
    cb1, cb2 = st.columns([1, 5])
    if cb1.button("➕ Forma"):
        nid = max(st.session_state.piezas_dict.keys()) + 1
        st.session_state.piezas_dict[nid] = crear_forma_vacia(nid); st.rerun()
    if cb2.button("🗑 Reiniciar"):
        st.session_state.piezas_dict = {0: crear_forma_vacia(0)}; st.session_state.lista_extras_grabados = []; st.rerun()

    for p_id, p in st.session_state.piezas_dict.items():
        with st.expander(f"🛠 {p['nombre']}", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                p['nombre'] = st.text_input("Etiqueta", p['nombre'], key=f"n_{p_id}")
                p['pliegos'] = st.number_input("Pliegos/Ud", 0.0, 100.0, float(p['pliegos']), key=f"p_{p_id}")
                p['w'], p['h'] = st.number_input("Ancho mm", 0, 5000, int(p['w']), key=f"w_{p_id}"), st.number_input("Largo mm", 0, 5000, int(p['h']), key=f"h_{p_id}")
                p['im'] = st.selectbox("Sistema Cara", ["Offset", "Digital", "No"], ["Offset", "Digital", "No"].index(p['im']), key=f"im_{p_id}")
                if p['im'] == "Offset":
                    p['nt'] = st.number_input("Tintas F.", 0, 6, max(0, int(p.get('nt',4))), key=f"nt_{p_id}") # Fix min a 0
                p['pel'] = st.selectbox("Peliculado", list(PRECIOS["peliculado"].keys()), key=f"pel_{p_id}")
            with c2:
                p['pf'] = st.selectbox("C. Frontal", list(PRECIOS["cartoncillo"].keys()), list(PRECIOS["cartoncillo"].keys()).index(p['pf']), key=f"pf_{p_id}")
                p['pl'] = st.selectbox("Plancha Base", list(PRECIOS["planchas"].keys()), list(PRECIOS["planchas"].keys()).index(p['pl']), key=f"pl_{p_id}")
                p['ap'] = st.selectbox("Calidad", ["C/C", "B/C", "B/B"], key=f"ap_{p_id}")
                p['pd'] = st.selectbox("C. Dorso", list(PRECIOS["cartoncillo"].keys()), list(PRECIOS["cartoncillo"].keys()).index(p['pd']), key=f"pd_{p_id}")
            with c3:
                p['cor'] = st.selectbox("Corte", ["Troquelado", "Plotter"], key=f"cor_{p_id}")
                if p['cor'] == "Troquelado": p['cobrar_arreglo'] = st.checkbox("¿Arreglo?", value=p.get('cobrar_arreglo', True), key=f"arr_{p_id}")
                if p['pd'] != "Ninguno":
                    p['im_d'] = st.selectbox("Imp. Dorso", ["Offset", "Digital", "No"], key=f"imd_{p_id}")
                    if p['im_d'] == "Offset": p['nt_d'] = st.number_input("Tintas D.", 0, 6, max(0, int(p.get('nt_d',0))), key=f"ntd_{p_id}")
                if st.button("🗑 Borrar", key=f"del_{p_id}"): del st.session_state.piezas_dict[p_id]; st.rerun()

    # Extras
    st.divider(); st.subheader("📦 Almacén de Accesorios")
    cex1, cex2 = st.columns(2)
    with cex1:
        ex_s = st.selectbox("De la lista:", ["---"] + list(PRECIOS["extras_base"].keys()))
        if st.button("➕ Añadir"):
            if ex_s != "---": st.session_state.lista_extras_grabados.append({"nombre": ex_s, "coste": PRECIOS["extras_base"][ex_s], "cantidad": 1.0}); st.rerun()
    with cex2:
        en = st.text_input("Manual:")
        if st.button("➕ Manual") and en: st.session_state.lista_extras_grabados.append({"nombre": en, "coste": 0.0, "cantidad": 1.0}); st.rerun()
    
    for i, ex in enumerate(st.session_state.lista_extras_grabados):
        ca, cb, cc, cd = st.columns([3, 2, 2, 1])
        ca.write(f"**{ex['nombre']}**"); ex['coste'] = cb.number_input("€", value=float(ex['coste']), key=f"exc_{i}"); ex['cantidad'] = cc.number_input("Cant", value=float(ex['cantidad']), key=f"exq_{i}")
        if cd.button("🗑", key=f"exd_{i}"): st.session_state.lista_extras_grabados.pop(i); st.rerun()

# --- 6. MOTOR DE CÁLCULO ---
res_final, desc_full = [], {}
if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
    for q_n in lista_cants:
        tiene_dig = any(pz["im"] == "Digital" or pz.get("im_d") == "Digital" for pz in st.session_state.piezas_dict.values())
        mn_m, _ = calcular_mermas(q_n, es_digital=tiene_dig)
        qp_taller = q_n + mn_m
        coste_f, det_f = 0.0, []
        for p_id, p in st.session_state.piezas_dict.items():
            nb = q_n * p["pliegos"]; mn, mi = calcular_mermas(nb, (p["im"]=="Digital" or p.get("im_d")=="Digital"))
            hc, hp = nb+mn+mi, nb+mn; m2 = (p["w"]*p["h"])/1_000_000
            c_cf = (hc*m2*(p.get('gf',0)/1000)*PRECIOS["cartoncillo"][p["pf"]]["precio_kg"])
            c_cd = (hc*m2*(p.get('gd',0)/1000)*PRECIOS["cartoncillo"][p["pd"]]["precio_kg"])
            c_pla, c_peg = 0.0, 0.0
            if p["pl"] != "Ninguna":
                c_pla = hp * m2 * PRECIOS["planchas"][p["pl"]][p["ap"]]
                pas = (1 if p["pf"]!="Ninguno" else 0) + (1 if p["pd"]!="Ninguno" else 0)
                c_peg = hp * m2 * PRECIOS["planchas"][p["pl"]]["peg"] * pas
            def f_o(n): return 60 if n < 100 else (120 if n > 500 else 60 + 0.15*(n-100))
            c_if = (nb*m2*6.5 if p["im"]=="Digital" else (f_o(nb)*(p.get('nt',0)+(1 if p.get('ba') else 0)) if p["im"]=="Offset" else 0))
            c_id = (nb*m2*6.5 if p.get("im_d")=="Digital" else (f_o(nb)*(p.get('nt_d',0)+(1 if p.get('ba_d') else 0)) if p.get("im_d")=="Offset" else 0))
            c_af = (hp*m2*PRECIOS["peliculado"][p["pel"]]) + (hp*m2*3.5 if p.get("ld") else 0)
            c_ad = (hp*m2*PRECIOS["peliculado"].get(p.get("pel_d", "Sin Peliculado"), 0)) + (hp*m2*3.5 if p.get("ld_d") else 0)
            c_arr = (107.7 if (p['h']>1000 or p['w']>700) else 48.19) if (p["cor"]=="Troquelado" and p.get('cobrar_arreglo', True)) else 0
            c_tir = (hp*(0.135 if (p['h']>1000 or p['w']>700) else 0.09)) if p["cor"]=="Troquelado" else hp*1.5
            sub = c_cf + c_cd + c_pla + c_peg + c_if + c_id + c_af + c_ad + c_arr + c_tir
            coste_f += sub
            det_f.append({"Pieza": p["nombre"], "C.F": c_cf, "C.D": c_cd, "Plancha": c_pla, "Peg": c_peg, "Imp": c_if+c_id, "Acab": c_af+c_ad, "Arr": c_arr, "Tir": c_tir, "Sub": sub})
        c_ext_tot = sum(e["coste"] * e["cantidad"] * qp_taller for e in st.session_state.lista_extras_grabados)
        c_mo = ((seg_man_total/3600)*18*qp_taller) + (qp_taller*dif_ud)
        t_fab = coste_f + c_mo + c_ext_tot
        desc_full[q_n] = {"det": det_f, "man": c_mo, "extras": c_ext_tot, "total": t_fab, "qp": qp_taller}
        res_final.append({"Cant": q_n, "Total": f"{(t_fab*margen):.2f}€", "Ud": f"{(t_fab*margen/q_n):.2f}€"})

# --- 7. SALIDA VISUAL ---
if modo_comercial:
    p_html = ""
    for p in st.session_state.piezas_dict.values():
        ac_c = f"{p['pel']} + Laminado" if p.get('ld') else p['pel']
        p_html += f"<li><b>{p['nombre']}:</b> {p['w']}x{p['h']} mm<br/>"
        p_html += f"&nbsp;&nbsp;&nbsp;• Cara: {p['pf']} ({p.get('gf',0)}g) | Imp: {p['im']} | Acabado: {ac_c}<br/>"
        if p.get('pl') != "Ninguna": p_html += f"&nbsp;&nbsp;&nbsp;• Soporte Base: {p['pl']} - Calidad {p['ap']}<br/>"
        if p.get('pd') != "Ninguno": p_html += f"&nbsp;&nbsp;&nbsp;• Dorso: {p['pd']} ({p.get('gd',0)}g) | Imp: {p.get('im_d','No')}</li>"
    
    ex_html = "".join([f"<li>{e['nombre']} (x{e['cantidad']})</li>" for e in st.session_state.lista_extras_grabados])
    f_html = "".join([f"<tr><td>{r['Cant']} uds</td><td>{r['Total']}</td><td><b>{r['Ud']}</b></td></tr>" for r in res_final])
    
    # Inyección directa de HTML limpio
    st.markdown(f"""
    <div class="comercial-box">
        <h2 class="comercial-header">OFERTA COMERCIAL - BRIEFING {st.session_state.brf}</h2>
        <div class="header-info">
            <span><b>Cliente:</b> {st.session_state.cli}</span>
            <span><b>Comercial:</b> {st.session_state.com}</span>
            <span><b>Versión:</b> {st.session_state.ver}</span>
        </div>
        <p><b>Descripción:</b> {st.session_state.des}</p>
        <h4>1. Especificaciones</h4><ul>{p_html}</ul>
        <h4>2. Accesorios y Montaje</h4><ul>{ex_html}<li>Manipulado y montaje especializado incluido.</li></ul>
        <table class="comercial-table">
            <tr><th>Cantidad</th><th>PVP Total</th><th>PVP Unitario</th></tr>
            {f_html}
        </table>
    </div>
    """, unsafe_allow_html=True)
else:
    if res_final:
        st.header(f"📊 Briefing: {st.session_state.brf}")
        st.dataframe(pd.DataFrame(res_final), use_container_width=True)
        for q, info in desc_full.items():
            with st.expander(f"🔍 Auditoría Compras {q} uds"):
                st.table(pd.DataFrame(info["det"]).style.format("{:.2f}€", subset=["C.F","C.D","Plancha","Peg","Imp","Acab","Arr","Tir","Sub"]))
                st.write(f"**Mano Obra:** {info['man']:.2f}€ | **Extras:** {info['extras']:.2f}€")
