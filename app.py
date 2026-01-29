import streamlit as st
import pandas as pd
import json

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

# --- 2. MOTORES TÉCNICOS ---

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
        mayor, intermedia = dims[0], dims[1]
        area_base = mayor * intermedia
        coste_250 = (0.00000091 * area_base) + 1.00
        if q >= 250: return coste_250 * ((q / 250) ** -0.32)
        elif q == 100: return 2.69
        elif 100 < q < 250:
            progreso = (q - 100) / (250 - 100)
            return 2.69 + progreso * (coste_250 - 2.69)
        else: return 2.69
    return 0.0

# --- 3. INICIALIZACIÓN ---
st.set_page_config(page_title="MAINSA ADMIN V33", layout="wide")

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
if 'lista_embalajes' not in st.session_state: st.session_state.lista_embalajes = []

st.markdown("""<style>
    .comercial-box { background-color: white; padding: 30px; border: 2px solid #1E88E5; border-radius: 10px; color: #333; }
    .comercial-header { color: #1E88E5; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .comercial-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 1.1em; }
    .comercial-table th { background-color: #1E88E5; color: white; padding: 10px; }
    .comercial-table td { padding: 10px; border: 1px solid #ddd; text-align: center; }
</style>""", unsafe_allow_html=True)

st.title("🛡️ PANEL ADMIN - ESCANDALLO")

