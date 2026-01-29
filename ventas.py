import streamlit as st
import pandas as pd
import json
import re

# --- 1. BASE DE DATOS DE PRECIOS (OCULTA AL USUARIO) ---
# Los comerciales no ven esto, pero el programa lo usa para calcular
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

# --- CONFIGURACIÓN INTERNA FIJA (NO MODIFICABLE POR COMERCIALES) ---
MARGEN_GENERAL = 2.2
MARGEN_EMBALAJE = 1.4
IMPORTE_FIJO_OCULTO = 500.0  # Se suma siempre al total

# --- 2. MOTORES TÉCNICOS ---
def calcular_mermas(n, es_digital=False):
    if es_digital: return n * 0.10, 0 
    if n < 100: return 15, 135
    if n < 200: return 30, 150
    if n < 600: return 40, 160
    if n < 1000: return 50, 170
    if n < 2000: return 60, 170
    return 120, 170

# --- 3. INICIALIZACIÓN ---
st.set_page_config(page_title="GENERADOR DE OFERTAS", layout="wide")

def crear_forma_vacia(index):
    return {
        "nombre": f"Forma {index + 1}", "pliegos": 1.0, "w": 0, "h": 0, 
        "pf": "Ninguno", "gf": 0, "pl": "Ninguna", "ap": "C/C", 
        "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, 
        "im_d": "No", "nt_d": 0, "ba_d": False, "pel": "Sin Peliculado", 
        "pel_d": "Sin Peliculado", "ld": False, "ld_d": False, 
        "cor": "Troquelado", "cobrar_arreglo": True, "pv_troquel": 0.0
    }

if 'piezas_dict' not in st.session_state: st.session_state.piezas_dict = {0: crear_forma_vacia(0)}
if 'lista_extras_grabados' not in st.session_state: st.session_state.lista_extras_grabados = []
if 'precios_venta_embalaje' not in st.session_state: st.session_state.precios_venta_embalaje = {}

st.markdown("""<style>
    .comercial-box { background-color: white; padding: 30px; border: 2px solid #1E88E5; border-radius: 10px; color: #333; }
    .comercial-header { color: #1E88E5; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 5px; }
    .comercial-ref { text-align: center; color: #555; font-size: 1.1em; margin-bottom: 25px; font-weight: bold; }
    .comercial-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 1.1em; }
    .comercial-table th { background-color: #1E88E5; color: white; padding: 10px; }
    .comercial-table td { padding: 10px; border: 1px solid #ddd; text-align: center; }
</style>""", unsafe_allow_html=True)

st.title("💼 GENERADOR DE OFERTAS")

