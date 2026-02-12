import streamlit as st
import pandas as pd
import json
import re

# --- 1. BASE DE DATOS FLEXICO (TARIFA 2024 COMPLETA) ---
PRODUCTOS_FLEXICO = {
    "172018": {"desc": "GANCHO EXTENSIBLE MAXI 0,5kg", "precio": 0.0397},
    "137018": {"desc": "PORTAETIQUETA GANCHO 28x30 mm", "precio": 0.0742},
    "142201": {"desc": "GANCHO PERFORANTE SIMPLE 200mm", "precio": 0.1480},
    "142203": {"desc": "GANCHO PERFORANTE SIMPLE 150mm", "precio": 0.1290},
    "142205": {"desc": "GANCHO PERFORANTE SIMPLE 100mm", "precio": 0.1080},
    "142206": {"desc": "GANCHO PERFORADOR SIMPLE 5 CM", "precio": 0.1530},
    "142412": {"desc": "GANCHO PERFORANTE DOBLE 100mm", "precio": 0.1260},
    "142413": {"desc": "GANCHO PERFORANTE DOBLE 150mm", "precio": 0.1280},
    "142414": {"desc": "PERFORANTE DOBLE 200mm GANCHO", "precio": 0.1710},
    "142415": {"desc": "PERFORANTE DOBLE 250mm GANCHO", "precio": 0.1800},
    "142422": {"desc": "GANCHO PERFO DOBLE NEGRO 100mm", "precio": 0.1020},
    "142424": {"desc": "GANCHO PERFO DOBLE NEGRO 200mm", "precio": 0.1880},
    "145104": {"desc": "TIRA CROSS MERCH METALICA", "precio": 3.1100},
    "145110": {"desc": "TIRA CROSS MERCH-740 MM", "precio": 0.3310},
    "145150": {"desc": "PINZA PARA CROSS-MERCHANDISING", "precio": 0.1072},
    "172594": {"desc": "ANILLA LLAVERO - 20 MM", "precio": 0.0600},
    "262041": {"desc": "SUJETADOR PERFIL PP 30-40mm", "precio": 0.0500},
    "752012": {"desc": "BISTUCADOR Ø12mm CIER14mm NEGR", "precio": 0.0400},
    "752013": {"desc": "BISTUCADOR Ø12mm CIER14mm TRSP", "precio": 0.0410},
    "752015": {"desc": "BISTUCADOR Ø12mm CIER7mm TRSP", "precio": 0.0370},
    "753007": {"desc": "SOP PORTACARTEL ADH TRSP 56X25", "precio": 0.1770},
    "792010": {"desc": "GANCHO SUSPENSION + HILO 1,2m", "precio": 0.1160},
    "792032": {"desc": "HILO NYLON- BOBINA 200M", "precio": 5.4800},
    "792071": {"desc": "TWISTER METAL 2 ADH 75mm", "precio": 0.0538},
    "792301": {"desc": "BASE DE PLAS EXPOSITOR TRSP", "precio": 0.1840},
    "792421": {"desc": "GANCHO S METAL 24MM DIAM 2MM", "precio": 0.0215},
    "792425": {"desc": "ESSE 32MM BOUCLE DIA 6 & 14MM", "precio": 0.0360},
    "792427": {"desc": "GANCHO S METAL30MM DIAM 2MM", "precio": 0.0267},
    "792432": {"desc": "GANCHO S 36 MM 014", "precio": 0.0300},
    "792436": {"desc": "GANCHO S METAL ASYMETRICO 45MM", "precio": 0.0394},
    "792437": {"desc": "GANCHO S METAL ASYMETRICO 40MM", "precio": 0.0428},
    "792451": {"desc": "GANCHO S METAL 59MM DIAM 2MM", "precio": 0.0365},
    "792452": {"desc": "GANCHO S METAL 65MM DIAM 2,5MM", "precio": 0.0540},
    "792542": {"desc": "TWISTER PET 75MM-2 ADHESIVOS", "precio": 0.0460},
    "792546": {"desc": "WOBBLER PET 150MM 2 ADH", "precio": 0.0411},
    "792550": {"desc": "WOBBLER PET 150MM 2 ADH REMOV", "precio": 0.0613},
    "792570": {"desc": "MEGA TWISTER METAL 2 ADH", "precio": 0.0897},
    "792571": {"desc": "TWISTER METAL 2 ADH", "precio": 0.0400},
    "792573": {"desc": "TWISTER METAL 3 ADH", "precio": 0.0543},
    "792582": {"desc": "TWISTER MET 75MM 2 ADH EN HOJA", "precio": 0.0600},
    "793075": {"desc": "TWISTER 2 ADH CLEAN", "precio": 0.0650},
    "793240": {"desc": "1100 ALMOH AUTOADH MACHO-19mm", "precio": 15.6000},
    "793242": {"desc": "1100 ALMOH AUTOADH HEMBRA-19mm", "precio": 15.6000},
    "793249": {"desc": "1500ALMOH AUTOAD HEMBR 13 NEGR", "precio": 11.8000},
    "793250": {"desc": "1500ALMOH AUTOAD MACH 13 NEGR", "precio": 11.8000},
    "793301": {"desc": "PLETINA PVC ADH 20X20mm", "precio": 0.0382},
    "793303": {"desc": "PLETINA PVC ADH 20X40mm", "precio": 0.0680},
    "796007": {"desc": "TORNILLO Ø15mm MAXI 9mm BLCO", "precio": 0.0299},
    "796043": {"desc": "TORNILLO Ø28mm MAXI 22mm BLCO", "precio": 0.0534},
    "796307": {"desc": "TORNILLO Ø 15mm MAXI 9mm NEGRO", "precio": 0.0300},
    "796309": {"desc": "TORNILLO Ø28mm MAXI 15mm NEGRO", "precio": 0.0320},
    "796343": {"desc": "TORNILLO Ø28mm MAXI 22mm NEGRO", "precio": 0.0525},
    "796407": {"desc": "TORNILLO Ø15mm MAXI 9mm TRSP", "precio": 0.0294},
    "796409": {"desc": "TORNILLO Ø28 mm MAXI15 mm TRSP", "precio": 0.0325},
    "796443": {"desc": "TORNILLO Ø 28mm MAXI 22mm TRSP", "precio": 0.0570},
    "796445": {"desc": "TORNILLO Ø 28mm MAXI 38mm TRSP", "precio": 0.0597},
    "797133": {"desc": "GRIPADOR 2 ENTRADAS EN L 25mm", "precio": 0.0579},
    "797148": {"desc": "GRIPADOR T13mm LG 76mm ADH", "precio": 0.0821},
    "797150": {"desc": "GRIPADOR T 28mm LG 25mm ADH", "precio": 0.0398},
    "797193": {"desc": "GRIPADOR 2 ENTRADAS EN J", "precio": 0.1080},
    "797786": {"desc": "PINZA MULTI ANGULO", "precio": 0.1460},
    "797885": {"desc": "BRIDA NYLON 300MM", "precio": 0.0434},
    "797910": {"desc": "PISTOLA", "precio": 10.5000},
    "797911": {"desc": "SET DE 5 AGUJERAS", "precio": 7.8000},
    "797915": {"desc": "ATADURAS NYLON 40MM", "precio": 0.0020},
    "797917": {"desc": "ATADURAS NYLON 65MM", "precio": 0.0024},
    "797921": {"desc": "ATADURAS EXTR ESTR 125mm", "precio": 0.0037},
    "841201": {"desc": "PESCANTE MULTIMAG", "precio": 1.8000},
    "841211": {"desc": "PESCANTE MULTIMAG PLUS", "precio": 1.9400},
    "950101": {"desc": "GANCHO FONDO PERF SIMPLE 50MM", "precio": 0.1384},
    "950235": {"desc": "CABLE ACIER ANTIRROBO PLACA", "precio": 2.6000},
    "950341": {"desc": "PORTA VISUAL BASE MADERA - A5", "precio": 5.5000},
    "950790": {"desc": "SUPER VENTOSA CON TORNILLON", "precio": 3.0100},
    "142002": {"desc": "GANCHO UNIVERSAL SIMPLE 100mm", "precio": 0.1101},
    "145101": {"desc": "TIRA CROSS MERCH DBLE FLJ 780", "precio": 0.4424},
    "145103": {"desc": "TIRA CROSS MERCH PNZA METL 790", "precio": 2.3700},
    "145111": {"desc": "TIRA CROSSMERCH 600 PE85X100mm", "precio": 0.2830},
    "163401": {"desc": "PINZA PORTA ETIQ ARTICUL TRSP", "precio": 0.3474},
    "172012": {"desc": "GANCHO SUSPENSION +HILO 1,2M", "precio": 0.1500},
    "172078": {"desc": "GANCHO DOBLE METALICO 300mm", "precio": 0.0690},
    "950221": {"desc": "BASE GIRATORIA Ø 150 MM", "precio": 1.9400}
}
OPCIONES_FLEXICO = [f"{k} - {v['desc']}" for k, v in PRODUCTOS_FLEXICO.items()]

