import streamlit as st
import pandas as pd
import json
import re

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

# --- LISTA DE FORMATOS COMUNES ---
FORMATOS_STD = {
    "Personalizado": (0, 0),
    "1600x1200": (1600, 1200),
    "1600x1100": (1600, 1100),
    "1400x1000": (1400, 1000),
    "1300x900": (1300, 900),
    "1200x800": (1200, 800),
    "1100x800": (1100, 800),
    "1000x700": (1000, 700),
    "900x650": (900, 650),
    "800x550": (800, 550),
    "700x500": (700, 500)
}

# --- 2. MOTORES TÉCNICOS ---
def calcular_mermas_estandar(n, es_digital=False):
    """
    Devuelve tupla: (merma_procesos_unidades, merma_impresion_hojas)
    Actualizado según tabla del usuario (V19).
    """
    if es_digital: 
        # Digital suele tener arranques muy bajos. Mantenemos logica simple o 0 si prefieres.
        return int(n * 0.02), 10 
    
    # Lógica OFFSET según tabla proporcionada
    if n < 100: return 10, 150
    if n < 200: return 20, 175
    if n < 600: return 30, 200
    if n < 1000: return 40, 220
    if n < 2000: return 50, 250
    # Para 2000 o más
    return int(n * 0.03), 300

# --- 3. INICIALIZACIÓN ---
st.set_page_config(page_title="MAINSA ADMIN V33", layout="wide")

def crear_forma_vacia(index):
    return {
        "nombre": f"Forma {index + 1}", "pliegos": 1.0, "w": 0, "h": 0, 
        "pf": "Ninguno", "gf": 0, "pl": "Ninguna", 
        "ap": "B/C", 
        "pd": "Ninguno", "gd": 0, 
        "im": "No", "nt": 0, "ba": False, 
        "im_d": "No", "nt_d": 0, "ba_d": False, "pel": "Sin Peliculado", 
        "pel_d": "Sin Peliculado", "ld": False, "ld_d": False, 
        "cor": "Troquelado", "cobrar_arreglo": True, "pv_troquel": 0.0
    }

if 'piezas_dict' not in st.session_state: st.session_state.piezas_dict = {0: crear_forma_vacia(0)}
if 'lista_extras_grabados' not in st.session_state: st.session_state.lista_extras_grabados = []
if 'costes_embalaje_manual' not in st.session_state: st.session_state.costes_embalaje_manual = {}
# Diccionarios separados para las dos mermas
if 'mermas_imp_manual' not in st.session_state: st.session_state.mermas_imp_manual = {}
if 'mermas_proc_manual' not in st.session_state: st.session_state.mermas_proc_manual = {}

st.markdown("""<style>
    .comercial-box { background-color: white; padding: 30px; border: 2px solid #1E88E5; border-radius: 10px; color: #333; }
    .comercial-header { color: #1E88E5; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 5px; }
    .comercial-ref { text-align: center; color: #555; font-size: 1.1em; margin-bottom: 25px; font-weight: bold; }
    .comercial-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 1.1em; }
    .comercial-table th { background-color: #1E88E5; color: white; padding: 10px; }
    .comercial-table td { padding: 10px; border: 1px solid #ddd; text-align: center; }
</style>""", unsafe_allow_html=True)

st.title("🛡️ PANEL ADMIN - ESCANDALLO")