# --- 4. PANEL LATERAL (SIMPLIFICADO) ---
with st.sidebar:
    st.header("Datos del Proyecto")
    
    # --- IMPORTACIÓN (Sin leer costes) ---
    with st.expander("📂 Cargar Datos (IA/PDF)", expanded=True):
        tab_paste, tab_up = st.tabs(["📋 Pegar Texto", "📂 Archivo"])
        datos_json = None
        
        with tab_paste:
            texto_json = st.text_area("Pega el JSON del GEM", height=100)
            if st.button("🚀 Cargar"):
                try:
                    if texto_json.strip():
                        clean = re.sub(r'\[cite.*?\]', '', texto_json).replace('', '')
                        datos_json = json.loads(clean)
                except: st.error("Formato no válido")

        with tab_up:
            subida = st.file_uploader("JSON", type=["json"])
            if subida: datos_json = json.load(subida)

        if datos_json:
            try:
                di = datos_json
                if "cli" in di: st.session_state["cli_input"] = str(di["cli"]).strip()
                if "brf" in di: st.session_state["brf_input"] = str(di["brf"]).strip()
                if "cantidades" in di: st.session_state["cants_input"] = ", ".join(map(str, di["cantidades"]))
                if "tiempo_manipulacion" in di: st.session_state["t_input_widget"] = float(di["tiempo_manipulacion"])
                if "unidad_manipulacion" in di:
                     val_u = str(di["unidad_manipulacion"])
                     st.session_state["unidad_t_input"] = "Minutos" if "in" in val_u.lower() else "Segundos"
                if "dificultad" in di: 
                    v = float(di["dificultad"])
                    st.session_state["dif_input"] = v if v in [0.02, 0.061, 0.091] else 0.091

                # Extras (Solo nombres y cantidades, el coste se ignora o se lee base)
                raw_ext = di.get("extras", [])
                clean_ext = []
                for ex in raw_ext:
                    nom = ex.get("nombre", ex.get("nota", "Accesorio"))
                    if isinstance(nom, str): nom = nom.strip()
                    # Buscamos coste base si existe para no pedirlo
                    base_cost = PRECIOS["extras_base"].get(nom, 0.0) 
                    clean_ext.append({"nombre": nom, "coste": base_cost, "cantidad": ex.get("cantidad", 1.0)})
                st.session_state.lista_extras_grabados = clean_ext
                st.session_state.precios_venta_embalaje = {} # Reset embalaje

                # Piezas
                if "piezas" in di:
                    st.session_state.piezas_dict = {int(k): v for k, v in di["piezas"].items()}
                    for pid, p in st.session_state.piezas_dict.items():
                        # Mapeo rápido de widgets
                        mapa = {"nombre":"n_", "pliegos":"p_", "h":"h_", "w":"w_", "im":"im_", "nt":"nt_", 
                                "ba":"ba_", "ld":"ld_", "pel":"pel_", "pf":"pf_", "gf":"gf_", "pl":"pl_", 
                                "ap":"ap_", "pd":"pd_", "gd":"gd_", "cor":"cor_", "cobrar_arreglo":"arr_", 
                                "pv_troquel":"pvt_", "im_d":"imd_", "nt_d":"ntd_", "ba_d":"bad_", "ld_d":"ldd_", "pel_d":"peld_"}
                        for k_json, prefix in mapa.items():
                            val = p.get(k_json)
                            # PV Troquel especial
                            if k_json == "pv_troquel" and "coste_troquel_estimado" in p:
                                try: val = float(str(p["coste_troquel_estimado"]).split("€")[0].strip())
                                except: val = 0.0
                            
                            if val is not None:
                                k_st = f"{prefix}{pid}"
                                if isinstance(val, str): val = val.strip()
                                if prefix in ["p_", "pvt_", "gf_", "gd_"]: val = float(val)
                                if prefix in ["h_", "w_", "nt_", "ntd_"]: val = int(val)
                                st.session_state[k_st] = val
                st.toast("Datos cargados")
                st.rerun()
            except: pass

    # --- INPUTS BÁSICOS ---
    st.session_state.cli = st.text_input("Cliente", key="cli_input")
    st.session_state.brf = st.text_input("Nº Briefing/Ref", key="brf_input")
    st.divider()
    cants_str = st.text_input("Cantidades (ej: 500, 1000)", key="cants_input")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    
    # Tiempo y Dificultad (Necesarios para cálculo, aunque el comercial no sepa el coste hora)
    unidad_t = st.radio("Manipulación:", ["Segundos", "Minutos"], horizontal=True, key="unidad_t_input")
    t_input = st.number_input(f"Tiempo montaje/ud", key="t_input_widget")
    seg_man_total = t_input * 60 if unidad_t == "Minutos" else t_input
    
    # Dificultad simplificada visualmente
    idx_dif = 2
    val_act_dif = st.session_state.get("dif_input", 0.091)
    if val_act_dif in [0.02, 0.061, 0.091]: idx_dif = [0.02, 0.061, 0.091].index(val_act_dif)
    dif_ud = st.selectbox("Nivel Dificultad", [0.02, 0.061, 0.091], 
                          format_func=lambda x: "Baja" if x==0.02 else ("Media" if x==0.061 else "Alta"), 
                          index=idx_dif, key="dif_input")

    # FIJO Y MARGEN OCULTOS (No hay inputs)

