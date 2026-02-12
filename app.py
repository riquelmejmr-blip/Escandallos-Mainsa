import streamlit as st
import pandas as pd
import json
import re
import math

# --- 1. CONFIGURACIÓN Y DATOS INICIALES ---
st.set_page_config(page_title="MAINSA ADMIN V45", layout="wide")

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

# --- 2. BASE DE DATOS INICIAL ---
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
    "rigidos": {
        "Ninguno": {"precio_ud": 0.0, "w": 0, "h": 0},
        "Compacto 1.5mm (1000x700)": {"precio_ud": 3.20, "w": 1000, "h": 700},
        "Compacto 2mm (1050x750)": {"precio_ud": 4.50, "w": 1050, "h": 750},
        "PVC 3mm (2000x1000)": {"precio_ud": 18.00, "w": 2000, "h": 1000},
        "PVC 5mm (3000x2000)": {"precio_ud": 45.00, "w": 3000, "h": 2000},
        "PET 1mm (1200x800)": {"precio_ud": 9.80, "w": 1200, "h": 800},
        "Pegasus 10mm (3000x2000)": {"precio_ud": 65.00, "w": 3000, "h": 2000},
        "Polipropileno Celular 3.5mm (3050x2050)": {"precio_ud": 15.00, "w": 3050, "h": 2050}
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

FORMATOS_STD = {
    "Personalizado": (0, 0), "1600x1200": (1600, 1200), "1600x1100": (1600, 1100),
    "1400x1000": (1400, 1000), "1300x900": (1300, 900), "1200x800": (1200, 800),
    "1100x800": (1100, 800), "1000x700": (1000, 700), "900x650": (900, 650),
    "800x550": (800, 550), "700x500": (700, 500)
}

def calcular_mermas_estandar(n, es_digital=False):
    if es_digital: return int(n * 0.02), 10 
    if n < 100: return 10, 150
    if n < 200: return 20, 175
    if n < 600: return 30, 200
    if n < 1000: return 40, 220
    if n < 2000: return 50, 250
    return int(n*0.03), 300

# --- 3. INICIALIZACIÓN ---
st.set_page_config(page_title="MAINSA ADMIN V45", layout="wide")

if 'db_precios' not in st.session_state: st.session_state.db_precios = PRECIOS_BASE.copy()
if 'is_admin' not in st.session_state: st.session_state.is_admin = False 

def crear_forma_vacia(index):
    return {
        "nombre": f"Forma {index + 1}", "pliegos": 1.0, "w": 0, "h": 0, 
        "pf": "Ninguno", "gf": 0, 
        "tipo_base": "Ondulado/Cartón", 
        "pl": "Ninguna", "ap": "B/C", "mat_rigido": "Ninguno",
        "pd": "Ninguno", "gd": 0, 
        "im": "No", "nt": 0, "ba": False, 
        "im_d": "No", "nt_d": 0, "ba_d": False, 
        "pel": "Sin Peliculado", "pel_d": "Sin Peliculado", "ld": False, "ld_d": False, 
        "cor": "Troquelado", "cobrar_arreglo": True, "pv_troquel": 0.0, "pl_dif": False, "pl_h": 0, "pl_w": 0 
    }

if 'piezas_dict' not in st.session_state: st.session_state.piezas_dict = {0: crear_forma_vacia(0)}
if 'lista_extras_grabados' not in st.session_state: st.session_state.lista_extras_grabados = []
if 'costes_embalaje_manual' not in st.session_state: st.session_state.costes_embalaje_manual = {}
if 'mermas_imp_manual' not in st.session_state: st.session_state.mermas_imp_manual = {}
if 'mermas_proc_manual' not in st.session_state: st.session_state.mermas_proc_manual = {}

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

# --- BARRA LATERAL ---
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
    else:
        dif_ud, imp_fijo_pvp, margen = 0.091, 500.0, 2.2
    
    # VISIBLE PARA TODOS
    modo_comercial = st.checkbox("🌟 VISTA OFERTA", value=False)
        
    st.divider()
    st.header("💾 Guardar")
    safe_brf = re.sub(r'[\\/*?:"<>|]', "", st.session_state.brf or "Ref").replace(" ", "_")
    safe_cli = re.sub(r'[\\/*?:"<>|]', "", st.session_state.cli or "Cli").replace(" ", "_")
    nombre_archivo = f"{safe_brf}_{safe_cli}.json"
    
    datos_exp = {
        "brf": st.session_state.brf, "cli": st.session_state.cli, "desc": st.session_state.desc,
        "piezas": st.session_state.piezas_dict, "extras": st.session_state.lista_extras_grabados,
        "costes_emb": st.session_state.costes_embalaje_manual, "emb_tipo": st.session_state.emb_tipo,
        "mermas_imp": st.session_state.mermas_imp_manual, "mermas_proc": st.session_state.mermas_proc_manual
    }
    st.download_button(f"Descargar {nombre_archivo}", json.dumps(datos_exp, indent=4), nombre_archivo)

# --- PESTAÑAS ---
if st.session_state.is_admin:
    tab_calculadora, tab_costes, tab_debug = st.tabs(["🧮 Calculadora", "💰 Base de Datos", "🔍 Desglose"])
else:
    tab_calculadora, = st.tabs(["🧮 Calculadora Técnica"])
    tab_costes, tab_debug = None, None

# --- CONTENIDO PESTAÑAS ---
if tab_costes:
    with tab_costes:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            with st.expander("📄 Cartoncillo (€/Kg)", expanded=True):
                for k, v in st.session_state.db_precios["cartoncillo"].items():
                    if k != "Ninguno":
                        st.session_state.db_precios["cartoncillo"][k]["precio_kg"] = st.number_input(f"{k} (€/kg)", value=float(v["precio_kg"]), key=f"cost_cart_{k}")
            with st.expander("🧱 Ondulado y Rígidos (€/u)", expanded=True):
                st.markdown("##### Ondulado (Base variable)")
                for k, v in st.session_state.db_precios["planchas"].items():
                    if k != "Ninguna":
                        st.markdown(f"**{k}**")
                        cols = st.columns(len(v))
                        for idx, (sk, sv) in enumerate(v.items()):
                            st.session_state.db_precios["planchas"][k][sk] = cols[idx].number_input(sk, value=float(sv), key=f"cost_pl_{k}_{sk}")
                st.markdown("---")
                st.markdown("##### Rígidos (Plancha Fija)")
                for k, v in st.session_state.db_precios["rigidos"].items():
                    if k != "Ninguno":
                        st.session_state.db_precios["rigidos"][k]["precio_ud"] = st.number_input(f"{k} ({v['w']}x{v['h']})", value=float(v["precio_ud"]), key=f"cost_rig_{k}")
        with col_c2:
            with st.expander("✨ Acabados", expanded=True):
                for k, v in st.session_state.db_precios["peliculado"].items():
                    if k != "Sin Peliculado":
                        st.session_state.db_precios["peliculado"][k] = st.number_input(f"{k}", value=float(v), key=f"cost_pel_{k}")
                st.session_state.db_precios["laminado_digital"] = st.number_input("Laminado Digital", value=float(st.session_state.db_precios.get("laminado_digital", 3.5)), key="cost_lam_dig")
            with st.expander("🔪 Troquelado", expanded=True):
                for k, v in st.session_state.db_precios["troquelado"].items():
                    st.markdown(f"**{k}**")
                    c_arr, c_tir = st.columns(2)
                    st.session_state.db_precios["troquelado"][k]["arranque"] = c_arr.number_input(f"Arranque (€)", value=float(v["arranque"]), key=f"trq_arr_{k}")
                    st.session_state.db_precios["troquelado"][k]["tiro"] = c_tir.number_input(f"Tiro (€/h)", value=float(v["tiro"]), format="%.4f", key=f"trq_tir_{k}")
            with st.expander("✂️ Plotter", expanded=True):
                 st.session_state.db_precios["plotter"]["precio_hoja"] = st.number_input("Corte Plotter (€/hoja)", value=float(st.session_state.db_precios["plotter"]["precio_hoja"]))

with tab_calculadora:
    if not modo_comercial:
        st.header("1. Definición Técnica")
        c_btns = st.columns([1, 4])
        if c_btns[0].button("➕ Forma"):
            nid = max(st.session_state.piezas_dict.keys()) + 1
            st.session_state.piezas_dict[nid] = crear_forma_vacia(nid); st.rerun()
        if c_btns[1].button("🗑 Reiniciar"):
            st.session_state.piezas_dict = {0: crear_forma_vacia(0)}; st.session_state.lista_extras_grabados = []; st.rerun()

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
                if not st.session_state.get(f"pldif_{pid}", False):
                     st.session_state[f"plh_{pid}"] = nh; st.session_state[f"plw_{pid}"] = nw

        for p_id, p in st.session_state.piezas_dict.items():
            with st.expander(f"🛠 {p.get('nombre', 'Forma')} - {p.get('h',0)}x{p.get('w',0)} mm", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    p['nombre'] = st.text_input("Etiqueta", p.get('nombre', f"Forma {p_id+1}"), key=f"n_{p_id}")
                    p['pliegos'] = st.number_input("Pliegos/Ud", 0.0, 100.0, float(p.get('pliegos', 1.0)), format="%.4f", key=f"p_{p_id}")
                    st.selectbox("Medidas Estándar", list(FORMATOS_STD.keys()), key=f"std_{p_id}", on_change=callback_medida_estandar, args=(p_id,))
                    
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
                    
                    st.divider()
                    
                    # --- NUEVA LÓGICA RÍGIDOS ---
                    opts_base = ["Ondulado/Cartón", "Material Rígido"]
                    idx_base = opts_base.index(p.get("tipo_base", "Ondulado/Cartón")) if p.get("tipo_base") in opts_base else 0
                    p['tipo_base'] = st.selectbox("Tipo Soporte", opts_base, index=idx_base, key=f"tb_{p_id}")
                    
                    if p['tipo_base'] == "Ondulado/Cartón":
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
                    else:
                        # RÍGIDO
                        opts_rig = list(st.session_state.db_precios["rigidos"].keys())
                        idx_rig = opts_rig.index(p.get('mat_rigido', "Ninguno")) if p.get('mat_rigido') in opts_rig else 0
                        p['mat_rigido'] = st.selectbox("Material Rígido", opts_rig, index=idx_rig, key=f"mrig_{p_id}")
                        if p['mat_rigido'] != "Ninguno":
                            im = st.session_state.db_precios["rigidos"][p['mat_rigido']]
                            if p['w']>0 and p['h']>0:
                                y1 = (im['w']//p['w'])*(im['h']//p['h'])
                                y2 = (im['w']//p['h'])*(im['h']//p['w'])
                                by = max(y1, y2)
                                if by>0: st.info(f"Caben {by} uds/plancha")
                                else: st.error("Pieza muy grande")

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

        st.divider(); st.subheader("📦 3. Embalaje")
        tipos_emb = ["Manual", "Embalaje Guaina (Automático)", "Embalaje en Plano (Pendiente)", "Embalaje en Volumen (Pendiente)"]
        idx_emb = tipos_emb.index(st.session_state.emb_tipo) if st.session_state.emb_tipo in tipos_emb else 0
        st.session_state.emb_tipo = st.selectbox("Selecciona el tipo de embalaje:", tipos_emb, index=idx_emb)

        if lista_cants:
            if st.session_state.emb_tipo == "Embalaje Guaina (Automático)":
                d1, d2, d3 = st.columns(3)
                L = d1.number_input("Largo mm", value=st.session_state.emb_dims["L"])
                W = d2.number_input("Ancho mm", value=st.session_state.emb_dims["W"])
                H = d3.number_input("Alto mm", value=st.session_state.emb_dims["H"])
                st.session_state.emb_dims = {"L": L, "W": W, "H": H}
                sup_m2 = ((2*(L+W)*H)+(L*W))/1_000_000
                cols = st.columns(len(lista_cants))
                for idx, q in enumerate(lista_cants):
                    if q > 0:
                        coste_auto = (sup_m2 * 0.70) + (30 / q)
                        st.session_state.costes_embalaje_manual[q] = coste_auto
                        if st.session_state.is_admin:
                            cols[idx].metric(f"{q} uds", f"{coste_auto:.3f}€")
                        else:
                            cols[idx].write(f"**{q} uds**: Calculado")
            else:
                cols = st.columns(len(lista_cants))
                for idx, q in enumerate(lista_cants):
                    if st.session_state.is_admin:
                        st.session_state.costes_embalaje_manual[q] = cols[idx].number_input(f"Coste {q} uds", value=float(st.session_state.costes_embalaje_manual.get(q,0.0)), key=f"em_{q}")
                    else:
                        cols[idx].write(f"**{q} uds**: Manual")
        else: st.warning("Define cantidades primero.")

        st.divider(); st.subheader("⚙️ 4. Gestión de Mermas")
        if lista_cants:
            for q in lista_cants:
                c1, c2, c3 = st.columns([1,2,2])
                c1.markdown(f"**{q} uds**")
                st.session_state.mermas_imp_manual[q] = c2.number_input("Arranque (h)", value=st.session_state.mermas_imp_manual.get(q, 150), key=f"mi_{q}")
                st.session_state.mermas_proc_manual[q] = c3.number_input("Rodaje (h)", value=st.session_state.mermas_proc_manual.get(q, 30), key=f"mp_{q}")

    # --- MOTOR DE CÁLCULO ---
    res_final, desc_full, res_tecnico = [], {}, []
    if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
        tot_pv_trq = sum(float(pz.get('pv_troquel', 0.0)) for pz in st.session_state.piezas_dict.values())
        
        for q_n in lista_cants:
            # 1. MOVIDO AL PRINCIPIO: Lectura de coste embalaje
            coste_emb_unit_compra = st.session_state.costes_embalaje_manual.get(q_n, 0.0)

            merma_imp_hojas = st.session_state.mermas_imp_manual.get(q_n, 0)        
            merma_proc_hojas = st.session_state.mermas_proc_manual.get(q_n, 0) 
            coste_f, det_f, debug_log = 0.0, [], []
            qp_labor = q_n 
            tech_hojas_papel = 0
            tech_planchas_rigidas = 0

            for pid, p in st.session_state.piezas_dict.items():
                # INICIALIZAR TODAS LAS VARIABLES A 0
                c_cf = c_cd = c_imp = c_pl = c_peg = c_pel_f = c_pel_d = c_pel = c_trq = c_plot = c_imp_f = c_imp_d = 0.0

                nb = q_n * p["pliegos"]
                hp_produccion = nb + merma_proc_hojas
                hp_papel_f = hp_produccion + merma_imp_hojas if p["im"] != "No" else hp_produccion
                hp_papel_d = hp_produccion + merma_imp_hojas if p.get("im_d", "No") != "No" else hp_produccion

                m2_papel = (p["w"]*p["h"])/1_000_000
                tech_hojas_papel += hp_papel_f 

                db = st.session_state.db_precios
                
                # --- CABECERA LOG ---
                debug_log.append(f"<br><b>🔹 PIEZA: {p['nombre']}</b>")
                
                # --- SOPORTE (RIGIDO vs ONDULADO) ---
                if p.get("tipo_base") == "Material Rígido" and p.get("mat_rigido") != "Ninguno":
                     im = db["rigidos"][p["mat_rigido"]]
                     mw, mh = im['w'], im['h']
                     if p['w'] > 0:
                         by = max((mw//p['w'])*(mh//p['h']), (mw//p['h'])*(mh//p['w']))
                         if by > 0:
                             n_pl = math.ceil(hp_produccion / by)
                             tech_planchas_rigidas += n_pl
                             c_pl = n_pl * im['precio_ud']
                             debug_log.append(f"🏗️ <b>Rígido:</b> {n_pl} planchas x {im['precio_ud']}€ = {c_pl:.2f}€")
                             if p["pf"] != "Ninguno":
                                 c_peg = hp_produccion * m2_papel * db["planchas"]["Microcanal / Canal 3"]["peg"]
                                 debug_log.append(f"🧬 <b>Pegado:</b> {c_peg:.2f}€")
                         else: debug_log.append("⚠️ ERROR: Pieza excede tamaño plancha")
                else:
                    # ONDULADO
                    if p.get("pl_dif", False) and p.get("pl_h", 0) > 0:
                        m2_plancha = (p["pl_w"]*p["pl_h"])/1_000_000
                    else: m2_plancha = m2_papel
                    
                    if p["pl"] != "Ninguna":
                        c_pl = hp_produccion * m2_plancha * db["planchas"][p["pl"]][p["ap"]]
                        c_peg = hp_produccion * m2_plancha * db["planchas"][p["pl"]]["peg"] * (1 if p["pf"]!="Ninguno" else 0)
                        debug_log.append(f"📦 <b>Ondulado:</b> {hp_produccion:.0f}h x {m2_plancha:.4f}m² x Coste = {c_pl:.2f}€")

                # --- MATERIALES ---
                c_cf = (hp_papel_f * m2_papel * (p['gf']/1000) * db["cartoncillo"][p["pf"]]["precio_kg"])
                if p.get("pd") != "Ninguno":
                     c_cd = (hp_papel_d * m2_papel * (p['gd']/1000) * db["cartoncillo"][p.get("pd","Ninguno")]["precio_kg"]) 
                debug_log.append(f"📄 <b>Papel F:</b> {c_cf:.2f}€ | <b>Papel D:</b> {c_cd:.2f}€")

                # --- IMPRESION ---
                def f_o(n): return 60 if n < 100 else (120 if n > 500 else 60 + 0.15*(n-100))
                c_imp = hp_papel_f * m2_papel * 6.5 if p["im"]=="Digital" else f_o(nb)*(p.get('nt',0) + (1 if p.get('ba') else 0))
                c_imp += hp_papel_d * m2_papel * 6.5 if p.get("im_d")=="Digital" else f_o(nb)*(p.get('nt_d',0) + (1 if p.get('ba_d') else 0))
                debug_log.append(f"🖨️ <b>Impresión Total:</b> {c_imp:.2f}€")

                # --- ACABADOS ---
                c_pel_f = (hp_produccion * m2_papel * db["peliculado"][p["pel"]]) if p["pel"] != "Sin Peliculado" else 0
                c_pel_d = (hp_produccion * m2_papel * db["peliculado"][p.get("pel_d","Sin Peliculado")]) if p.get("pel_d") != "Sin Peliculado" else 0
                c_pel = c_pel_f + c_pel_d
                if c_pel > 0: debug_log.append(f"✨ <b>Peliculado:</b> {c_pel:.2f}€")
                
                t_db = db.get("troquelado", PRECIOS_BASE["troquelado"])
                cat = "Grande (> 1000x700)" if (p['h']>1000 or p['w']>700) else ("Pequeño (< 1000x700)" if (p['h']<1000 and p['w']<700) else "Mediano (Estándar)")
                
                if p["cor"] == "Troquelado": c_trq = (t_db[cat]['arranque'] if p.get('cobrar_arreglo',True) else 0) + (hp_produccion * t_db[cat]['tiro'])
                if p["cor"] == "Plotter": c_plot = (hp_produccion * db["plotter"]["precio_hoja"])

                sub = c_cf + c_cd + c_imp + c_pl + c_peg + c_pel + c_trq + c_plot
                coste_f += sub
                
                s_mat = c_cf + c_cd + c_pl
                s_imp_t = c_imp
                s_narba = c_pel + c_peg + c_trq + c_plot

                det_f.append({"Pieza": p["nombre"], "Mat. Frontal": c_cf, "Mat. Dorso": c_cd, "Mat. Ondulado": c_pl, "Total Mat": s_mat, "Imp. Total": s_imp_t, "Acab. Peliculado": c_pel, "Acab. Contracolado": c_peg, "Acab. Troquel/Corte": c_trq + c_plot, "Total Narba": s_narba, "Subtotal": sub})

            c_ext = sum(e["coste"] * e["cantidad"] * qp_labor for e in st.session_state.lista_extras_grabados)
            c_mo = ((seg_man_total/3600)*18*q_n) + (q_n*dif_ud)
            pv_emb_total = coste_emb_unit_compra * 1.4 * q_n
            
            pvp_total_todo = ((coste_f + c_ext_tot + c_mo) * margen) + imp_fijo_pvp + pv_emb_total + tot_pv_trq
            
            res_final.append({"Cantidad": q_n, "Precio Venta Unitario": f"{pvp_total_todo/q_n:.3f}€", "Precio Embalaje Unitario": f"{pv_emb_ud:.3f}€", "Precio Troquel (Total)": f"{tot_pv_trq:.2f}€", "Precio Venta Total": f"{pvp_total_todo:.2f}€", "Unitario (Todo Incluido)": f"{pvp_total_todo/q_n:.3f}€"})
            
            # Resultado técnico para operarios
            res_tecnico.append({
                "Cantidad": q_n,
                "Hojas Papel": f"{tech_hojas_papel:.0f} hojas",
                "Planchas Rígidas": f"{tech_planchas_rigidas} planchas",
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
                
                if p.get("tipo_base") == "Material Rígido":
                    mat_pl = f" | <b>Rígido:</b> {p.get('mat_rigido')}"
                else:
                    mat_pl = f" | <b>Base:</b> {p['pl']} ({p['ap']})" if p.get('pl', "Ninguna") != "Ninguna" else ""
                    if p.get('pl_dif', False):
                        mat_pl += f" <span style='color: #d32f2f; font-size: 0.9em;'>(Medida Optimizada: {p['pl_h']}x{p['pl_w']}mm)</span>"

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
            for r in res_final: 
                rows_html += f"""<tr><td style='font-weight:bold;'>{r['Cantidad']}</td><td>{r['Precio Venta Unitario']}</td><td>{r['Precio Embalaje Unitario']}</td><td>{r['Precio Troquel (Total)']}</td><td style='background-color: #f0f8ff;'>{r['Precio Venta Total']}</td><td style='font-weight:bold; color: #1E88E5;'>{r['Unitario (Todo Incluido)']}</td></tr>"""
                
            st.markdown(f"""<div class="comercial-box"><h2 class="comercial-header">OFERTA COMERCIAL - {st.session_state.cli}</h2><p class="comercial-ref">Ref. Briefing: {st.session_state.brf}</p>{desc_html}<table class="comercial-table"><tr><th>Cantidad</th><th>P. Venta Unitario</th><th>P. Emb. Unitario</th><th>Troqueles (Total)</th><th>PRECIO VENTA TOTAL</th><th>UNITARIO (TODO)</th></tr>{rows_html}</table><p style='text-align: right; font-size: 0.9em; color: #777; margin-top: 15px;'>* Oferta válida salvo error tipográfico. IVA no incluido.</p></div>""", unsafe_allow_html=True)
        else:
            if res_final: 
                st.header(f"📊 Resumen de Venta: {st.session_state.cli}")
                simple_res = []
                for r in res_final:
                    simple_res.append({"Cant": r['Cantidad'], "PVP Total": r['Precio Venta Total'], "Unitario": r['Unitario (Todo Incluido)']})
                st.dataframe(pd.DataFrame(simple_res), use_container_width=True)
                
                for q, info in desc_full.items():
                    with st.expander(f"🔍 Auditoría Taller {q} uds"):
                        df_raw = pd.DataFrame(info["det"])
                        cols_order = ["Pieza", "Mat. Frontal", "Mat. Dorso", "Mat. Ondulado", "Total Mat", "Imp. Total", "Acab. Peliculado", "Acab. Contracolado", "Acab. Troquel/Corte", "Total Narba", "Subtotal"]
                        cols_final = [c for c in cols_order if c in df_raw.columns]
                        df_sorted = df_raw[cols_final]
                        row_mo = {c: 0 for c in cols_final[1:]}; row_mo["Pieza"] = "MANO DE OBRA"; row_mo["Subtotal"] = info['mo']
                        row_ext = {c: 0 for c in cols_final[1:]}; row_ext["Pieza"] = "MATERIALES EXTRA"; row_ext["Subtotal"] = info['extras']
                        df_audit = pd.concat([df_sorted, pd.DataFrame([row_mo, row_ext])], ignore_index=True)
                        st.table(df_audit.style.format("{:.2f}€", subset=df_audit.columns[1:]).set_properties(**{'background-color': '#e3f2fd', 'font-weight': 'bold'}, subset=["Total Mat","Imp. Total","Total Narba","Subtotal"]))
                        st.metric("COSTO TALLER", f"{info['taller']:.2f}€")
    else:
        if res_tecnico:
            st.success("✅ Cálculo Realizado")
            st.table(pd.DataFrame(res_tecnico))

if tab_debug:
    with tab_debug:
        st.header("🔍 Auditoría de Cálculos")
        if lista_cants and desc_full:
            sel_q = st.selectbox("Ver Detalle Cantidad:", lista_cants)
            for l in desc_full[sel_q]["debug"]: st.markdown(l, unsafe_allow_html=True)
