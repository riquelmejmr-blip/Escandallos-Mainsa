import streamlit as st
import pandas as pd
import json

# --- 1. CONSTANTES FIJAS (OCULTAS) ---
MARGEN_FIJO = 2.2         #
DIFICULTAD_FIJA = 0.091   #
IMPORTE_FIJO_VENTAS = 500 #

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
st.set_page_config(page_title="ESCANDALLO MAINSA (VENTAS)", layout="wide")

def crear_forma_vacia(index):
    return {
        "nombre": f"Forma {index + 1}", "pliegos": 1.0, "w": 0, "h": 0, 
        "pf": "Ninguno", "gf": 0, "pl": "Ninguna", "ap": "C/C", 
        "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, 
        "im_d": "No", "nt_d": 0, "ba_d": False, "pel": "Sin Peliculado", 
        "pel_d": "Sin Peliculado", "ld": False, "ld_d": False, 
        "cor": "Troquelado", "cobrar_arreglo": True
    }

if 'piezas_dict' not in st.session_state: st.session_state.piezas_dict = {0: crear_forma_vacia(0)}
if 'lista_extras_grabados' not in st.session_state: st.session_state.lista_extras_grabados = []
if 'brf' not in st.session_state: st.session_state.brf = ""
if 'com' not in st.session_state: st.session_state.com = ""
if 'ver' not in st.session_state: st.session_state.ver = "1.0"
if 'cli' not in st.session_state: st.session_state.cli = ""
if 'des' not in st.session_state: st.session_state.des = ""

st.markdown("""<style>
    .comercial-box { background-color: white; padding: 30px; border: 2px solid #1E88E5; border-radius: 10px; color: #333; font-family: sans-serif; }
    .comercial-header { color: #1E88E5; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .comercial-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.9em; }
    .comercial-table th { background-color: #1E88E5; color: white; padding: 10px; }
    .comercial-table td { padding: 10px; border: 1px solid #ddd; text-align: center; }
</style>""", unsafe_allow_html=True)

st.title("ESCANDALLO MAINSA (VENTAS)")

# --- 3. PANEL LATERAL (VENTAS) ---
with st.sidebar:
    st.header("📋 Datos Proyecto")
    st.session_state.brf = st.text_input("Nº de Briefing", st.session_state.brf)
    st.session_state.cli = st.text_input("Cliente", st.session_state.cli)
    st.session_state.com = st.text_input("Comercial", st.session_state.com)
    st.session_state.ver = st.text_input("Versión", st.session_state.ver)
    st.session_state.des = st.text_area("Descripción")
    st.divider()
    cants_str = st.text_input("Cantidades", "0")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    unidad_t = st.radio("Manipulación:", ["Segundos", "Minutos"], horizontal=True)
    t_input = st.number_input(f"Tiempo ({unidad_t})", value=0)
    seg_man_total = t_input * 60 if unidad_t == "Minutos" else t_input
    st.divider()
    modo_comercial = st.checkbox("🌟 VISTA OFERTA COMERCIAL", value=False)
    st.divider()
    st.header("📂 Gestión")
    partes_n = [st.session_state.brf, st.session_state.com, st.session_state.ver]
    archivo_n = " ".join([str(p).strip() for p in partes_n if str(p).strip()]) + ".json"
    datos_e = {"brf": st.session_state.brf, "cli": st.session_state.cli, "com": st.session_state.com, "ver": st.session_state.ver, "des": st.session_state.des, "piezas": st.session_state.piezas_dict, "extras": st.session_state.lista_extras_grabados}
    st.download_button("💾 Guardar", json.dumps(datos_e, indent=4), file_name=archivo_n)
    subida = st.file_uploader("📂 Abrir JSON", type=["json"])
    if subida:
        di = json.load(subida)
        st.session_state.piezas_dict = {int(k): v for k, v in di["piezas"].items()}
        st.session_state.lista_extras_grabados = di.get("extras", [])
        st.rerun()