# --- 5. DEFINICIÓN DE PRODUCTO ---
st.header("1. Especificaciones del Producto")

# Sección Formas (Igual que Admin pero sin ver precios de coste)
c_btns = st.columns([1, 4])
if c_btns[0].button("➕ Forma"):
    nid = max(st.session_state.piezas_dict.keys()) + 1
    st.session_state.piezas_dict[nid] = crear_forma_vacia(nid); st.rerun()
if c_btns[1].button("🗑 Borrar Todo"):
    st.session_state.piezas_dict = {0: crear_forma_vacia(0)}; st.session_state.lista_extras_grabados=[]; st.session_state.precios_venta_embalaje={}; st.rerun()

for p_id, p in st.session_state.piezas_dict.items():
    with st.expander(f"📄 {p.get('nombre', 'Pieza')} ({p.get('h',0)}x{p.get('w',0)} mm)", expanded=True):
        c1, c2, c3 = st.columns(3)
        # Columna 1
        with c1:
            p['nombre'] = st.text_input("Nombre Pieza", p.get('nombre', ""), key=f"n_{p_id}")
            p['pliegos'] = st.number_input("Pliegos/Ud", 0.0, 100.0, float(p.get('pliegos', 1.0)), key=f"p_{p_id}")
            p['h'] = st.number_input("Largo mm", 0, 5000, int(p.get('h', 0)), key=f"h_{p_id}")
            p['w'] = st.number_input("Ancho mm", 0, 5000, int(p.get('w', 0)), key=f"w_{p_id}")
            
            opts_im = ["Offset", "Digital", "No"]
            p['im'] = st.selectbox("Impresión Cara", opts_im, index=opts_im.index(p.get('im','Offset')), key=f"im_{p_id}")
            if p['im'] == "Offset":
                p['nt'] = st.number_input("Tintas F.", 0, 6, int(p.get('nt',4)), key=f"nt_{p_id}")
                p['ba'] = st.checkbox("Barniz F.", p.get('ba',False), key=f"ba_{p_id}")
            elif p['im'] == "Digital": p['ld'] = st.checkbox("Laminado F.", p.get('ld',False), key=f"ld_{p_id}")
            
            opts_pel = list(PRECIOS["peliculado"].keys())
            p['pel'] = st.selectbox("Peliculado Cara", opts_pel, index=opts_pel.index(p.get('pel','Sin Peliculado')), key=f"pel_{p_id}")

        # Columna 2 (Materiales)
        with c2:
            opts_pf = list(PRECIOS["cartoncillo"].keys())
            pf_prev = p.get('pf', 'Ninguno')
            p['pf'] = st.selectbox("Material Frontal", opts_pf, index=opts_pf.index(pf_prev), key=f"pf_{p_id}")
            if p['pf'] != pf_prev: p['gf'] = PRECIOS["cartoncillo"][p['pf']]["gramaje"]
            p['gf'] = st.number_input("Gramaje F.", value=int(p.get('gf', 0)), key=f"gf_{p_id}")
            
            opts_pl = list(PRECIOS["planchas"].keys())
            p['pl'] = st.selectbox("Plancha Base", opts_pl, index=opts_pl.index(p.get('pl','Ninguna')), key=f"pl_{p_id}")
            
            opts_ap = ["C/C", "B/C", "B/B"]
            p['ap'] = st.selectbox("Calidad Onda", opts_ap, index=opts_ap.index(p.get('ap','C/C')), key=f"ap_{p_id}")
            
            opts_pd = list(PRECIOS["cartoncillo"].keys())
            p['pd'] = st.selectbox("Material Dorso", opts_pd, index=opts_pd.index(p.get('pd','Ninguno')), key=f"pd_{p_id}")
            if p['pd'] != "Ninguno": p['gd'] = st.number_input("Gramaje D.", value=int(p.get('gd',0)), key=f"gd_{p_id}")

        # Columna 3 (Acabados y Troquel)
        with c3:
            p['cor'] = st.selectbox("Corte", ["Troquelado", "Plotter"], index=["Troquelado", "Plotter"].index(p.get('cor','Troquelado')), key=f"cor_{p_id}")
            if p['cor'] == "Troquelado": 
                p['cobrar_arreglo'] = st.checkbox("¿Cobrar Arreglo?", value=p.get('cobrar_arreglo', True), key=f"arr_{p_id}")
                # EL PRECIO VENTA TROQUEL SÍ SE PUEDE VER (Es lo que se cobra al cliente)
                p['pv_troquel'] = st.number_input("PVP Troquel (€)", value=float(p.get('pv_troquel', 0.0)), key=f"pvt_{p_id}")
            
            if p['pd'] != "Ninguno":
                opts_imd = ["Offset", "Digital", "No"]
                p['im_d'] = st.selectbox("Impresión Dorso", opts_imd, index=opts_imd.index(p.get('im_d','No')), key=f"imd_{p_id}")
                if p['im_d'] == "Offset":
                    p['nt_d'] = st.number_input("Tintas D.", 0, 6, int(p.get('nt_d',0)), key=f"ntd_{p_id}")
                    p['ba_d'] = st.checkbox("Barniz D.", p.get('ba_d',False), key=f"bad_{p_id}")
                elif p['im_d'] == "Digital": p['ld_d'] = st.checkbox("Laminado D.", p.get('ld_d',False), key=f"ldd_{p_id}")
                p['pel_d'] = st.selectbox("Peliculado Dorso", opts_pel, index=opts_pel.index(p.get('pel_d','Sin Peliculado')), key=f"peld_{p_id}")
            
            if st.button("🗑 Eliminar", key=f"del_{p_id}"): del st.session_state.piezas_dict[p_id]; st.rerun()