# --- 4. PANEL LATERAL (CONTROL TOTAL) ---
with st.sidebar:
    st.header("⚙️ Configuración Admin")
    
    # --- ZONA DE IMPORTACIÓN INTELIGENTE ---
    with st.expander("🤖 Importar Datos de IA/PDF", expanded=False):
        st.info("Sube el JSON generado por Gemini")
        subida_ia = st.file_uploader("Archivo JSON", type=["json"], key="uploader_ia")
        
        if subida_ia:
            try:
                di = json.load(subida_ia)
                
                # 1. ACTUALIZAR VARIABLES GLOBALES DE SESIÓN
                # Asignamos directamente a las 'keys' de los widgets para forzar el cambio visual
                if "cli" in di: st.session_state.cli_input = di["cli"]
                if "brf" in di: st.session_state.brf_input = di["brf"]
                
                if "cantidades" in di: 
                    st.session_state.cants_input = ", ".join(map(str, di["cantidades"]))
                
                if "tiempo_manipulacion" in di: 
                    # Detectar si son segundos o minutos (asumimos minutos si viene del JSON suele ser manipulación)
                    st.session_state.t_input_widget = float(di["tiempo_manipulacion"])
                    
                if "dificultad" in di: 
                    # Buscamos el índice correcto para el selectbox
                    vals_dif = [0.02, 0.061, 0.091]
                    val = float(di["dificultad"])
                    if val in vals_dif:
                        st.session_state.dif_input = val
                    else:
                        st.session_state.dif_input = 0.091 # Default si no coincide

                if "imp_fijo" in di: st.session_state.fijo_input = float(di["imp_fijo"])
                if "margen" in di: st.session_state.margen_input = float(di["margen"])

                # 2. CARGAR LISTAS SIMPLES
                st.session_state.lista_embalajes = di.get("embalajes", [])
                st.session_state.lista_extras_grabados = di.get("extras", [])
                
                # 3. CARGAR PIEZAS Y LIMPIAR CACHÉ DE WIDGETS ANTIGUOS
                # Esto es CRUCIAL: Borramos la memoria de los inputs de las formas (n_0, h_0...)
                # para que se regeneren con los nuevos datos del diccionario.
                if "piezas" in di:
                    # Cargamos el diccionario
                    st.session_state.piezas_dict = {int(k): v for k, v in di["piezas"].items()}
                    
                    # Lista de prefijos que usamos en los widgets de las formas
                    prefijos_widgets = ["n_", "p_", "h_", "w_", "im_", "nt_", "ba_", "ld_", "pel_", 
                                      "pf_", "gf_", "pl_", "ap_", "pd_", "gd_", "cor_", "arr_", "pvt_",
                                      "imd_", "ntd_", "bad_", "ldd_", "peld_"]
                    
                    # Borramos estado de session_state para obligar a leer del diccionario
                    keys_a_borrar = []
                    for k in st.session_state.keys():
                        for pid in st.session_state.piezas_dict.keys():
                            # Si la key empieza por un prefijo y termina con el ID de la pieza (ej: h_0)
                            for pre in prefijos_widgets:
                                if k == f"{pre}{pid}":
                                    keys_a_borrar.append(k)
                    
                    for k in keys_a_borrar:
                        if k in st.session_state:
                            del st.session_state[k]

                st.success("¡Datos cargados correctamente!")
                # Forzamos recarga para ver los cambios
                st.rerun()
                
            except Exception as e:
                st.error(f"Error al leer JSON: {e}")

    # --- INPUTS MANUALES (CON KEYS EXPLICITAS PARA PODER ESCRIBIRLES DESDE ARRIBA) ---
    # Usamos st.session_state.get para el valor por defecto, pero la key es lo importante.
    
    st.session_state.cli = st.text_input("Cliente", value=st.session_state.get('cli', ""), key="cli_input")
    st.session_state.brf = st.text_input("Nº Briefing", value=st.session_state.get('brf', ""), key="brf_input")
    st.divider()
    
    # Cantidades
    cants_str = st.text_input("Cantidades (ej: 500, 1000)", value="0", key="cants_input")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    
    unidad_t = st.radio("Manipulación en:", ["Segundos", "Minutos"], horizontal=True)
    
    # Tiempo
    t_input = st.number_input(f"Tiempo montaje/ud", value=0.0, key="t_input_widget")
    seg_man_total = t_input * 60 if unidad_t == "Minutos" else t_input
    
    st.divider()
    
    # Dificultad
    dif_ud = st.selectbox("Dificultad (€/ud)", [0.02, 0.061, 0.091], index=2, key="dif_input")
    
    # Fijo y Margen
    imp_fijo_pvp = st.number_input("Importe Fijo PVP (€)", value=500.0, help="Suma directa al precio.", key="fijo_input")
    margen = st.number_input("Multiplicador Comercial", value=2.2, step=0.1, key="margen_input")

    st.divider()
    modo_comercial = st.checkbox("🌟 VISTA OFERTA COMERCIAL", value=False)
    
    st.header("📂 Gestión de Archivos")
    partes_nombre = [st.session_state.brf, st.session_state.cli]
    nombre_archivo = "ADMIN_" + "_".join([str(p).strip() for p in partes_nombre if str(p).strip()]) + ".json"
    
    datos_exp = {
        "brf": st.session_state.brf, "cli": st.session_state.cli, "piezas": st.session_state.piezas_dict, 
        "extras": st.session_state.lista_extras_grabados, "embalajes": st.session_state.lista_embalajes,
        "imp_fijo": imp_fijo_pvp, "margen": margen, "cantidades": lista_cants, 
        "tiempo_manipulacion": t_input, "dificultad": dif_ud
    }
    st.download_button("💾 Guardar Proyecto", json.dumps(datos_exp, indent=4), file_name=nombre_archivo)