# --- 4. GESTIÓN DE FORMAS Y EXTRAS ---
if not modo_comercial:
    c1, c2 = st.columns([1, 5])
    if c1.button("➕ Forma"):
        nid = max(st.session_state.piezas_dict.keys()) + 1
        st.session_state.piezas_dict[nid] = crear_forma_vacia(nid); st.rerun()
    if c2.button("🗑 Reiniciar"):
        st.session_state.piezas_dict = {0: crear_forma_vacia(0)}; st.session_state.lista_extras_grabados = []; st.rerun()

    for p_id, p in st.session_state.piezas_dict.items():
        with st.expander(f"🛠 {p['nombre']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                p['nombre'] = st.text_input("Etiqueta", p['nombre'], key=f"n_{p_id}")
                p['pliegos'] = st.number_input("Pliegos/Ud", 0.0, 100.0, float(p['pliegos']), key=f"p_{p_id}")
                p['w'], p['h'] = st.number_input("Ancho mm", 0, 5000, int(p['w']), key=f"w_{p_id}"), st.number_input("Largo mm", 0, 5000, int(p['h']), key=f"h_{p_id}")
                p['im'] = st.selectbox("Sistema Cara", ["Offset", "Digital", "No"], ["Offset", "Digital", "No"].index(p['im']), key=f"im_{p_id}")
                if p['im'] == "Offset":
                    p['nt'] = st.number_input("Tintas F.", 0, 6, max(0, int(p.get('nt',4))), key=f"nt_{p_id}")
                    p['ba'] = st.checkbox("Barniz F.", p.get('ba',False), key=f"ba_{p_id}")
                elif p['im'] == "Digital": p['ld'] = st.checkbox("Laminado Digital F.", p.get('ld',False), key=f"ld_{p_id}")
                p['pel'] = st.selectbox("Peliculado Cara", list(PRECIOS["peliculado"].keys()), index=list(PRECIOS["peliculado"].keys()).index(p.get('pel', 'Sin Peliculado')), key=f"pel_{p_id}")
            with col2:
                pf_prev = p['pf']; p['pf'] = st.selectbox("C. Frontal", list(PRECIOS["cartoncillo"].keys()), index=list(PRECIOS["cartoncillo"].keys()).index(p['pf']), key=f"pf_{p_id}")
                if p['pf'] != pf_prev: p['gf'] = PRECIOS["cartoncillo"][p['pf']]["gramaje"]
                if p['pf'] != "Ninguno": p['gf'] = st.number_input("Gramaje F.", value=int(p['gf']), key=f"gf_{p_id}")
                p['pl'] = st.selectbox("Plancha Base", list(PRECIOS["planchas"].keys()), index=list(PRECIOS["planchas"].keys()).index(p['pl']), key=f"pl_{p_id}")
                p['ap'] = st.selectbox("Calidad", ["C/C", "B/C", "B/B"], index=["C/C", "B/C", "B/B"].index(p.get('ap', 'C/C')), key=f"ap_{p_id}")
                p['pd'] = st.selectbox("C. Dorso", list(PRECIOS["cartoncillo"].keys()), index=list(PRECIOS["cartoncillo"].keys()).index(p.get('pd', 'Ninguno')), key=f"pd_{p_id}")
            with col3:
                p['cor'] = st.selectbox("Corte", ["Troquelado", "Plotter"], index=["Troquelado", "Plotter"].index(p.get('cor', 'Troquelado')), key=f"cor_{p_id}")
                if p['cor'] == "Troquelado": p['cobrar_arreglo'] = st.checkbox("¿Cobrar Arreglo?", value=p.get('cobrar_arreglo', True), key=f"arr_{p_id}")
                if p['pd'] != "Ninguno":
                    p['im_d'] = st.selectbox("Sistema Dorso", ["Offset", "Digital", "No"], index=["Offset", "Digital", "No"].index(p.get('im_d', 'No')), key=f"imd_{p_id}")
                    if p['im_d'] == "Offset":
                        p['nt_d'] = st.number_input("Tintas D.", 0, 6, max(0, int(p.get('nt_d',0))), key=f"ntd_{p_id}")
                        p['ba_d'] = st.checkbox("Barniz D.", p.get('ba_d',False), key=f"bad_{p_id}")
                    elif p['im_d'] == "Digital": p['ld_d'] = st.checkbox("Laminado Digital D.", p.get('ld_d',False), key=f"ldd_{p_id}")
                    p['pel_d'] = st.selectbox("Peliculado Dorso", list(PRECIOS["peliculado"].keys()), index=list(PRECIOS["peliculado"].keys()).index(p.get('pel_d', 'Sin Peliculado')), key=f"peld_{p_id}")
                if st.button("🗑 Borrar", key=f"del_{p_id}"): del st.session_state.piezas_dict[p_id]; st.rerun()

    st.divider(); st.subheader("📦 Accesorios")
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        ex_sel = st.selectbox("Añadir accesorio:", ["---"] + list(PRECIOS["extras_base"].keys()))
        if st.button("➕ Añadir") and ex_sel != "---":
            st.session_state.lista_extras_grabados.append({"nombre": ex_sel, "coste": PRECIOS["extras_base"][ex_sel], "cantidad": 1.0}); st.rerun()
    with col_e2:
        en = st.text_input("Manual:"); ec = st.number_input("Coste:", 0.0, 50.0)
        if st.button("➕ Añadir Manual") and en:
            st.session_state.lista_extras_grabados.append({"nombre": en, "coste": ec, "cantidad": 1.0}); st.rerun()
    for i, ex in enumerate(st.session_state.lista_extras_grabados):
        ca, cb, cc, cd = st.columns([4, 2, 2, 1])
        ca.write(f"**{ex['nombre']}**"); ex['cantidad'] = cc.number_input("Cant", value=float(ex['cantidad']), key=f"exq_{i}")
        if cd.button("🗑", key=f"exd_{i}"): st.session_state.lista_extras_grabados.pop(i); st.rerun()

# --- 5. MOTOR DE CÁLCULO ---
res_final = []
if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
    for q_n in lista_cants:
        tiene_dig = any(pz["im"] == "Digital" or pz.get("im_d") == "Digital" for pz in st.session_state.piezas_dict.values())
        mn_m, _ = calcular_mermas(q_n, es_digital=tiene_dig)
        qp_taller = q_n + mn_m
        coste_f = 0.0
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
            coste_f += (c_cf + c_cd + c_pla + c_peg + c_if + c_id + c_af + c_ad + c_arr + c_tir)
        
        c_ext_tot = sum(e["coste"] * e["cantidad"] * qp_taller for e in st.session_state.lista_extras_grabados)
        c_mo = ((seg_man_total/3600)*18*qp_taller) + (qp_taller * DIFICULTAD_FIJA)
        # Importe fijo bloqueado en 500€ para Ventas
        t_fab = coste_f + c_mo + c_ext_tot + IMPORTE_FIJO_VENTAS
        res_final.append({"Cant": q_n, "Total": f"{(t_fab * MARGEN_FIJO):.2f}€", "Ud": f"{(t_fab * MARGEN_FIJO / q_n):.2f}€"})

# --- 6. SALIDA VISUAL (OFERTA COMERCIAL) ---
if modo_comercial and res_final:
    p_html = ""
    for p in st.session_state.piezas_dict.values():
        ac_c_list = [p['pel'] if p.get('pel')!="Sin Peliculado" else None, "Laminado Digital" if p.get('ld') else None, "Barniz" if p.get('ba') else None]
        ac_c_final = " + ".join([x for x in ac_c_list if x]) or "Sin acabado"
        p_html += f"<li><b>{p['nombre']}:</b> {p['w']}x{p['h']} mm ({p['pliegos']:g} pliegos/ud)<br/>&nbsp;&nbsp;&nbsp;• Cara: {p['pf']} ({p.get('gf',0)}g) | Imp: {p['im']} | Acabado: {ac_c_final}<br/>"
        if p.get('pl') != "Ninguna": p_html += f"&nbsp;&nbsp;&nbsp;• Soporte Base: {p['pl']} - Calidad {p['ap']}<br/>"
        if p.get('pd') != "Ninguno":
            ac_d_list = [p.get('pel_d') if p.get('pel_d')!="Sin Peliculado" else None, "Laminado Digital" if p.get('ld_d') else None, "Barniz" if p.get('ba_d') else None]
            ac_d_final = " + ".join([x for x in ac_d_list if x]) or "Sin acabado"
            p_html += f"&nbsp;&nbsp;&nbsp;• Dorso: {p['pd']} ({p.get('gd',0)}g) | Imp: {p.get('im_d', 'No')} | Acabado: {ac_d_final}</li>"
    ex_h_list = [f"<li>{e['nombre']} (x{e['cantidad']:g})</li>" for e in st.session_state.lista_extras_grabados]
    ex_h = "".join(ex_h_list) if ex_h_list else "<li>Sin accesorios adicionales</li>"
    f_h = "".join([f"<tr><td>{r['Cant']} uds</td><td>{r['Total']}</td><td><b>{r['Ud']}</b></td></tr>" for r in res_final])
    st.markdown(f"""<div class="comercial-box"><h2 class="comercial-header">OFERTA COMERCIAL - {st.session_state.brf}</h2><div class="header-info"><span><b>Cliente:</b> {st.session_state.cli}</span><span><b>Comercial:</b> {st.session_state.com}</span><span><b>Versión:</b> {st.session_state.ver}</span></div><h4>1. Especificaciones</h4><ul>{p_html}</ul><h4>2. Accesorios y Montaje</h4><ul>{ex_h}<li><b>Tiempo de manipulado:</b> {t_input} {unidad_t.lower()} / ud incluido.</li></ul><table class="comercial-table"><tr><th>Cantidad</th><th>PVP Total</th><th>PVP Unitario</th></tr>{f_h}</table></div>""", unsafe_allow_html=True)
else:
    if res_final:
        st.header(f"📊 Precios de Venta: {st.session_state.brf}")
        st.table(pd.DataFrame(res_final))