# --- EXTRAS (SIN VER COSTES) ---
st.divider()
c_ex1, c_ex2 = st.columns(2)
with c_ex1:
    st.subheader("🧩 Accesorios")
    opts_extra = ["---"] + list(PRECIOS["extras_base"].keys())
    ex_sel = st.selectbox("Añadir accesorio:", opts_extra)
    if st.button("Añadir") and ex_sel != "---":
        # Se añade con el coste de la BD (oculto)
        st.session_state.lista_extras_grabados.append({"nombre": ex_sel, "coste": PRECIOS["extras_base"][ex_sel], "cantidad": 1.0}); st.rerun()
    
    for i, ex in enumerate(st.session_state.lista_extras_grabados):
        col_a, col_b, col_c = st.columns([4, 2, 1])
        col_a.write(f"🔹 {ex['nombre']}")
        # Solo pedimos cantidad, NO COSTE
        ex['cantidad'] = col_b.number_input("Cant/Ud", value=float(ex['cantidad']), key=f"exq_{i}")
        if col_c.button("🗑", key=f"exd_{i}"): st.session_state.lista_extras_grabados.pop(i); st.rerun()

# --- EMBALAJES (SOLO PRECIO VENTA) ---
with c_ex2:
    st.subheader("📦 Embalaje y Transporte")
    if lista_cants:
        st.info("Introduce el PRECIO VENTA UNITARIO (lo que cobrarás al cliente por caja).")
        for q in lista_cants:
            curr = st.session_state.precios_venta_embalaje.get(q, 0.0)
            val = st.number_input(f"PVP Unitario Emb. para {q} uds (€)", value=float(curr), format="%.4f", key=f"emb_{q}")
            st.session_state.precios_venta_embalaje[q] = val
    else:
        st.warning("Define cantidades primero.")