# --- 4. PANEL LATERAL (CONTROL TOTAL) ---
with st.sidebar:
    st.header("⚙️ Configuración Admin")
    
    with st.expander("🤖 Importar Datos (IA/PDF)", expanded=True):
        tab_up, tab_paste = st.tabs(["📂 Subir Archivo", "📋 Pegar Texto"])
        datos_json = None
        
        with tab_up:
            subida_ia = st.file_uploader("Sube el JSON", type=["json"], key="uploader_ia")
            if subida_ia:
                if 'last_loaded_name' not in st.session_state or st.session_state.last_loaded_name != subida_ia.name:
                    try: 
                        datos_json = json.load(subida_ia)
                        st.session_state.last_loaded_name = subida_ia.name
                    except Exception as e: st.error(f"Error archivo: {e}")

        with tab_paste:
            texto_json = st.text_area("Pega el JSON aquí", height=150)
            if st.button("🚀 Cargar desde Texto"):
                try:
                    if texto_json.strip():
                        texto_limpio = re.sub(r'\[cite.*?\]', '', texto_json)
                        texto_limpio = re.sub(r'\[cite_start.*?\]', '', texto_limpio)
                        datos_json = json.loads(texto_limpio)
                    else: st.warning("El campo está vacío")
                except Exception as e: st.error(f"Error JSON: {e}")

        if datos_json:
            try:
                di = datos_json
                if "cli" in di: st.session_state["cli_input"] = di["cli"].strip() if isinstance(di["cli"], str) else di["cli"]
                if "brf" in di: st.session_state["brf_input"] = str(di["brf"]).strip()
                if "cantidades" in di: st.session_state["cants_input"] = ", ".join(map(str, di["cantidades"]))
                if "tiempo_manipulacion" in di: st.session_state["t_input_widget"] = float(di["tiempo_manipulacion"])
                if "unidad_manipulacion" in di:
                     val_u = str(di["unidad_manipulacion"])
                     st.session_state["unidad_t_input"] = "Minutos" if "in" in val_u.lower() else "Segundos"
                if "dificultad" in di: 
                    v = float(di["dificultad"])
                    st.session_state["dif_input"] = v if v in [0.02, 0.061, 0.091] else 0.091
                if "imp_fijo" in di: st.session_state["fijo_input"] = float(di["imp_fijo"])
                if "margen" in di: st.session_state["margen_input"] = float(di["margen"])

                raw_ext = di.get("extras", [])
                clean_ext = []
                for ex in raw_ext:
                    nom = ex.get("nombre", ex.get("nota", ex.get("descripcion", "Accesorio")))
                    if isinstance(nom, str): nom = nom.strip()
                    clean_ext.append({"nombre": nom, "coste": ex.get("coste", 0.0), "cantidad": ex.get("cantidad", 1.0)})
                st.session_state.lista_extras_grabados = clean_ext
                
                if "costes_emb" in di:
                    st.session_state.costes_embalaje_manual = {int(k): float(v) for k, v in di["costes_emb"].items()}
                else: st.session_state.costes_embalaje_manual = {}
                
                # Reset mermas manuales al importar nuevo
                st.session_state.mermas_imp_manual = {}
                st.session_state.mermas_proc_manual = {}

                if "piezas" in di:
                    st.session_state.piezas_dict = {int(k): v for k, v in di["piezas"].items()}
                    for pid, p in st.session_state.piezas_dict.items():
                        mapa_widgets = {
                            "nombre": "n_", "pliegos": "p_", "h": "h_", "w": "w_", 
                            "im": "im_", "nt": "nt_", "ba": "ba_", "ld": "ld_", "pel": "pel_",
                            "pf": "pf_", "gf": "gf_", "pl": "pl_", "ap": "ap_", 
                            "pd": "pd_", "gd": "gd_", 
                            "cor": "cor_", "cobrar_arreglo": "arr_", "pv_troquel": "pvt_",
                            "im_d": "imd_", "nt_d": "ntd_", "ba_d": "bad_", "ld_d": "ldd_", "pel_d": "peld_"
                        }
                        for key_json, prefix_widget in mapa_widgets.items():
                            key_streamlit = f"{prefix_widget}{pid}"
                            val = None
                            if key_json in p: val = p[key_json]
                            if key_json == "pv_troquel" and "coste_troquel_estimado" in p: 
                                try: val = float(str(p["coste_troquel_estimado"]).split("€")[0].strip())
                                except: val = 0.0
                            if val is not None:
                                if isinstance(val, str): val = val.strip()
                                if prefix_widget in ["p_", "pvt_", "gf_", "gd_"]: val = float(val)
                                if prefix_widget in ["h_", "w_", "nt_", "ntd_"]: val = int(val)
                                st.session_state[key_streamlit] = val
                st.toast("✅ Datos cargados correctamente.", icon="🧠")
                st.rerun()
            except Exception as e: st.error(f"Error procesando datos: {e}")

    st.session_state.cli = st.text_input("Cliente", key="cli_input", value=st.session_state.get("cli_input", ""))
    st.session_state.brf = st.text_input("Nº Briefing", key="brf_input", value=st.session_state.get("brf_input", ""))
    st.divider()
    
    cants_str = st.text_input("Cantidades (ej: 500, 1000)", key="cants_input", value=st.session_state.get("cants_input", "0"))
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    
    unidad_t = st.radio("Manipulación en:", ["Segundos", "Minutos"], horizontal=True, key="unidad_t_input")
    t_input = st.number_input(f"Tiempo montaje/ud", key="t_input_widget", value=st.session_state.get("t_input_widget", 0.0))
    seg_man_total = t_input * 60 if unidad_t == "Minutos" else t_input
    
    st.divider()
    
    idx_dif = 2
    val_act_dif = st.session_state.get("dif_input", 0.091)
    if val_act_dif in [0.02, 0.061, 0.091]: idx_dif = [0.02, 0.061, 0.091].index(val_act_dif)
    dif_ud = st.selectbox("Dificultad (€/ud)", [0.02, 0.061, 0.091], index=idx_dif, key="dif_input")
    
    imp_fijo_pvp = st.number_input("Importe Fijo PVP (€)", key="fijo_input", value=st.session_state.get("fijo_input", 500.0))
    margen = st.number_input("Multiplicador Comercial", step=0.1, key="margen_input", value=st.session_state.get("margen_input", 2.2))

    st.divider()
    modo_comercial = st.checkbox("🌟 VISTA OFERTA COMERCIAL", value=False)
    
    st.header("📂 Gestión de Archivos")
    partes_nombre = [st.session_state.brf, st.session_state.cli]
    nombre_archivo = "ADMIN_" + "_".join([str(p).strip() for p in partes_nombre if str(p).strip()]) + ".json"
    
    datos_exp = {
        "brf": st.session_state.brf, "cli": st.session_state.cli, "piezas": st.session_state.piezas_dict, 
        "extras": st.session_state.lista_extras_grabados, "costes_emb": st.session_state.costes_embalaje_manual,
        "mermas_imp": st.session_state.mermas_imp_manual, "mermas_proc": st.session_state.mermas_proc_manual,
        "imp_fijo": imp_fijo_pvp, "margen": margen, "cantidades": lista_cants, 
        "tiempo_manipulacion": t_input, "dificultad": dif_ud, "unidad_manipulacion": unidad_t
    }
    st.download_button("💾 Guardar Proyecto", json.dumps(datos_exp, indent=4), file_name=nombre_archivo)