# --- 5. ENTRADA DE DATOS ---
if not modo_comercial:
    # SECCIÓN 1: FORMAS
    st.header("1. Definición Técnica de Formas")
    c_btns = st.columns([1, 4])
    if c_btns[0].button("➕ Forma"):
        nid = max(st.session_state.piezas_dict.keys()) + 1
        st.session_state.piezas_dict[nid] = crear_forma_vacia(nid); st.rerun()
    if c_btns[1].button("🗑 Reiniciar Todo"):
        st.session_state.piezas_dict = {0: crear_forma_vacia(0)}; st.session_state.lista_extras_grabados = []; st.session_state.lista_embalajes = []; st.rerun()

    for p_id, p in st.session_state.piezas_dict.items():
        with st.expander(f"🛠 {p['nombre']} - {p['h']}x{p['w']} mm", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                p['nombre'] = st.text_input("Etiqueta", p['nombre'], key=f"n_{p_id}")
                p['pliegos'] = st.number_input("Pliegos/Ud", 0.0, 100.0, float(p['pliegos']), key=f"p_{p_id}")
                p['h'] = st.number_input("Largo mm", 0, 5000, int(p['h']), key=f"h_{p_id}")
                p['w'] = st.number_input("Ancho mm", 0, 5000, int(p['w']), key=f"w_{p_id}")
                p['im'] = st.selectbox("Sistema Cara", ["Offset", "Digital", "No"], index=["Offset", "Digital", "No"].index(p['im']), key=f"im_{p_id}")
                if p['im'] == "Offset":
                    p['nt'] = st.number_input("Tintas F.", 0, 6, int(p.get('nt',4)), key=f"nt_{p_id}")
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
                if p['pd'] != "Ninguno": p['gd'] = st.number_input("Gramaje D.", value=int(p.get('gd',0)), key=f"gd_{p_id}")
            with col3:
                p['cor'] = st.selectbox("Corte", ["Troquelado", "Plotter"], index=["Troquelado", "Plotter"].index(p.get('cor', 'Troquelado')), key=f"cor_{p_id}")
                if p['cor'] == "Troquelado": 
                    p['cobrar_arreglo'] = st.checkbox("¿Cobrar Arreglo?", value=p.get('cobrar_arreglo', True), key=f"arr_{p_id}")
                    p['pv_troquel'] = st.number_input("Precio Venta Troquel (€)", value=float(p.get('pv_troquel', 0.0)), key=f"pvt_{p_id}")
                if p['pd'] != "Ninguno":
                    p['im_d'] = st.selectbox("Sistema Dorso", ["Offset", "Digital", "No"], index=["Offset", "Digital", "No"].index(p.get('im_d', 'No')), key=f"imd_{p_id}")
                    if p['im_d'] == "Offset":
                        p['nt_d'] = st.number_input("Tintas D.", 0, 6, int(p.get('nt_d',0)), key=f"ntd_{p_id}")
                        p['ba_d'] = st.checkbox("Barniz D.", p.get('ba_d',False), key=f"bad_{p_id}")
                    elif p['im_d'] == "Digital": p['ld_d'] = st.checkbox("Laminado Digital D.", p.get('ld_d',False), key=f"ldd_{p_id}")
                    p['pel_d'] = st.selectbox("Peliculado Dorso", list(PRECIOS["peliculado"].keys()), index=list(PRECIOS["peliculado"].keys()).index(p.get('pel_d', 'Sin Peliculado')), key=f"peld_{p_id}")
                if st.button("🗑 Borrar Forma", key=f"del_{p_id}"): del st.session_state.piezas_dict[p_id]; st.rerun()

    # SECCIÓN EXTRAS
    st.divider(); st.subheader("📦 2. Almacén de Accesorios")
    ex_sel = st.selectbox("Añadir extra:", ["---"] + list(PRECIOS["extras_base"].keys()))
    if st.button("➕ Añadir Accesorio") and ex_sel != "---":
        st.session_state.lista_extras_grabados.append({"nombre": ex_sel, "coste": PRECIOS["extras_base"][ex_sel], "cantidad": 1.0}); st.rerun()
    for i, ex in enumerate(st.session_state.lista_extras_grabados):
        ca, cb, cc, cd = st.columns([3, 2, 2, 1]); ca.write(f"**{ex['nombre']}**"); ex['coste'] = cb.number_input("€/ud compra", value=float(ex['coste']), key=f"exc_{i}"); ex['cantidad'] = cc.number_input("Cant/Ud prod", value=float(ex['cantidad']), key=f"exq_{i}")
        if cd.button("🗑", key=f"exd_{i}"): st.session_state.lista_extras_grabados.pop(i); st.rerun()

    # SECCIÓN EMBALAJES
    st.divider(); st.subheader("📦 3. Complemento de Embalajes")
    tipo_em = st.selectbox("Tipo de Caja:", ["Plano (Canal 5)", "En Volumen", "Guainas"])
    if st.button("➕ Añadir Embalaje"):
        st.session_state.lista_embalajes.append({"tipo": tipo_em, "l": 0, "w": 0, "a": 0, "uds": 1}); st.rerun()
    for i, em in enumerate(st.session_state.lista_embalajes):
        with st.info(f"Embalaje {i+1}: {em['tipo']}"):
            ce1, ce2, ce3, ce4, ce5 = st.columns(5)
            em['l'], em['w'], em['a'], em['uds'] = ce1.number_input("L mm", value=em['l'], key=f"el_{i}"), ce2.number_input("W mm", value=em['w'], key=f"ew_{i}"), ce3.number_input("A mm", value=em['a'], key=f"ea_{i}"), ce4.number_input("C/U", value=em['uds'], key=f"eu_{i}")
            if ce5.button("🗑", key=f"ed_{i}"): st.session_state.lista_embalajes.pop(i); st.rerun()

# --- 6. MOTOR DE CÁLCULO ---
res_final, desc_full = [], {}
if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
    total_pv_troqueles = sum(float(pz.get('pv_troquel', 0.0)) for pz in st.session_state.piezas_dict.values())
    
    for q_n in lista_cants:
        tiene_dig = any(pz["im"] == "Digital" or pz.get("im_d") == "Digital" for pz in st.session_state.piezas_dict.values())
        mn_m, _ = calcular_mermas(q_n, es_digital=tiene_dig); qp_taller = q_n + mn_m; coste_f, det_f = 0.0, []
        
        for p_id, p in st.session_state.piezas_dict.items():
            nb = q_n * p["pliegos"]
            
            # --- NUEVA LÓGICA MERMAS INDEPENDIENTES CARA/DORSO ---
            # Cara: Si no hay impresión, solo mermas normales (manipulado), ignoramos impresión.
            mn_f, mi_f = calcular_mermas(nb, (p["im"]=="Digital"))
            waste_f = mn_f + (mi_f if p["im"] != "No" else 0)
            hc_f = nb + waste_f # Hoja Compra Frontal
            
            # Dorso: Si no hay impresión, solo mermas normales.
            mn_d, mi_d = calcular_mermas(nb, (p.get("im_d")=="Digital"))
            waste_d = mn_d + (mi_d if p.get("im_d", "No") != "No" else 0)
            hc_d = nb + waste_d # Hoja Compra Dorso

            # Hoja Pasada (Finishing): Usamos la merma base (normalmente la de la cara marca el proceso)
            mn_gen, _ = calcular_mermas(nb, (p["im"]=="Digital" or p.get("im_d")=="Digital"))
            hp = nb + mn_gen 

            m2 = (p["w"]*p["h"])/1_000_000
            
            # --- MATERIALES (Desglosado) ---
            c_cf = (hc_f * m2 * (p.get('gf',0)/1000) * PRECIOS["cartoncillo"][p["pf"]]["precio_kg"])
            c_cd = (hc_d * m2 * (p.get('gd',0)/1000) * PRECIOS["cartoncillo"][p.get('pd','Ninguno')]["precio_kg"])
            c_pla, c_peg = 0.0, 0.0
            if p["pl"] != "Ninguna":
                c_pla = hp * m2 * PRECIOS["planchas"][p["pl"]][p.get('ap','C/C')]
                pas = (1 if p["pf"]!="Ninguno" else 0) + (1 if p.get('pd','Ninguno')!="Ninguno" else 0)
                c_peg = hp * m2 * PRECIOS["planchas"][p["pl"]]["peg"] * pas
            
            # --- IMPRESIÓN (Desglosado) ---
            def f_o(n): return 60 if n < 100 else (120 if n > 500 else 60 + 0.15*(n-100))
            c_if = (nb*m2*6.5 if p["im"]=="Digital" else (f_o(nb)*(p.get('nt',0)+(1 if p.get('ba') else 0)) if p["im"]=="Offset" else 0))
            c_id = (nb*m2*6.5 if p.get("im_d")=="Digital" else (f_o(nb)*(p.get('nt_d',0)+(1 if p.get('ba_d') else 0)) if p.get("im_d")=="Offset" else 0))
            
            # --- NARBA / ACABADOS (Desglosado) ---
            c_pel_f = (hp*m2*PRECIOS["peliculado"][p["pel"]]) + (hp*m2*3.5 if p.get("ld") else 0)
            c_pel_d = (hp*m2*PRECIOS["peliculado"].get(p.get('pel_d','Sin Peliculado'), 0)) + (hp*m2*3.5 if p.get("ld_d") else 0)
            
            # Criterio Arreglo
            l_p, w_p = p['h'], p['w']
            if l_p > 1000 or w_p > 700: v_arr, v_tir = 107.80, 0.135
            elif l_p < 1000 and w_p < 700: v_arr, v_tir = 48.19, 0.06
            else: v_arr, v_tir = 80.77, 0.09
            
            c_arr = v_arr if (p["cor"]=="Troquelado" and p.get('cobrar_arreglo', True)) else 0
            c_tir = (hp * v_tir) if p["cor"]=="Troquelado" else hp*1.5
            
            s_imp = c_if + c_id
            s_narba = c_pel_f + c_pel_d + c_peg + c_arr + c_tir
            s_mat = c_cf + c_pla + c_cd
            sub = s_imp + s_narba + s_mat
            coste_f += sub
            
            # --- NUEVO DESGLOSE PARA AUDITORÍA ---
            det_f.append({
                "Pieza": p["nombre"],
                # Grupo Materiales
                "Mat. Frontal": c_cf,
                "Mat. Dorso": c_cd,
                "Mat. Ondulado": c_pla,
                # Grupo Impresión
                "Imp. Cara": c_if,
                "Imp. Dorso": c_id,
                # Grupo Narba
                "Acab. Peliculado": c_pel_f + c_pel_d,
                "Acab. Contracolado": c_peg,
                "Acab. Troquel/Corte": c_arr + c_tir,
                # Totales Originales (para referencia rápida)
                "Total Imp": s_imp, 
                "Total Narba": s_narba, 
                "Total Mat": s_mat, 
                "Subtotal": sub
            })

        c_ext_tot = sum(e["coste"] * e["cantidad"] * qp_taller for e in st.session_state.lista_extras_grabados)
        c_mo = ((seg_man_total/3600)*18*qp_taller) + (qp_taller*dif_ud)
        
        # Embalaje
        coste_emb_taller = sum(motor_embalajes(em['tipo'], em['l'], em['w'], em['a'], q_n*em['uds']) * (q_n*em['uds']) for em in st.session_state.lista_embalajes)
        pv_emb_total = coste_emb_taller * margen
        pv_emb_ud = pv_emb_total / q_n if q_n > 0 else 0
        
        # --- PVP PRODUCTO ---
        pvp_producto_base = ((coste_f + c_ext_tot + c_mo) * margen) + imp_fijo_pvp
        pvp_total_todo = pvp_producto_base + pv_emb_total + total_pv_troqueles
        
        # Calculamos unitarios para la tabla
        p_venta_unitario = pvp_producto_base / q_n if q_n > 0 else 0
        p_total_unitario_all = pvp_total_todo / q_n if q_n > 0 else 0

        res_final.append({
            "Cantidad": q_n, 
            "Precio Venta Unitario": f"{p_venta_unitario:.3f}€",
            "Precio Embalaje Unitario": f"{pv_emb_ud:.3f}€",
            "Precio Troquel (Total)": f"{total_pv_troqueles:.2f}€",
            "Precio Venta Total": f"{pvp_total_todo:.2f}€",
            "Unitario (Todo Incluido)": f"{p_total_unitario_all:.3f}€"
        })
        desc_full[q_n] = {"det": det_f, "mo": c_mo, "extras": c_ext_tot, "fijo": imp_fijo_pvp, "taller": coste_f + c_mo + c_ext_tot, "qp": qp_taller}

# --- 7. SALIDA VISUAL ---
if modo_comercial and res_final:
    # 1. Generar HTML de Descripción Técnica
    desc_html = """<div style='text-align: left; margin-bottom: 20px; color: #444;'>
    <h4 style='color: #1E88E5; margin-bottom: 5px;'>📋 Especificaciones del Proyecto</h4>
    <ul style='list-style-type: none; padding-left: 0;'>"""
    
    # Detalle Formas
    for p in st.session_state.piezas_dict.values():
        mat_info = f"{p['pf']} ({p['gf']}g)" if p['pf'] != "Ninguno" else "Sin cartoncillo"
        desc_html += f"<li style='margin-bottom: 5px;'>🔹 <b>{p['nombre']}</b>: {p['h']}x{p['w']} mm. Material: {mat_info}.</li>"
    
    # Detalle Accesorios
    if st.session_state.lista_extras_grabados:
        desc_html += "<li style='margin-top: 10px;'><b>🧩 Accesorios:</b> "
        items_acc = [f"{ex['nombre']} (x{int(ex['cantidad']) if ex['cantidad'].is_integer() else ex['cantidad']})" for ex in st.session_state.lista_extras_grabados]
        desc_html += ", ".join(items_acc) + "</li>"

    # Detalle Embalaje
    if st.session_state.lista_embalajes:
        desc_html += "<li style='margin-top: 10px;'><b>📦 Embalaje:</b> "
        items_emb = [f"{em['tipo']} ({em['l']}x{em['w']}x{em['a']} mm)" for em in st.session_state.lista_embalajes]
        desc_html += ", ".join(items_emb) + "</li>"
    else:
        desc_html += "<li style='margin-top: 10px;'><b>📦 Embalaje:</b> Sin embalaje especial (A granel/Palet).</li>"

    desc_html += "</ul></div>"

    # 2. Generar Tabla de Precios
    # Cabeceras exactas solicitadas
    headers = ["Cantidad", "Precio venta unitario", "Precio Embalaje unitario", "Precio Troquel (total)", "Precio Venta Total", "Unitario (Todo Incluido)"]
    
    rows_html = ""
    for r in res_final:
        rows_html += f"""<tr>
            <td style='font-weight:bold;'>{r['Cantidad']}</td>
            <td>{r['Precio Venta Unitario']}</td>
            <td>{r['Precio Embalaje Unitario']}</td>
            <td>{r['Precio Troquel (Total)']}</td>
            <td style='background-color: #f0f8ff;'>{r['Precio Venta Total']}</td>
            <td style='font-weight:bold; color: #1E88E5;'>{r['Unitario (Todo Incluido)']}</td>
        </tr>"""

    st.markdown(f"""
    <div class="comercial-box">
        <h2 class="comercial-header">OFERTA COMERCIAL - {st.session_state.cli}</h2>
        {desc_html}
        <table class="comercial-table">
            <tr>
                <th>Cantidad</th>
                <th>P. Venta Unitario</th>
                <th>P. Emb. Unitario</th>
                <th>Troqueles (Total)</th>
                <th>PRECIO VENTA TOTAL</th>
                <th>UNITARIO (TODO)</th>
            </tr>
            {rows_html}
        </table>
        <p style='text-align: right; font-size: 0.9em; color: #777; margin-top: 15px;'>* Oferta válida salvo error tipográfico. IVA no incluido.</p>
    </div>
    """, unsafe_allow_html=True)

else:
    if res_final:
        st.header(f"📊 Resumen de Venta: {st.session_state.cli}")
        # Ajustamos el dataframe normal para que tenga coherencia con los nuevos datos, aunque manteniendo simplicidad visual si se quiere
        st.dataframe(pd.DataFrame(res_final), use_container_width=True)
        
        for q, info in desc_full.items():
            with st.expander(f"🔍 Auditoría Taller {q} uds (Taller: {info['qp']} uds)"):
                df_raw = pd.DataFrame(info["det"])
                cols_order = ["Pieza", "Mat. Frontal", "Mat. Dorso", "Mat. Ondulado", "Total Mat",
                              "Imp. Cara", "Imp. Dorso", "Total Imp",
                              "Acab. Peliculado", "Acab. Contracolado", "Acab. Troquel/Corte", "Total Narba", "Subtotal"]
                cols_final = [c for c in cols_order if c in df_raw.columns]
                df_sorted = df_raw[cols_final]

                sum_row = {"Pieza": "TOTAL PROYECTO"}
                for col in cols_final[1:]:
                    sum_row[col] = df_sorted[col].sum()
                
                df_f = pd.concat([df_sorted, pd.DataFrame([sum_row])], ignore_index=True)

                st.table(df_f.style.format("{:.2f}€", subset=df_f.columns[1:])
                         .set_properties(**{'background-color': '#e3f2fd', 'font-weight': 'bold'}, subset=["Total Imp","Total Narba","Total Mat","Subtotal"])
                         .set_properties(**{'color': '#666'}, subset=["Mat. Frontal", "Mat. Dorso", "Mat. Ondulado", "Imp. Cara", "Imp. Dorso", "Acab. Peliculado", "Acab. Contracolado", "Acab. Troquel/Corte"])
                         )
                st.metric("COSTO TALLER (Sin Margen)", f"{info['taller']:.2f}€")