# --- CÁLCULO INTERNO (MOTOR OCULTO) ---
res_final = []
if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
    total_pv_troqueles = sum(float(pz.get('pv_troquel', 0.0)) for pz in st.session_state.piezas_dict.values())
    
    for q_n in lista_cants:
        # 1. Calcular Costes Técnicos (Sin mostrar)
        tiene_dig = any(pz["im"] == "Digital" or pz.get("im_d") == "Digital" for pz in st.session_state.piezas_dict.values())
        mn_m, _ = calcular_mermas(q_n, es_digital=tiene_dig); qp_taller = q_n + mn_m; coste_f = 0.0
        
        for p in st.session_state.piezas_dict.values():
            nb = q_n * p["pliegos"]
            mn_f, mi_f = calcular_mermas(nb, (p["im"]=="Digital"))
            waste_f = mn_f + (mi_f if p["im"] != "No" else 0); hc_f = nb + waste_f
            mn_d, mi_d = calcular_mermas(nb, (p.get("im_d")=="Digital"))
            waste_d = mn_d + (mi_d if p.get("im_d", "No") != "No" else 0); hc_d = nb + waste_d
            mn_gen, _ = calcular_mermas(nb, (p["im"]=="Digital" or p.get("im_d")=="Digital")); hp = nb + mn_gen 
            m2 = (p["w"]*p["h"])/1_000_000
            
            c_cf = (hc_f * m2 * (p.get('gf',0)/1000) * PRECIOS["cartoncillo"][p["pf"]]["precio_kg"])
            c_cd = (hc_d * m2 * (p.get('gd',0)/1000) * PRECIOS["cartoncillo"][p.get('pd','Ninguno')]["precio_kg"])
            c_pla, c_peg = 0.0, 0.0
            if p["pl"] != "Ninguna":
                c_pla = hp * m2 * PRECIOS["planchas"][p["pl"]][p.get('ap','C/C')]
                pas = (1 if p["pf"]!="Ninguno" else 0) + (1 if p.get('pd','Ninguno')!="Ninguno" else 0)
                c_peg = hp * m2 * PRECIOS["planchas"][p["pl"]]["peg"] * pas
            
            def f_o(n): return 60 if n < 100 else (120 if n > 500 else 60 + 0.15*(n-100))
            c_if = (nb*m2*6.5 if p["im"]=="Digital" else (f_o(nb)*(p.get('nt',0)+(1 if p.get('ba') else 0)) if p["im"]=="Offset" else 0))
            c_id = (nb*m2*6.5 if p.get("im_d")=="Digital" else (f_o(nb)*(p.get('nt_d',0)+(1 if p.get('ba_d') else 0)) if p.get("im_d")=="Offset" else 0))
            
            c_pel_f = (hp*m2*PRECIOS["peliculado"][p["pel"]]) + (hp*m2*3.5 if p.get("ld") else 0)
            c_pel_d = (hp*m2*PRECIOS["peliculado"].get(p.get('pel_d','Sin Peliculado'), 0)) + (hp*m2*3.5 if p.get("ld_d") else 0)
            
            l_p, w_p = p['h'], p['w']
            if l_p > 1000 or w_p > 700: v_arr, v_tir = 107.80, 0.135
            elif l_p < 1000 and w_p < 700: v_arr, v_tir = 48.19, 0.06
            else: v_arr, v_tir = 80.77, 0.09
            c_arr = v_arr if (p["cor"]=="Troquelado" and p.get('cobrar_arreglo', True)) else 0
            c_tir = (hp * v_tir) if p["cor"]=="Troquelado" else hp*1.5
            
            coste_f += c_cf + c_cd + c_pla + c_peg + c_if + c_id + c_pel_f + c_pel_d + c_arr + c_tir

        # Costes Mano de Obra y Extras
        c_ext_tot = sum(e["coste"] * e["cantidad"] * qp_taller for e in st.session_state.lista_extras_grabados)
        c_mo = ((seg_man_total/3600)*18*qp_taller) + (qp_taller*dif_ud)
        
        # 2. Aplicar Márgenes Ocultos (Fijos)
        pvp_producto_base = ((coste_f + c_ext_tot + c_mo) * MARGEN_GENERAL) + IMPORTE_FIJO_OCULTO
        
        # Embalaje (Directo PVP)
        pv_emb_ud = st.session_state.precios_venta_embalaje.get(q_n, 0.0)
        pv_emb_total = pv_emb_ud * q_n
        
        # Total
        pvp_total_todo = pvp_producto_base + pv_emb_total + total_pv_troqueles
        
        res_final.append({
            "Cantidad": q_n, 
            "Precio Venta Unitario": f"{pvp_producto_base/q_n:.3f}€",
            "Precio Embalaje Unitario": f"{pv_emb_ud:.3f}€",
            "Troqueles (Total)": f"{total_pv_troqueles:.2f}€",
            "PRECIO VENTA TOTAL": f"{pvp_total_todo:.2f}€",
            "UNITARIO (TODO)": f"{pvp_total_todo/q_n:.3f}€"
        })