# --- 5. ENTRADA DE DATOS ---
if not modo_comercial:
    st.header("1. Definición Técnica de Formas")
    c_btns = st.columns([1, 4])
    if c_btns[0].button("➕ Forma"):
        nid = max(st.session_state.piezas_dict.keys()) + 1
        st.session_state.piezas_dict[nid] = crear_forma_vacia(nid); st.rerun()
    if c_btns[1].button("🗑 Reiniciar Todo"):
        st.session_state.piezas_dict = {0: crear_forma_vacia(0)}; st.session_state.lista_extras_grabados = []
        st.session_state.costes_embalaje_manual = {}; st.session_state.mermas_imp_manual = {}; st.session_state.mermas_proc_manual = {}; st.rerun()

    # --- CALLBACKS ---
    def callback_cambio_frontal(pid):
        new_mat = st.session_state[f"pf_{pid}"]
        if new_mat != "Ninguno":
            st.session_state[f"gf_{pid}"] = PRECIOS["cartoncillo"][new_mat]["gramaje"]
            st.session_state[f"im_{pid}"] = "Offset"
            st.session_state[f"nt_{pid}"] = 4
        else:
            st.session_state[f"im_{pid}"] = "No"
            st.session_state[f"nt_{pid}"] = 0

    def callback_cambio_dorso(pid):
        new_mat = st.session_state[f"pd_{pid}"]
        if new_mat != "Ninguno":
            st.session_state[f"gd_{pid}"] = PRECIOS["cartoncillo"][new_mat]["gramaje"]

    def callback_medida_estandar(pid):
        fmt = st.session_state[f"std_{pid}"]
        if fmt != "Personalizado":
            nh, nw = FORMATOS_STD[fmt]
            st.session_state[f"h_{pid}"] = nh
            st.session_state[f"w_{pid}"] = nw

    for p_id, p in st.session_state.piezas_dict.items():
        with st.expander(f"🛠 {p.get('nombre', 'Forma')} - {p.get('h',0)}x{p.get('w',0)} mm", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                p['nombre'] = st.text_input("Etiqueta", p.get('nombre', f"Forma {p_id+1}"), key=f"n_{p_id}")
                p['pliegos'] = st.number_input("Pliegos/Ud", 0.0, 100.0, float(p.get('pliegos', 1.0)), key=f"p_{p_id}")
                
                st.selectbox("Medidas Estándar", list(FORMATOS_STD.keys()), key=f"std_{p_id}", 
                             on_change=callback_medida_estandar, args=(p_id,))

                p['h'] = st.number_input("Largo mm", 0, 5000, key=f"h_{p_id}", value=int(p.get('h', 0)))
                p['w'] = st.number_input("Ancho mm", 0, 5000, key=f"w_{p_id}", value=int(p.get('w', 0)))
                
                opts_im = ["Offset", "Digital", "No"]
                val_im = p.get('im', 'No'); idx_im = opts_im.index(val_im) if val_im in opts_im else 2
                p['im'] = st.selectbox("Sistema Cara", opts_im, index=idx_im, key=f"im_{p_id}")
                
                if p['im'] == "Offset":
                    p['nt'] = st.number_input("Tintas F.", 0, 6, int(p.get('nt',4)), key=f"nt_{p_id}")
                    p['ba'] = st.checkbox("Barniz F.", p.get('ba',False), key=f"ba_{p_id}")
                elif p['im'] == "Digital": p['ld'] = st.checkbox("Laminado Digital F.", p.get('ld',False), key=f"ld_{p_id}")
                
                opts_pel = list(PRECIOS["peliculado"].keys())
                val_pel = p.get('pel', 'Sin Peliculado'); idx_pel = opts_pel.index(val_pel) if val_pel in opts_pel else 0
                p['pel'] = st.selectbox("Peliculado Cara", opts_pel, index=idx_pel, key=f"pel_{p_id}")

            with col2:
                opts_pf = list(PRECIOS["cartoncillo"].keys())
                val_pf = p.get('pf', 'Ninguno'); idx_pf = opts_pf.index(val_pf) if val_pf in opts_pf else 0 
                p['pf'] = st.selectbox("C. Frontal", opts_pf, index=idx_pf, key=f"pf_{p_id}", 
                                       on_change=callback_cambio_frontal, args=(p_id,))
                
                p['gf'] = st.number_input("Gramaje F.", value=int(p.get('gf', 0)), key=f"gf_{p_id}")
                
                opts_pl = list(PRECIOS["planchas"].keys())
                val_pl = p.get('pl', 'Ninguna'); idx_pl = opts_pl.index(val_pl) if val_pl in opts_pl else 0
                p['pl'] = st.selectbox("Plancha Base", opts_pl, index=idx_pl, key=f"pl_{p_id}")
                
                opts_ap = ["C/C", "B/C", "B/B"]
                val_ap = p.get('ap', 'B/C'); idx_ap = opts_ap.index(val_ap) if val_ap in opts_ap else 1
                p['ap'] = st.selectbox("Calidad", opts_ap, index=idx_ap, key=f"ap_{p_id}")
                
                opts_pd = list(PRECIOS["cartoncillo"].keys())
                val_pd = p.get('pd', 'Ninguno'); idx_pd = opts_pd.index(val_pd) if val_pd in opts_pd else 0
                p['pd'] = st.selectbox("C. Dorso", opts_pd, index=idx_pd, key=f"pd_{p_id}", 
                                       on_change=callback_cambio_dorso, args=(p_id,))
                
                if p['pd'] != "Ninguno": p['gd'] = st.number_input("Gramaje D.", value=int(p.get('gd',0)), key=f"gd_{p_id}")
            
            with col3:
                opts_cor = ["Troquelado", "Plotter"]
                val_cor = p.get('cor', 'Troquelado'); idx_cor = opts_cor.index(val_cor) if val_cor in opts_cor else 0
                p['cor'] = st.selectbox("Corte", opts_cor, index=idx_cor, key=f"cor_{p_id}")
                
                if p['cor'] == "Troquelado": 
                    p['cobrar_arreglo'] = st.checkbox("¿Cobrar Arreglo?", value=p.get('cobrar_arreglo', True), key=f"arr_{p_id}")
                    p['pv_troquel'] = st.number_input("Precio Venta Troquel (€)", value=float(p.get('pv_troquel', 0.0)), key=f"pvt_{p_id}")
                
                if p['pd'] != "Ninguno":
                    opts_imd = ["Offset", "Digital", "No"]
                    val_imd = p.get('im_d', 'No'); idx_imd = opts_imd.index(val_imd) if val_imd in opts_imd else 2
                    p['im_d'] = st.selectbox("Sistema Dorso", opts_imd, index=idx_imd, key=f"imd_{p_id}")
                    
                    if p['im_d'] == "Offset":
                        p['nt_d'] = st.number_input("Tintas D.", 0, 6, int(p.get('nt_d',0)), key=f"ntd_{p_id}")
                        p['ba_d'] = st.checkbox("Barniz D.", p.get('ba_d',False), key=f"bad_{p_id}")
                    elif p['im_d'] == "Digital": p['ld_d'] = st.checkbox("Laminado Digital D.", p.get('ld_d',False), key=f"ldd_{p_id}")
                    
                    val_peld = p.get('pel_d', 'Sin Peliculado'); idx_peld = opts_pel.index(val_peld) if val_peld in opts_pel else 0
                    p['pel_d'] = st.selectbox("Peliculado Dorso", opts_pel, index=idx_peld, key=f"peld_{p_id}")
                
                if st.button("🗑 Borrar Forma", key=f"del_{p_id}"): del st.session_state.piezas_dict[p_id]; st.rerun()

    st.divider(); st.subheader("📦 2. Almacén de Accesorios")
    opts_extra = ["---"] + list(PRECIOS["extras_base"].keys())
    ex_sel = st.selectbox("Añadir extra:", opts_extra)
    
    if st.button("➕ Añadir Accesorio") and ex_sel != "---":
        st.session_state.lista_extras_grabados.append({"nombre": ex_sel, "coste": PRECIOS["extras_base"][ex_sel], "cantidad": 1.0}); st.rerun()
    for i, ex in enumerate(st.session_state.lista_extras_grabados):
        ca, cb, cc, cd = st.columns([3, 2, 2, 1]); ca.write(f"**{ex['nombre']}**"); ex['coste'] = cb.number_input("€/ud compra", value=float(ex['coste']), key=f"exc_{i}"); ex['cantidad'] = cc.number_input("Cant/Ud prod", value=float(ex['cantidad']), key=f"exq_{i}")
        if cd.button("🗑", key=f"exd_{i}"): st.session_state.lista_extras_grabados.pop(i); st.rerun()

    st.divider(); st.subheader("📦 3. Embalaje Manual")
    st.info("Introduce el coste de compra UNITARIO (por caja/unidad) para cada cantidad.")
    if lista_cants:
        cols_emb = st.columns(len(lista_cants))
        for i, q in enumerate(lista_cants):
            current_val = st.session_state.costes_embalaje_manual.get(q, 0.0)
            val = cols_emb[i].number_input(f"Coste UNITARIO Compra {q} uds (€)", value=float(current_val), format="%.4f", key=f"emb_man_{q}")
            st.session_state.costes_embalaje_manual[q] = val
    else: st.warning("Define primero las cantidades en el panel lateral.")

    # --- SECCIÓN 4: MERMAS MANUALES DETALLADAS ---
    st.divider()
    st.subheader("⚙️ 4. Gestión de Mermas (Manual)")
    
    tiene_dig = any(pz["im"] == "Digital" or pz.get("im_d") == "Digital" for pz in st.session_state.piezas_dict.values())
    
    if lista_cants:
        for q in lista_cants:
            # --- USO CONTAINER PARA FORZAR CAMBIO VISUAL ---
            with st.container(border=True):
                c_lbl, c_imp, c_proc = st.columns([1, 2, 2])
                
                c_lbl.markdown(f"### 📦 {q} uds")
                
                std_proc, std_imp = calcular_mermas_estandar(q, tiene_dig)
                
                # Recuperar
                curr_imp = st.session_state.mermas_imp_manual.get(q, std_imp)
                curr_proc = st.session_state.mermas_proc_manual.get(q, std_proc)
                
                # Inputs con keys únicas
                val_imp = c_imp.number_input(f"🖨️ Arranque (Hojas)", value=int(curr_imp), key=f"mi_{q}", help="Hojas fijas de puesta a punto")
                val_proc = c_proc.number_input(f"⚙️ Rodaje (Unidades)", value=int(curr_proc), key=f"mp_{q}", help="Piezas perdidas durante el proceso")
                
                st.session_state.mermas_imp_manual[q] = val_imp
                st.session_state.mermas_proc_manual[q] = val_proc
                
                # Resumen visual
                p_ejemplo = list(st.session_state.piezas_dict.values())[0] if st.session_state.piezas_dict else {'pliegos': 1}
                total_hojas_extra = val_imp + (val_proc * p_ejemplo['pliegos'])
                st.caption(f"Total desperdicio estimado: {total_hojas_extra:.0f} hojas de papel extra.")
    else: st.warning("Define primero las cantidades en el panel lateral.")

# --- 6. MOTOR DE CÁLCULO ---
res_final, desc_full = [], {}
if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
    total_pv_troqueles = sum(float(pz.get('pv_troquel', 0.0)) for pz in st.session_state.piezas_dict.values())
    
    for q_n in lista_cants:
        tiene_dig = any(pz["im"] == "Digital" or pz.get("im_d") == "Digital" for pz in st.session_state.piezas_dict.values())
        
        merma_imp_hojas = st.session_state.mermas_imp_manual.get(q_n, 0)
        merma_proc_unidades = st.session_state.mermas_proc_manual.get(q_n, 0)
        
        # CANTIDAD TALLER = Cantidad Neta + Merma Procesos
        qp_taller = q_n + merma_proc_unidades

        coste_f, det_f = 0.0, []
        
        for p_id, p in st.session_state.piezas_dict.items():
            nb = q_n * p["pliegos"]
            
            # --- CÁLCULO PRECISO DE HOJAS ---
            # 1. Hojas Netas
            hojas_netas = nb
            
            # 2. Hojas por Merma Procesos (Unidades * Pliegos)
            waste_proc_hojas = merma_proc_unidades * p["pliegos"]
            
            # 3. Hojas por Merma Impresión (Fijas arranque)
            waste_imp_hojas = merma_imp_hojas 
            
            # TOTAL HOJAS COMPRA
            hc_f = hojas_netas + waste_proc_hojas + waste_imp_hojas
            hc_d = hc_f 
            
            # Hojas Pasada (Impresión/Acabados): Todo lo que se compra se pasa por máquina
            hp = hc_f 
            
            debug_merma = f"Imp: {waste_imp_hojas} hojas | Proc: {merma_proc_unidades} uds ({waste_proc_hojas:.1f} hojas)"

            m2 = (p["w"]*p["h"])/1_000_000
            
            c_cf = (hc_f * m2 * (p.get('gf',0)/1000) * PRECIOS["cartoncillo"][p["pf"]]["precio_kg"])
            c_cd = (hc_d * m2 * (p.get('gd',0)/1000) * PRECIOS["cartoncillo"][p.get('pd','Ninguno')]["precio_kg"])
            c_pla, c_peg = 0.0, 0.0
            
            if p["pl"] != "Ninguna":
                c_pla = hp * m2 * PRECIOS["planchas"][p["pl"]][p.get('ap','C/C')]
                pas = (1 if p["pf"]!="Ninguno" else 0) + (1 if p.get('pd','Ninguno')!="Ninguno" else 0)
                c_peg = hp * m2 * PRECIOS["planchas"][p["pl"]]["peg"] * pas
            elif p["pf"] != "Ninguno" and p.get('pd', 'Ninguno') != "Ninguno":
                c_peg = hp * m2 * PRECIOS["planchas"]["Microcanal / Canal 3"]["peg"] * 1

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
            
            s_imp = c_if + c_id; s_narba = c_pel_f + c_pel_d + c_peg + c_arr + c_tir; s_mat = c_cf + c_pla + c_cd
            sub = s_imp + s_narba + s_mat; coste_f += sub
            det_f.append({
                "Pieza": p["nombre"], "Mat. Frontal": c_cf, "Mat. Dorso": c_cd, "Mat. Ondulado": c_pla,
                "Imp. Cara": c_if, "Imp. Dorso": c_id, "Acab. Peliculado": c_pel_f + c_pel_d, 
                "Acab. Contracolado": c_peg, "Acab. Troquel/Corte": c_arr + c_tir,
                "Total Imp": s_imp, "Total Narba": s_narba, "Total Mat": s_mat, "Subtotal": sub,
                "_debug": debug_merma
            })

        c_ext_tot = sum(e["coste"] * e["cantidad"] * qp_taller for e in st.session_state.lista_extras_grabados)
        c_mo = ((seg_man_total/3600)*18*qp_taller) + (qp_taller*dif_ud)
        
        coste_emb_unit_compra = st.session_state.costes_embalaje_manual.get(q_n, 0.0)
        pv_emb_ud = coste_emb_unit_compra * 1.4
        pv_emb_total = pv_emb_ud * q_n
        
        pvp_producto_base = ((coste_f + c_ext_tot + c_mo) * margen) + imp_fijo_pvp
        pvp_total_todo = pvp_producto_base + pv_emb_total + total_pv_troqueles
        p_venta_unitario = pvp_producto_base / q_n if q_n > 0 else 0
        p_total_unitario_all = pvp_total_todo / q_n if q_n > 0 else 0

        res_final.append({
            "Cantidad": q_n, "Precio Venta Unitario": f"{p_venta_unitario:.3f}€",
            "Precio Embalaje Unitario": f"{pv_emb_ud:.3f}€", "Precio Troquel (Total)": f"{total_pv_troqueles:.2f}€",
            "Precio Venta Total": f"{pvp_total_todo:.2f}€", "Unitario (Todo Incluido)": f"{p_total_unitario_all:.3f}€"
        })
        desc_full[q_n] = {"det": det_f, "mo": c_mo, "extras": c_ext_tot, "fijo": imp_fijo_pvp, "taller": coste_f + c_mo + c_ext_tot, "qp": qp_taller, 
                          "m_imp": merma_imp_hojas, "m_proc": merma_proc_unidades}

# --- 7. SALIDA VISUAL ---
if modo_comercial and res_final:
    desc_html = """<div style='text-align: left; margin-bottom: 20px; color: #444;'>
    <h4 style='color: #1E88E5; margin-bottom: 5px;'>📋 Especificaciones del Proyecto</h4>
    <ul style='list-style-type: none; padding-left: 0;'>"""
    for p in st.session_state.piezas_dict.values():
        mat_f = f"<b>Frontal:</b> {p['pf']} ({p.get('gf',0)}g)" if p['pf'] != "Ninguno" else ""
        mat_d = f" | <b>Dorso:</b> {p['pd']} ({p.get('gd',0)}g)" if p.get('pd', "Ninguno") != "Ninguno" else ""
        mat_pl = f" | <b>Base:</b> {p['pl']}" if p.get('pl', "Ninguna") != "Ninguna" else ""
        
        info_imp = ""
        if p['im'] == "Offset": info_imp = f" | <b>Imp:</b> Offset {p['nt']} tintas" + (" + Barniz" if p['ba'] else "")
        elif p['im'] == "Digital": info_imp = " | <b>Imp:</b> Digital"
        info_pliegos = f" | <b>Pliegos/Ud:</b> {p['pliegos']}" if p['pliegos'] != 1 else ""
        
        detalles_mat = mat_f + mat_d + mat_pl + info_imp + info_pliegos
        if not detalles_mat: detalles_mat = "Sin materiales definidos"
        desc_html += f"<li style='margin-bottom: 8px;'>🔹 <b>{p['nombre']}</b> ({p['h']}x{p['w']} mm)<br><span style='font-size:0.9em; color:#666; margin-left: 20px;'>{detalles_mat}</span></li>"
    if st.session_state.lista_extras_grabados:
        desc_html += "<li style='margin-top: 10px;'><b>🧩 Accesorios:</b> "
        items_acc = [f"{ex['nombre']} (x{int(ex['cantidad']) if ex['cantidad'].is_integer() else ex['cantidad']})" for ex in st.session_state.lista_extras_grabados]
        desc_html += ", ".join(items_acc) + "</li>"
    desc_html += "</ul></div>"

    rows_html = ""
    for r in res_final:
        rows_html += f"""<tr><td style='font-weight:bold;'>{r['Cantidad']}</td><td>{r['Precio Venta Unitario']}</td><td>{r['Precio Embalaje Unitario']}</td><td>{r['Precio Troquel (Total)']}</td><td style='background-color: #f0f8ff;'>{r['Precio Venta Total']}</td><td style='font-weight:bold; color: #1E88E5;'>{r['Unitario (Todo Incluido)']}</td></tr>"""

    st.markdown(f"""
    <div class="comercial-box"><h2 class="comercial-header">OFERTA COMERCIAL - {st.session_state.cli}</h2>
        <p class="comercial-ref">Ref. Briefing: {st.session_state.brf}</p>{desc_html}
        <table class="comercial-table"><tr><th>Cantidad</th><th>P. Venta Unitario</th><th>P. Emb. Unitario</th><th>Troqueles (Total)</th><th>PRECIO VENTA TOTAL</th><th>UNITARIO (TODO)</th></tr>{rows_html}</table>
        <p style='text-align: right; font-size: 0.9em; color: #777; margin-top: 15px;'>* Oferta válida salvo error tipográfico. IVA no incluido.</p>
    </div>""", unsafe_allow_html=True)

else:
    if res_final:
        st.header(f"📊 Resumen de Venta: {st.session_state.cli}")
        st.dataframe(pd.DataFrame(res_final), use_container_width=True)
        
        for q, info in desc_full.items():
            with st.expander(f"🔍 Auditoría Taller {q} uds (Taller: {info['qp']} uds)"):
                
                # --- VISUALIZACIÓN CRISTALINA DE MERMAS ---
                st.info(f"""
                **CONTROL DE MERMAS:**
                \n🔹 **Arranque Impresión:** {info['m_imp']} hojas fijas (Se tiran al inicio)
                \n🔹 **Merma Procesos:** {info['m_proc']} unidades perdidas en taller
                \n✅ **Total a Manipular (Taller):** {q} + {info['m_proc']} = **{info['qp']} unidades**
                """)

                df_raw = pd.DataFrame(info["det"])
                cols_order = ["Pieza", "Mat. Frontal", "Mat. Dorso", "Mat. Ondulado", "Total Mat", "Imp. Cara", "Imp. Dorso", "Total Imp", "Acab. Peliculado", "Acab. Contracolado", "Acab. Troquel/Corte", "Total Narba", "Subtotal"]
                cols_final = [c for c in cols_order if c in df_raw.columns]
                
                df_sorted = df_raw[cols_final]
                
                row_mo = {c: 0 for c in cols_final[1:]}; row_mo["Pieza"] = "MANO DE OBRA (Manipulado)"; row_mo["Subtotal"] = info['mo']
                row_ext = {c: 0 for c in cols_final[1:]}; row_ext["Pieza"] = "MATERIALES EXTRA (Accesorios)"; row_ext["Subtotal"] = info['extras']
                
                df_audit = pd.concat([df_sorted, pd.DataFrame([row_mo, row_ext])], ignore_index=True)
                
                sum_row = {"Pieza": "TOTAL COSTE INDUSTRIAL"}
                for col in cols_final[1:]: sum_row[col] = df_audit[col].sum()
                
                df_final = pd.concat([df_audit, pd.DataFrame([sum_row])], ignore_index=True)

                st.table(df_final.style.format("{:.2f}€", subset=df_final.columns[1:])
                         .set_properties(**{'background-color': '#e3f2fd', 'font-weight': 'bold'}, subset=["Total Imp","Total Narba","Total Mat","Subtotal"])
                         .set_properties(**{'color': '#666'}, subset=["Mat. Frontal", "Mat. Dorso", "Mat. Ondulado", "Imp. Cara", "Imp. Dorso", "Acab. Peliculado", "Acab. Contracolado", "Acab. Troquel/Corte"]))
                
                st.metric("COSTO TALLER (Sin Margen)", f"{info['taller']:.2f}€")