# --- 2. BASE DE DATOS INICIAL (PRECIOS POR DEFECTO) ---
PRECIOS_BASE = {
    "cartoncillo": {
        "Ninguno": {"precio_kg": 0.0, "gramaje": 0},
        "Reverso Gris": {"precio_kg": 0.93, "gramaje": 220},
        "Zenith": {"precio_kg": 1.55, "gramaje": 350},
        "Reverso Madera": {"precio_kg": 0.95, "gramaje": 400},
        "Folding Kraft": {"precio_kg": 1.90, "gramaje": 340},
        "Folding Blanco": {"precio_kg": 1.82, "gramaje": 350}
    },
    "planchas": {
        "Ninguna": {"C/C": 0.0, "peg": 0.0},
        "Microcanal / Canal 3": {"C/C": 0.659, "B/C": 0.672, "B/B": 0.758, "peg": 0.217},
        "Doble Micro / Doble Doble": {"C/C": 1.046, "B/C": 1.1, "B/B": 1.276, "peg": 0.263},
        "AC (Cuero/Cuero)": {"C/C": 2.505, "peg": 0.217}
    },
    "peliculado": {
        "Sin Peliculado": 0.0, 
        "Polipropileno": 0.26, 
        "Poliéster brillo": 0.38, 
        "Poliéster mate": 0.64
    },
    "laminado_digital": 3.5,
    "extras_base": {
        "CINTA D/CARA": 0.26, "CINTA LOHMAN": 0.49, "CINTA GEL": 1.2,
        "GOMA TERMINALES": 0.079, "IMAN 20x2mm": 1.145, "TUBOS": 1.06,
        "REMACHES": 0.049, "VELCRO": 0.43, "PUNTO ADHESIVO": 0.08
    },
    "troquelado": {
        "Pequeño (< 1000x700)": {"arranque": 48.19, "tiro": 0.06},
        "Mediano (Estándar)":   {"arranque": 80.77, "tiro": 0.09},
        "Grande (> 1000x700)":  {"arranque": 107.80, "tiro": 0.135}
    },
    "plotter": {
        "precio_hoja": 2.03
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
    if es_digital: return int(n * 0.02), 10 
    if n < 100: return 10, 150
    if n < 200: return 20, 175
    if n < 600: return 30, 200
    if n < 1000: return 40, 220
    if n < 2000: return 50, 250
    return int(n*0.03), 300

# --- 3. INICIALIZACIÓN ---
st.set_page_config(page_title="MAINSA ADMIN V28", layout="wide")

if 'db_precios' not in st.session_state:
    st.session_state.db_precios = PRECIOS_BASE.copy()

def crear_forma_vacia(index):
    return {
        "nombre": f"Forma {index + 1}", "pliegos": 1.0, "w": 0, "h": 0, 
        "pf": "Ninguno", "gf": 0, "pl": "Ninguna", 
        "ap": "B/C", "pd": "Ninguno", "gd": 0, 
        "im": "No", "nt": 0, "ba": False, 
        "im_d": "No", "nt_d": 0, "ba_d": False, "pel": "Sin Peliculado", 
        "pel_d": "Sin Peliculado", "ld": False, "ld_d": False, 
        "cor": "Troquelado", "cobrar_arreglo": True, "pv_troquel": 0.0,
        # NUEVOS CAMPOS V27 (Plancha diferente)
        "pl_dif": False, "pl_h": 0, "pl_w": 0 
    }

if 'piezas_dict' not in st.session_state: st.session_state.piezas_dict = {0: crear_forma_vacia(0)}
if 'lista_extras_grabados' not in st.session_state: st.session_state.lista_extras_grabados = []
if 'costes_embalaje_manual' not in st.session_state: st.session_state.costes_embalaje_manual = {}
if 'mermas_imp_manual' not in st.session_state: st.session_state.mermas_imp_manual = {}
if 'mermas_proc_manual' not in st.session_state: st.session_state.mermas_proc_manual = {}
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# Variables para embalaje automático
if 'emb_tipo' not in st.session_state: st.session_state.emb_tipo = "Manual"
if 'emb_dims' not in st.session_state: st.session_state.emb_dims = {"L": 0, "W": 0, "H": 0}

st.markdown("""<style>
    .comercial-box { background-color: white; padding: 30px; border: 2px solid #1E88E5; border-radius: 10px; color: #333; }
    .comercial-header { color: #1E88E5; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 5px; }
    .comercial-ref { text-align: center; color: #555; font-size: 1.1em; margin-bottom: 25px; font-weight: bold; }
    .comercial-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 1.1em; }
    .comercial-table th { background-color: #1E88E5; color: white; padding: 10px; }
    .comercial-table td { padding: 10px; border: 1px solid #ddd; text-align: center; }
</style>""", unsafe_allow_html=True)

st.title("🛡️ PANEL ADMIN - ESCANDALLO")

# --- BARRA LATERAL (PRIMERO) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    pwd = st.text_input("🔑 Contraseña Admin", type="password")
    if pwd == "mainsa2024": 
        st.session_state.is_admin = True
        st.success("Modo Admin Activo")
    else: 
        st.session_state.is_admin = False
        if pwd: st.error("Contraseña incorrecta")
    
    st.divider()
    with st.expander("🤖 Importar Datos", expanded=False):
        uploaded = st.file_uploader("Subir JSON", type=["json"])
        if uploaded:
            try:
                di = json.load(uploaded)
                if "cli" in di: st.session_state.cli = di["cli"]
                if "piezas" in di: st.session_state.piezas_dict = {int(k): v for k, v in di["piezas"].items()}
                if "extras" in di: st.session_state.lista_extras_grabados = di["extras"]
                st.rerun()
            except: pass

    st.session_state.brf = st.text_input("Nº Briefing", key="brf_input")
    st.session_state.cli = st.text_input("Cliente", key="cli_input")
    st.session_state.desc = st.text_input("Descripción", key="desc_input")
    st.divider()
    cants_str = st.text_input("Cantidades (ej: 500, 1000)", key="cants_input", value="0")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    
    unidad_t = st.radio("Manipulación:", ["Segundos", "Minutos"], horizontal=True)
    t_input = st.number_input("Tiempo/ud", key="t_input_widget")
    seg_man_total = t_input * 60 if unidad_t == "Minutos" else t_input
    
    if st.session_state.is_admin:
        st.divider()
        st.markdown("### 💰 Finanzas")
        dif_ud = st.selectbox("Dificultad (€/ud)", [0.02, 0.061, 0.091], index=2)
        imp_fijo_pvp = st.number_input("Fijo PVP (€)", value=500.0)
        margen = st.number_input("Multiplicador", step=0.1, value=2.2)
        modo_comercial = st.checkbox("🌟 VISTA OFERTA", value=False)
    else:
        dif_ud, imp_fijo_pvp, margen, modo_comercial = 0.091, 500.0, 2.2, False

# --- PESTAÑAS PRINCIPALES ---
# IMPORTANTE: Definimos las pestañas AQUÍ para que existan en todo el script
if st.session_state.is_admin:
    tab_calculadora, tab_costes, tab_debug = st.tabs(["🧮 Calculadora", "💰 Base de Datos de Costes", "🔍 Desglose de Cálculos"])
else:
    tab_calculadora, = st.tabs(["🧮 Calculadora Técnica"])
    tab_costes, tab_debug = None, None

# ==============================================================================
# PESTAÑA 2: GESTIÓN DE COSTES
# ==============================================================================
if tab_costes:
    with tab_costes:
        st.header("Gestión de Costes de Materia Prima y Procesos")
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            with st.expander("📄 Cartoncillo (Precio €/Kg)", expanded=True):
                for k, v in st.session_state.db_precios["cartoncillo"].items():
                    if k != "Ninguno":
                        nuevo_precio = st.number_input(f"{k} (€/kg)", value=float(v["precio_kg"]), format="%.3f", key=f"cost_cart_{k}")
                        st.session_state.db_precios["cartoncillo"][k]["precio_kg"] = nuevo_precio
            
            with st.expander("🧱 Planchas Ondulado (€/m²)", expanded=True):
                for k, v in st.session_state.db_precios["planchas"].items():
                    if k != "Ninguna":
                        st.markdown(f"**{k}**")
                        cols = st.columns(len(v))
                        for idx, (sub_k, sub_v) in enumerate(v.items()):
                            label = "Pegado" if sub_k == "peg" else f"Calidad {sub_k}"
                            nuevo_val = cols[idx].number_input(f"{label}", value=float(sub_v), format="%.3f", key=f"cost_pla_{k}_{sub_k}")
                            st.session_state.db_precios["planchas"][k][sub_k] = nuevo_val
                        st.divider()

        with col_c2:
            with st.expander("✨ Peliculado (€/m²)", expanded=True):
                for k, v in st.session_state.db_precios["peliculado"].items():
                    if k != "Sin Peliculado":
                        nuevo_p = st.number_input(f"{k}", value=float(v), format="%.3f", key=f"cost_pel_{k}")
                        st.session_state.db_precios["peliculado"][k] = nuevo_p
                st.divider()
                lam_dig = st.number_input("Laminado Digital (€/m²)", value=float(st.session_state.db_precios.get("laminado_digital", 3.5)), key="cost_lam_dig")
                st.session_state.db_precios["laminado_digital"] = lam_dig

            with st.expander("🔪 Troquelado (Arranque y Tiro)", expanded=True):
                if "troquelado" not in st.session_state.db_precios: st.session_state.db_precios["troquelado"] = PRECIOS_BASE["troquelado"]
                for k, v in st.session_state.db_precios["troquelado"].items():
                    st.markdown(f"**{k}**")
                    c_arr, c_tir = st.columns(2)
                    n_arr = c_arr.number_input(f"Arranque (€)", value=float(v["arranque"]), format="%.2f", key=f"trq_arr_{k}")
                    n_tir = c_tir.number_input(f"Tiro (€/hoja)", value=float(v["tiro"]), format="%.4f", key=f"trq_tir_{k}")
                    st.session_state.db_precios["troquelado"][k]["arranque"] = n_arr
                    st.session_state.db_precios["troquelado"][k]["tiro"] = n_tir
                    st.divider()

            with st.expander("✂️ Plotter de Corte", expanded=True):
                if "plotter" not in st.session_state.db_precios: st.session_state.db_precios["plotter"] = PRECIOS_BASE["plotter"]
                val_plot = st.number_input("Precio Corte (€/hoja)", value=float(st.session_state.db_precios["plotter"]["precio_hoja"]), format="%.3f", key="cost_plotter_base")
                st.session_state.db_precios["plotter"]["precio_hoja"] = val_plot

            with st.expander("🧩 Extras y Accesorios (€/ud)", expanded=False):
                for k, v in st.session_state.db_precios["extras_base"].items():
                    nuevo_e = st.number_input(f"{k}", value=float(v), format="%.4f", key=f"cost_ext_{k}")
                    st.session_state.db_precios["extras_base"][k] = nuevo_e

# ==============================================================================
# PESTAÑA 1: CALCULADORA
# ==============================================================================
with tab_calculadora:
    # --- ENTRADA DE DATOS FORMULARIO ---
    if not modo_comercial:
        st.header("1. Definición Técnica de Formas")
        c_btns = st.columns([1, 4])
        if c_btns[0].button("➕ Forma"):
            nid = max(st.session_state.piezas_dict.keys()) + 1
            st.session_state.piezas_dict[nid] = crear_forma_vacia(nid); st.rerun()
        if c_btns[1].button("🗑 Reiniciar Todo"):
            st.session_state.piezas_dict = {0: crear_forma_vacia(0)}; st.session_state.lista_extras_grabados = []
            st.session_state.costes_embalaje_manual = {}; st.session_state.mermas_imp_manual = {}; st.session_state.mermas_proc_manual = {}; st.rerun()

        # CALLBACKS
        def callback_cambio_frontal(pid):
            new_mat = st.session_state[f"pf_{pid}"]
            if new_mat != "Ninguno":
                st.session_state[f"gf_{pid}"] = st.session_state.db_precios["cartoncillo"][new_mat]["gramaje"]
                st.session_state[f"im_{pid}"] = "Offset"; st.session_state[f"nt_{pid}"] = 4
            else:
                st.session_state[f"im_{pid}"] = "No"; st.session_state[f"nt_{pid}"] = 0
        def callback_cambio_dorso(pid):
            new_mat = st.session_state[f"pd_{pid}"]
            if new_mat != "Ninguno": st.session_state[f"gd_{pid}"] = st.session_state.db_precios["cartoncillo"][new_mat]["gramaje"]
        def callback_medida_estandar(pid):
            fmt = st.session_state[f"std_{pid}"]
            if fmt != "Personalizado":
                nh, nw = FORMATOS_STD[fmt]
                st.session_state[f"h_{pid}"] = nh; st.session_state[f"w_{pid}"] = nw
                # Reset plancha si no es custom
                if not st.session_state.get(f"pldif_{pid}", False):
                     st.session_state[f"plh_{pid}"] = nh; st.session_state[f"plw_{pid}"] = nw

        for p_id, p in st.session_state.piezas_dict.items():
            with st.expander(f"🛠 {p.get('nombre', 'Forma')} - {p.get('h',0)}x{p.get('w',0)} mm", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    p['nombre'] = st.text_input("Etiqueta", p.get('nombre', f"Forma {p_id+1}"), key=f"n_{p_id}")
                    p['pliegos'] = st.number_input("Pliegos/Ud", 0.0, 100.0, float(p.get('pliegos', 1.0)), format="%.4f", key=f"p_{p_id}")
                    st.selectbox("Medidas Estándar", list(FORMATOS_STD.keys()), key=f"std_{p_id}", on_change=callback_medida_estandar, args=(p_id,))
                    
                    # MEDIDAS PAPEL (PRINCIPAL)
                    c_h, c_w = st.columns(2)
                    p['h'] = c_h.number_input("Largo Papel (mm)", 0, 5000, key=f"h_{p_id}", value=int(p.get('h', 0)))
                    p['w'] = c_w.number_input("Ancho Papel (mm)", 0, 5000, key=f"w_{p_id}", value=int(p.get('w', 0)))
                    
                    opts_im = ["Offset", "Digital", "No"]; val_im = p.get('im', 'No'); idx_im = opts_im.index(val_im) if val_im in opts_im else 2
                    p['im'] = st.selectbox("Sistema Cara", opts_im, index=idx_im, key=f"im_{p_id}")
                    if p['im'] == "Offset":
                        p['nt'] = st.number_input("Tintas F.", 0, 6, int(p.get('nt',4)), key=f"nt_{p_id}")
                        p['ba'] = st.checkbox("Barniz F.", p.get('ba',False), key=f"ba_{p_id}")
                    elif p['im'] == "Digital": p['ld'] = st.checkbox("Laminado Digital F.", p.get('ld',False), key=f"ld_{p_id}")
                    opts_pel = list(st.session_state.db_precios["peliculado"].keys())
                    val_pel = p.get('pel', 'Sin Peliculado'); idx_pel = opts_pel.index(val_pel) if val_pel in opts_pel else 0
                    p['pel'] = st.selectbox("Peliculado Cara", opts_pel, index=idx_pel, key=f"pel_{p_id}")

                with col2:
                    opts_pf = list(st.session_state.db_precios["cartoncillo"].keys())
                    val_pf = p.get('pf', 'Ninguno'); idx_pf = opts_pf.index(val_pf) if val_pf in opts_pf else 0 
                    p['pf'] = st.selectbox("C. Frontal", opts_pf, index=idx_pf, key=f"pf_{p_id}", on_change=callback_cambio_frontal, args=(p_id,))
                    p['gf'] = st.number_input("Gramaje F.", value=int(p.get('gf', 0)), key=f"gf_{p_id}")
                    
                    # SECCIÓN PLANCHA / ONDULADO
                    st.divider()
                    opts_pl = list(st.session_state.db_precios["planchas"].keys())
                    val_pl = p.get('pl', 'Ninguna'); idx_pl = opts_pl.index(val_pl) if val_pl in opts_pl else 0
                    p['pl'] = st.selectbox("Plancha Base", opts_pl, index=idx_pl, key=f"pl_{p_id}")
                    
                    if p['pl'] != "Ninguna":
                        p['pl_dif'] = st.checkbox("📏 Medida Plancha Diferente", value=p.get('pl_dif', False), key=f"pldif_{p_id}")
                        if p['pl_dif']:
                            c_ph, c_pw = st.columns(2)
                            p['pl_h'] = c_ph.number_input("Alto Plancha", 0, 5000, value=int(p.get('pl_h', p['h'])), key=f"plh_{p_id}")
                            p['pl_w'] = c_pw.number_input("Ancho Plancha", 0, 5000, value=int(p.get('pl_w', p['w'])), key=f"plw_{p_id}")
                        else:
                            p['pl_h'] = p['h']
                            p['pl_w'] = p['w']
                    
                    opts_ap = ["C/C", "B/C", "B/B"]; val_ap = p.get('ap', 'B/C'); idx_ap = opts_ap.index(val_ap) if val_ap in opts_ap else 1
                    p['ap'] = st.selectbox("Calidad Ondulado", opts_ap, index=idx_ap, key=f"ap_{p_id}")
                    st.divider()

                    opts_pd = list(st.session_state.db_precios["cartoncillo"].keys())
                    val_pd = p.get('pd', 'Ninguno'); idx_pd = opts_pd.index(val_pd) if val_pd in opts_pd else 0
                    p['pd'] = st.selectbox("C. Dorso", opts_pd, index=idx_pd, key=f"pd_{p_id}", on_change=callback_cambio_dorso, args=(p_id,))
                    if p['pd'] != "Ninguno": p['gd'] = st.number_input("Gramaje D.", value=int(p.get('gd',0)), key=f"gd_{p_id}")
                
                with col3:
                    opts_cor = ["Troquelado", "Plotter"]; val_cor = p.get('cor', 'Troquelado'); idx_cor = opts_cor.index(val_cor) if val_cor in opts_cor else 0
                    p['cor'] = st.selectbox("Corte", opts_cor, index=idx_cor, key=f"cor_{p_id}")
                    if p['cor'] == "Troquelado": 
                        p['cobrar_arreglo'] = st.checkbox("¿Cobrar Arreglo?", value=p.get('cobrar_arreglo', True), key=f"arr_{p_id}")
                        p['pv_troquel'] = st.number_input("Precio Venta Troquel (€)", value=float(p.get('pv_troquel', 0.0)), key=f"pvt_{p_id}")
                    if p['pd'] != "Ninguno":
                        opts_imd = ["Offset", "Digital", "No"]; val_imd = p.get('im_d', 'No'); idx_imd = opts_imd.index(val_imd) if val_imd in opts_imd else 2
                        p['im_d'] = st.selectbox("Sistema Dorso", opts_imd, index=idx_imd, key=f"imd_{p_id}")
                        if p['im_d'] == "Offset":
                            p['nt_d'] = st.number_input("Tintas D.", 0, 6, int(p.get('nt_d',0)), key=f"ntd_{p_id}")
                            p['ba_d'] = st.checkbox("Barniz D.", p.get('ba_d',False), key=f"bad_{p_id}")
                        elif p['im_d'] == "Digital": p['ld_d'] = st.checkbox("Laminado Digital D.", p.get('ld_d',False), key=f"ldd_{p_id}")
                        val_peld = p.get('pel_d', 'Sin Peliculado'); idx_peld = opts_pel.index(val_peld) if val_peld in opts_pel else 0
                        p['pel_d'] = st.selectbox("Peliculado Dorso", opts_pel, index=idx_peld, key=f"peld_{p_id}")
                    if st.button("🗑 Borrar Forma", key=f"del_{p_id}"): del st.session_state.piezas_dict[p_id]; st.rerun()

        st.divider(); st.subheader("📦 2. Almacén de Accesorios")
        
        # --- MODIFICACIÓN V28: COLUMNAS PARA SELECTOR FLEXICO ---
        c_add_main, c_add_flex = st.columns(2)
        
        with c_add_main:
            st.markdown("**Extras Mainsa**")
            opts_extra = ["---"] + list(st.session_state.db_precios["extras_base"].keys())
            ex_sel = st.selectbox("Añadir extra estándar:", opts_extra, key="sel_extra_mainsa")
            if st.button("➕ Añadir Mainsa", key="btn_add_mainsa") and ex_sel != "---":
                coste_actual = st.session_state.db_precios["extras_base"][ex_sel]
                st.session_state.lista_extras_grabados.append({"nombre": ex_sel, "coste": coste_actual, "cantidad": 1.0}); st.rerun()
        
        with c_add_flex:
            st.markdown("**Catálogo FLEXICO**")
            OPCIONES_FLEXICO = [f"{k} - {v['desc']}" for k, v in PRODUCTOS_FLEXICO.items()]
            flx_sel = st.selectbox("Buscar Ref/Desc:", ["---"] + OPCIONES_FLEXICO, key="sel_extra_flexico") 
            if st.button("➕ Añadir Flexico", key="btn_add_flexico") and flx_sel != "---":
                cod = flx_sel.split(" - ")[0]
                prod = PRODUCTOS_FLEXICO[cod]
                st.session_state.lista_extras_grabados.append({"nombre": f"FLEXICO: {prod['desc']}", "coste": prod['precio'], "cantidad": 1.0}); st.rerun()

        for i, ex in enumerate(st.session_state.lista_extras_grabados):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            c1.write(f"**{ex['nombre']}**")
            if st.session_state.is_admin:
                ex['coste'] = c2.number_input("€/ud compra", value=float(ex['coste']), key=f"exc_{i}", format="%.4f")
            else:
                c2.write(f"{ex['coste']:.4f}€")
            ex['cantidad'] = c3.number_input("Cant/Ud prod", value=float(ex['cantidad']), key=f"exq_{i}")
            if c4.button("🗑", key=f"exd_{i}"): st.session_state.lista_extras_grabados.pop(i); st.rerun()

        st.divider(); st.subheader("📦 3. Cálculo de Embalaje")
        
        # SELECTOR DE TIPO DE EMBALAJE
        tipos_emb = ["Manual", "Embalaje Guaina (Automático)", "Embalaje en Plano (Pendiente)", "Embalaje en Volumen (Pendiente)"]
        idx_emb = tipos_emb.index(st.session_state.emb_tipo) if st.session_state.emb_tipo in tipos_emb else 0
        st.session_state.emb_tipo = st.selectbox("Selecciona el tipo de embalaje:", tipos_emb, index=idx_emb)

        if lista_cants:
            # LÓGICA AUTOMÁTICA (GUAINA)
            if st.session_state.emb_tipo == "Embalaje Guaina (Automático)":
                st.info("💡 **Fórmula Vallter:** `(Superficie * 0.70) + (30€ / Cantidad)`")
                c_dim1, c_dim2, c_dim3 = st.columns(3)
                st.session_state.emb_dims["L"] = c_dim1.number_input("Largo Caja (mm)", value=st.session_state.emb_dims.get("L", 0))
                st.session_state.emb_dims["W"] = c_dim2.number_input("Ancho Caja (mm)", value=st.session_state.emb_dims.get("W", 0))
                st.session_state.emb_dims["H"] = c_dim3.number_input("Alto Caja (mm)", value=st.session_state.emb_dims.get("H", 0))
                
                # Calcular automáticamente
                L, W, H = st.session_state.emb_dims["L"], st.session_state.emb_dims["W"], st.session_state.emb_dims["H"]
                if L > 0 and W > 0 and H > 0:
                    sup_m2 = ((2 * (L + W) * H) + (L * W)) / 1_000_000
                    st.write(f"📏 Superficie Cartón: **{sup_m2:.4f} m²**")
                    cols_emb = st.columns(len(lista_cants))
                    for i, q in enumerate(lista_cants):
                        if q > 0:
                            coste_auto = (sup_m2 * 0.70) + (30 / q)
                            st.session_state.costes_embalaje_manual[q] = coste_auto
                            if st.session_state.is_admin:
                                cols_emb[i].metric(f"{q} uds", f"{coste_auto:.3f}€")
                            else:
                                cols_emb[i].write(f"**{q} uds**: Calculado")
                else:
                    st.warning("Introduce las medidas de la caja para calcular el precio.")

            # LÓGICA MANUAL (O FALLBACK PARA PENDIENTES)
            else:
                if "Pendiente" in st.session_state.emb_tipo:
                    st.warning("⚠️ Fórmula no disponible aún. Introduce el precio manualmente.")
                
                st.info("Introduce el coste de compra UNITARIO (por caja/unidad) para cada cantidad.")
                cols_emb = st.columns(len(lista_cants))
                for i, q in enumerate(lista_cants):
                    if st.session_state.is_admin:
                        current_val = st.session_state.costes_embalaje_manual.get(q, 0.0)
                        val = cols_emb[i].number_input(f"Coste {q} uds (€)", value=float(current_val), format="%.4f", key=f"emb_man_{q}")
                        st.session_state.costes_embalaje_manual[q] = val
                    else:
                        cols_emb[i].write(f"**{q}**: Manual")
        else: st.warning("Define primero las cantidades en el panel lateral.")

        st.divider(); st.subheader("⚙️ 4. Gestión de Mermas (Manual)")
        tiene_dig = any(pz["im"] == "Digital" or pz.get("im_d") == "Digital" for pz in st.session_state.piezas_dict.values())
        if lista_cants:
            for q in lista_cants:
                with st.container(border=True):
                    c_lbl, c_imp, c_proc = st.columns([1, 2, 2])
                    c_lbl.markdown(f"### 📦 {q} uds")
                    std_proc, std_imp = calcular_mermas_estandar(q, tiene_dig)
                    curr_imp = st.session_state.mermas_imp_manual.get(q, std_imp)
                    curr_proc = st.session_state.mermas_proc_manual.get(q, std_proc)
                    val_imp = c_imp.number_input(f"🖨️ Arranque (Hojas Fijas)", value=int(curr_imp), key=f"mi_{q}", help="Hojas fijas de puesta a punto (se tiran al inicio)")
                    val_proc = c_proc.number_input(f"⚙️ Merma Rodaje (Hojas Extra)", value=int(curr_proc), key=f"mp_{q}", help="Hojas extra para cubrir roturas en producción")
                    st.session_state.mermas_imp_manual[q] = val_imp
                    st.session_state.mermas_proc_manual[q] = val_proc
        else: st.warning("Define primero las cantidades en el panel lateral.")

    # --- 6. MOTOR DE CÁLCULO (LÓGICA ACTUALIZADA CON DOBLE MEDIDA) ---
    res_final, desc_full, res_tecnico = [], {}, []
    if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
        total_pv_troqueles = sum(float(pz.get('pv_troquel', 0.0)) for pz in st.session_state.piezas_dict.values())
        
        for q_n in lista_cants:
            # 1. Definición de Mermas
            merma_imp_hojas = st.session_state.mermas_imp_manual.get(q_n, 0)        
            merma_proc_hojas = st.session_state.mermas_proc_manual.get(q_n, 0) 
            
            coste_f, det_f, debug_log = 0.0, [], []
            qp_labor = q_n 
            tech_hojas_papel = 0

            for p_id, p in st.session_state.piezas_dict.items():
                # VARIABLES DE CANTIDAD
                nb = q_n * p["pliegos"] # Netas
                hp_produccion = nb + merma_proc_hojas # Base Acabados
                hp_papel = hp_produccion + merma_imp_hojas # Base Compra Papel
                
                tech_hojas_papel += hp_papel

                # CÁLCULO DE SUPERFICIES (DOBLE MEDIDA)
                m2_papel = (p["w"]*p["h"])/1_000_000
                
                if p.get("pl_dif", False) and p.get("pl_h", 0) > 0:
                    m2_plancha = (p["pl_w"]*p["pl_h"])/1_000_000
                    txt_dim_plancha = f"(Custom: {p['pl_h']}x{p['pl_w']}mm)"
                else:
                    m2_plancha = m2_papel
                    txt_dim_plancha = "(Igual a Papel)"

                db = st.session_state.db_precios
                
                # --- CABECERA LOG ---
                debug_log.append(f"<br><b>🔹 PIEZA: {p['nombre']}</b>")
                debug_log.append(f"• Dim Papel: {p['h']}x{p['w']}mm = <b>{m2_papel:.4f} m²</b>")
                debug_log.append(f"• Dim Plancha: {txt_dim_plancha} = <b>{m2_plancha:.4f} m²</b>")
                
                # ---------------------------------------------------------
                # 1. PAPEL (Materia Prima) - Usa m2_papel
                # ---------------------------------------------------------
                p_kg_f = db["cartoncillo"][p["pf"]]["precio_kg"]
                c_cf = (hp_papel * m2_papel * (p.get('gf',0)/1000) * p_kg_f)
                
                p_kg_d = db["cartoncillo"][p.get('pd','Ninguno')]["precio_kg"]
                c_cd = (hp_papel * m2_papel * (p.get('gd',0)/1000) * p_kg_d)
                
                if p["pf"]!="Ninguno": 
                    debug_log.append(f"📦 <b>Papel Frontal:</b> {hp_papel:.0f}h x {m2_papel:.4f}m² x {p.get('gf',0)/1000:.3f}kg x {p_kg_f}€ = <b>{c_cf:.2f}€</b>")

                # ---------------------------------------------------------
                # 2. IMPRESIÓN (Usa m2_papel)
                # ---------------------------------------------------------
                def f_o(n): return 60 if n < 100 else (120 if n > 500 else 60 + 0.15*(n-100))
                
                # CARA
                if p["im"] == "Digital":
                    c_if = hp_papel * m2_papel * 6.5
                    debug_log.append(f"🖨️ <b>Imp. Digital F:</b> {hp_papel:.0f}h x {m2_papel:.4f}m² x 6.5€ = {c_if:.2f}€")
                elif p["im"] == "Offset":
                    coste_base_tirada = f_o(nb)
                    n_tintas = p.get('nt',0)
                    tiene_barniz = 1 if p.get('ba') else 0
                    c_if = coste_base_tirada * (n_tintas + tiene_barniz)
                    if c_if > 0: 
                        txt_barniz = " + 1 Barniz" if tiene_barniz else ""
                        debug_log.append(f"🖨️ <b>Imp. Offset F:</b> {coste_base_tirada:.2f}€ (Base Tirada) x ({n_tintas} Tintas{txt_barniz}) = <b>{c_if:.2f}€</b>")
                else: c_if = 0

                # DORSO
                if p.get("im_d") == "Digital":
                    c_id = hp_papel * m2_papel * 6.5
                    debug_log.append(f"🖨️ <b>Imp. Digital D:</b> {hp_papel:.0f}h x {m2_papel:.4f}m² x 6.5€ = {c_id:.2f}€")
                elif p.get("im_d") == "Offset":
                    coste_base_tirada = f_o(nb)
                    n_tintas_d = p.get('nt_d',0)
                    tiene_barniz_d = 1 if p.get('ba_d') else 0
                    c_id = coste_base_tirada * (n_tintas_d + tiene_barniz_d)
                    if c_id > 0:
                        txt_barniz_d = " + 1 Barniz" if tiene_barniz_d else ""
                        debug_log.append(f"🖨️ <b>Imp. Offset D:</b> {coste_base_tirada:.2f}€ (Base Tirada) x ({n_tintas_d} Tintas{txt_barniz_d}) = <b>{c_id:.2f}€</b>")
                else: c_id = 0

                # ---------------------------------------------------------
                # 3. PROCESOS (Usa m2_plancha)
                # ---------------------------------------------------------
                c_pla, c_peg = 0.0, 0.0
                if p["pl"] != "Ninguna":
                    # Plancha (Compra Material)
                    tipo_onda = p.get('ap','C/C')
                    p_ond = db["planchas"][p["pl"]][tipo_onda]
                    c_pla = hp_produccion * m2_plancha * p_ond
                    debug_log.append(f"🧱 <b>Plancha ({tipo_onda}):</b> {hp_produccion:.0f}h x {m2_plancha:.4f}m² x {p_ond}€ = <b>{c_pla:.2f}€</b>")
                    
                    # Contracolado (Proceso sobre superficie plancha)
                    p_peg = db["planchas"][p["pl"]]["peg"]
                    pas = (1 if p["pf"]!="Ninguno" else 0) + (1 if p.get('pd','Ninguno')!="Ninguno" else 0)
                    c_peg = hp_produccion * m2_plancha * p_peg * pas
                    debug_log.append(f"🧬 <b>Contracolado:</b> {hp_produccion:.0f}h x {m2_plancha:.4f}m² x {p_peg}€ x {pas} pases = <b>{c_peg:.2f}€</b>")
                
                # ---------------------------------------------------------
                # 4. PELICULADO (Usa m2_papel)
                # ---------------------------------------------------------
                c_pel_f, c_pel_d = 0.0, 0.0
                # Frontal
                if p["pel"] != "Sin Peliculado":
                    precio_pel = db["peliculado"][p["pel"]]
                    c_pel_base = hp_produccion * m2_papel * precio_pel
                    c_lam_dig = (hp_produccion * m2_papel * db.get("laminado_digital", 3.5)) if p.get("ld") else 0
                    c_pel_f = c_pel_base + c_lam_dig
                    desc_lam = f" + {c_lam_dig:.2f}€ (Lam.Dig)" if c_lam_dig > 0 else ""
                    debug_log.append(f"✨ <b>Peliculado F ({p['pel']}):</b> {hp_produccion:.0f}h x {m2_papel:.4f}m² x {precio_pel}€{desc_lam} = <b>{c_pel_f:.2f}€</b>")
                
                # Dorso
                if p.get('pel_d', 'Sin Peliculado') != "Sin Peliculado":
                    precio_pel_d = db["peliculado"][p['pel_d']]
                    c_pel_base_d = hp_produccion * m2_papel * precio_pel_d
                    c_lam_dig_d = (hp_produccion * m2_papel * db.get("laminado_digital", 3.5)) if p.get("ld_d") else 0
                    c_pel_d = c_pel_base_d + c_lam_dig_d
                    desc_lam_d = f" + {c_lam_dig_d:.2f}€ (Lam.Dig)" if c_lam_dig_d > 0 else ""
                    debug_log.append(f"✨ <b>Peliculado D ({p['pel_d']}):</b> {hp_produccion:.0f}h x {m2_papel:.4f}m² x {precio_pel_d}€{desc_lam_d} = <b>{c_pel_d:.2f}€</b>")
                
                # ---------------------------------------------------------
                # 5. CORTE Y TROQUEL
                # ---------------------------------------------------------
                l_p, w_p = p['h'], p['w']
                if p["cor"] == "Troquelado":
                    t_db = db.get("troquelado", PRECIOS_BASE["troquelado"])
                    if l_p > 1000 or w_p > 700: v_arr, v_tir = t_db["Grande (> 1000x700)"]["arranque"], t_db["Grande (> 1000x700)"]["tiro"]
                    elif l_p < 1000 and w_p < 700: v_arr, v_tir = t_db["Pequeño (< 1000x700)"]["arranque"], t_db["Pequeño (< 1000x700)"]["tiro"]
                    else: v_arr, v_tir = t_db["Mediano (Estándar)"]["arranque"], t_db["Mediano (Estándar)"]["tiro"]
                    
                    c_arr = v_arr if p.get('cobrar_arreglo', True) else 0
                    c_tir = (hp_produccion * v_tir)
                    debug_log.append(f"🔪 <b>Troquelado:</b> {c_arr}€ (Arr) + ({hp_produccion:.0f}h x {v_tir}€) = <b>{c_arr+c_tir:.2f}€</b>")
                else: 
                    coste_plotter = db.get("plotter", {"precio_hoja": 2.03}).get("precio_hoja", 2.03)
                    c_arr = 0; c_tir = hp_produccion * coste_plotter
                    debug_log.append(f"✂️ <b>Plotter:</b> {hp_produccion:.0f}h x {coste_plotter}€ = <b>{c_tir:.2f}€</b>")
                
                # TOTALES PIEZA
                s_imp = c_if + c_id; s_narba = c_pel_f + c_pel_d + c_peg + c_arr + c_tir; s_mat = c_cf + c_pla + c_cd
                sub = s_imp + s_narba + s_mat; coste_f += sub
                det_f.append({"Pieza": p["nombre"], "Mat. Frontal": c_cf, "Mat. Dorso": c_cd, "Mat. Ondulado": c_pla, "Imp. Cara": c_if, "Imp. Dorso": c_id, "Acab. Peliculado": c_pel_f + c_pel_d, "Acab. Contracolado": c_peg, "Acab. Troquel/Corte": c_arr + c_tir, "Total Imp": s_imp, "Total Narba": s_narba, "Total Mat": s_mat, "Subtotal": sub})

            # Costes Finales Globales
            c_ext_tot = sum(e["coste"] * e["cantidad"] * qp_labor for e in st.session_state.lista_extras_grabados)
            c_mo = ((seg_man_total/3600)*18*qp_labor) + (qp_labor*dif_ud)
            
            coste_emb_unit_compra = st.session_state.costes_embalaje_manual.get(q_n, 0.0)
            pv_emb_ud = coste_emb_unit_compra * 1.4; pv_emb_total = pv_emb_ud * q_n
            
            pvp_producto_base = ((coste_f + c_ext_tot + c_mo) * margen) + imp_fijo_pvp
            pvp_total_todo = pvp_producto_base + pv_emb_total + total_pv_troqueles
            p_total_unitario_all = pvp_total_todo / q_n if q_n > 0 else 0

            res_final.append({"Cantidad": q_n, "Precio Venta Unitario": f"{pvp_producto_base/q_n:.3f}€", "Precio Embalaje Unitario": f"{pv_emb_ud:.3f}€", "Precio Troquel (Total)": f"{total_pv_troqueles:.2f}€", "Precio Venta Total": f"{pvp_total_todo:.2f}€", "Unitario (Todo Incluido)": f"{p_total_unitario_all:.3f}€"})
            
            # Resultado técnico para operarios
            res_tecnico.append({
                "Cantidad": q_n,
                "Hojas Papel": f"{tech_hojas_papel:.0f} hojas",
                "Embalaje": f"{coste_emb_unit_compra:.2f}€/u (Compra)"
            })
            
            desc_full[q_n] = {"det": det_f, "mo": c_mo, "extras": c_ext_tot, "fijo": imp_fijo_pvp, "taller": coste_f + c_mo + c_ext_tot, "qp": qp_labor, "m_imp": merma_imp_hojas, "m_proc": merma_proc_hojas, "debug": debug_log}

    # --- 7. SALIDA VISUAL ---
    if st.session_state.is_admin:
        if modo_comercial and res_final:
            desc_html = """<div style='text-align: left; margin-bottom: 20px; color: #444;'>
            <h4 style='color: #1E88E5; margin-bottom: 5px;'>📋 Especificaciones del Proyecto</h4>
            <ul style='list-style-type: none; padding-left: 0;'>"""
            for p in st.session_state.piezas_dict.values():
                mat_f = f"<b>Frontal:</b> {p['pf']} ({p.get('gf',0)}g)" if p['pf'] != "Ninguno" else ""
                mat_d = f" | <b>Dorso:</b> {p['pd']} ({p.get('gd',0)}g)" if p.get('pd', "Ninguno") != "Ninguno" else ""
                mat_pl = f" | <b>Base:</b> {p['pl']}" if p.get('pl', "Ninguna") != "Ninguna" else ""
                
                # --- MODIFICACIÓN VISUAL: MOSTRAR SI HAY PLANCHA DIFERENTE ---
                if p.get('pl_dif', False):
                    mat_pl += f" <span style='color: #d32f2f; font-size: 0.9em;'>(Medida Optimizada: {p['pl_h']}x{p['pl_w']}mm)</span>"
                # -------------------------------------------------------------

                info_imp = ""; info_pliegos = f" | <b>Pliegos/Ud:</b> {p['pliegos']}" if p['pliegos'] != 1 else ""
                if p['im'] == "Offset": info_imp = f" | <b>Imp:</b> Offset {p['nt']} tintas" + (" + Barniz" if p['ba'] else "")
                elif p['im'] == "Digital": info_imp = " | <b>Imp:</b> Digital"
                detalles_mat = mat_f + mat_d + mat_pl + info_imp + info_pliegos
                if not detalles_mat: detalles_mat = "Sin materiales definidos"
                desc_html += f"<li style='margin-bottom: 8px;'>🔹 <b>{p['nombre']}</b> ({p['h']}x{p['w']} mm)<br><span style='font-size:0.9em; color:#666; margin-left: 20px;'>{detalles_mat}</span></li>"
            if st.session_state.lista_extras_grabados:
                desc_html += "<li style='margin-top: 10px;'><b>🧩 Accesorios:</b> "
                items_acc = [f"{ex['nombre']} (x{int(ex['cantidad']) if ex['cantidad'].is_integer() else ex['cantidad']})" for ex in st.session_state.lista_extras_grabados]
                desc_html += ", ".join(items_acc) + "</li>"
            desc_html += "</ul></div>"
            rows_html = ""
            for r in res_final: rows_html += f"""<tr><td style='font-weight:bold;'>{r['Cantidad']}</td><td>{r['Precio Venta Unitario']}</td><td>{r['Precio Embalaje Unitario']}</td><td>{r['Precio Troquel (Total)']}</td><td style='background-color: #f0f8ff;'>{r['Precio Venta Total']}</td><td style='font-weight:bold; color: #1E88E5;'>{r['Unitario (Todo Incluido)']}</td></tr>"""
            st.markdown(f"""<div class="comercial-box"><h2 class="comercial-header">OFERTA COMERCIAL - {st.session_state.cli}</h2><p class="comercial-ref">Ref. Briefing: {st.session_state.brf}</p>{desc_html}<table class="comercial-table"><tr><th>Cantidad</th><th>P. Venta Unitario</th><th>P. Emb. Unitario</th><th>Troqueles (Total)</th><th>PRECIO VENTA TOTAL</th><th>UNITARIO (TODO)</th></tr>{rows_html}</table><p style='text-align: right; font-size: 0.9em; color: #777; margin-top: 15px;'>* Oferta válida salvo error tipográfico. IVA no incluido.</p></div>""", unsafe_allow_html=True)
        else:
            # VISUALIZACIÓN TÉCNICA ADMIN
            if res_final:
                st.header(f"📊 Resumen de Venta: {st.session_state.cli}")
                st.dataframe(pd.DataFrame(res_final), use_container_width=True)
                for q, info in desc_full.items():
                    with st.expander(f"🔍 Auditoría Taller {q} uds (Taller: {info['qp']} uds)"):
                        st.info(f"**CONTROL DE MERMAS:**\n🔹 **Arranque Impresión:** {info['m_imp']} hojas fijas\n🔹 **Merma Procesos:** {info['m_proc']} hojas extra\n✅ **Base Cálculo Acabados:** {info['qp']*st.session_state.piezas_dict[0]['pliegos'] + info['m_proc']} hojas")
                        df_raw = pd.DataFrame(info["det"])
                        cols_order = ["Pieza", "Mat. Frontal", "Mat. Dorso", "Mat. Ondulado", "Total Mat", "Imp. Cara", "Imp. Dorso", "Total Imp", "Acab. Peliculado", "Acab. Contracolado", "Acab. Troquel/Corte", "Total Narba", "Subtotal"]
                        cols_final = [c for c in cols_order if c in df_raw.columns]
                        df_sorted = df_raw[cols_final]
                        row_mo = {c: 0 for c in cols_final[1:]}; row_mo["Pieza"] = "MANO DE OBRA (Manipulado)"; row_mo["Subtotal"] = info['mo']
                        row_ext = {c: 0 for c in cols_final[1:]}; row_ext["Pieza"] = "MATERIALES EXTRA (Accesorios)"; row_ext["Subtotal"] = info['extras']
                        df_audit = pd.concat([df_sorted, pd.DataFrame([row_mo, row_ext])], ignore_index=True)
                        sum_row = {"Pieza": "TOTAL COSTE INDUSTRIAL"}; 
                        for col in cols_final[1:]: sum_row[col] = df_audit[col].sum()
                        df_final = pd.concat([df_audit, pd.DataFrame([sum_row])], ignore_index=True)
                        st.table(df_final.style.format("{:.2f}€", subset=df_final.columns[1:]).set_properties(**{'background-color': '#e3f2fd', 'font-weight': 'bold'}, subset=["Total Imp","Total Narba","Total Mat","Subtotal"]))
                        st.metric("COSTO TALLER (Sin Margen)", f"{info['taller']:.2f}€")
    else:
        # VISUALIZACIÓN OPERARIO
        if res_tecnico:
            st.success("✅ Cálculo Realizado Correctamente")
            st.subheader("📋 Hoja de Producción")
            st.table(pd.DataFrame(res_tecnico))
            
            # Mostrar detalles técnicos sin precios
            for q, info in desc_full.items():
                with st.expander(f"📦 Detalle Materiales para {q} uds"):
                    st.write(f"**Hojas Totales (Inc. Mermas):** {info['m_imp'] + info['qp']*st.session_state.piezas_dict[0]['pliegos']} hojas")
                    st.write(f"**Mermas Previstas:** {info['m_imp']} arranque + {info['m_proc']} rodaje")

# ==============================================================================
# PESTAÑA 3: DESGLOSE DETALLADO (AUDITORÍA)
# ==============================================================================
if tab_debug:
    with tab_debug:
        st.header("🔍 Auditoría de Cálculos Paso a Paso")
        st.info("Aquí puedes ver la fórmula exacta que se ha usado para cada línea de coste.")
        
        if lista_cants and desc_full:
            sel_q = st.selectbox("Seleccionar Cantidad a Auditar:", lista_cants)
            if sel_q in desc_full:
                logs = desc_full[sel_q]["debug"]
                for linea in logs:
                    st.markdown(linea, unsafe_allow_html=True)
                
                st.divider()
                st.markdown(f"**Mano de Obra:** {desc_full[sel_q]['mo']:.2f}€")
                st.markdown(f"**Extras:** {desc_full[sel_q]['extras']:.2f}€")
        else:
            st.warning("Calcula un presupuesto primero para ver el desglose.")