# --- SALIDA VISUAL (SOLO OFERTA) ---
if res_final:
    st.divider()
    desc_html = """<div style='text-align: left; margin-bottom: 20px; color: #444;'>
    <h4 style='color: #1E88E5; margin-bottom: 5px;'>📋 Especificaciones</h4><ul style='list-style-type: none; padding-left: 0;'>"""
    
    for p in st.session_state.piezas_dict.values():
        mat_f = f"<b>Frontal:</b> {p['pf']} ({p.get('gf',0)}g)" if p['pf'] != "Ninguno" else ""
        mat_d = f" | <b>Dorso:</b> {p['pd']} ({p.get('gd',0)}g)" if p.get('pd', "Ninguno") != "Ninguno" else ""
        mat_pl = f" | <b>Base:</b> {p['pl']}" if p.get('pl', "Ninguna") != "Ninguna" else ""
        detalles = mat_f + mat_d + mat_pl if (mat_f+mat_d+mat_pl) else "Sin materiales definidos"
        desc_html += f"<li style='margin-bottom: 8px;'>🔹 <b>{p['nombre']}</b> ({p['h']}x{p['w']} mm)<br><span style='font-size:0.9em; color:#666; margin-left: 20px;'>{detalles}</span></li>"
    
    if st.session_state.lista_extras_grabados:
        items = [f"{ex['nombre']} (x{int(ex['cantidad'])})" for ex in st.session_state.lista_extras_grabados]
        desc_html += f"<li style='margin-top: 10px;'><b>🧩 Accesorios:</b> {', '.join(items)}</li>"
    
    desc_html += "</ul></div>"

    rows = ""
    for r in res_final:
        rows += f"""<tr><td><b>{r['Cantidad']}</b></td><td>{r['Precio Venta Unitario']}</td><td>{r['Precio Embalaje Unitario']}</td><td>{r['Troqueles (Total)']}</td><td style='background-color:#f0f8ff;'>{r['PRECIO VENTA TOTAL']}</td><td style='color:#1E88E5; font-weight:bold;'>{r['UNITARIO (TODO)']}</td></tr>"""

    st.markdown(f"""
    <div class="comercial-box">
        <h2 class="comercial-header">OFERTA COMERCIAL - {st.session_state.cli}</h2>
        <p class="comercial-ref">Ref: {st.session_state.brf}</p>
        {desc_html}
        <table class="comercial-table">
            <tr><th>Cantidad</th><th>P. Venta Unitario</th><th>P. Emb. Unitario</th><th>Troqueles</th><th>TOTAL</th><th>UNITARIO (TODO)</th></tr>
            {rows}
        </table>
        <p style='text-align: right; font-size: 0.9em; color: #777; margin-top: 15px;'>* Oferta válida salvo error tipográfico. IVA no incluido.</p>
    </div>""", unsafe_allow_html=True)
elif lista_cants:
    st.info("Añade formas y configura los datos para ver la oferta.")
