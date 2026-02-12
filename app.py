import streamlit as st
import pandas as pd
import json
import re
import math

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
    "plotter": { "precio_hoja": 2.03 }
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
st.set_page_config(page_title="MAINSA ADMIN V35", layout="wide")

if 'db_precios' not in st.session_state: st.session_state.db_precios = PRECIOS_BASE.copy()
if 'is_admin' not in st.session_state: st.session_state.is_admin = False 

def crear_forma_vacia(index):
    return {
        "nombre": f"Forma {index + 1}", "pliegos": 1.0, "w": 0, "h": 0, 
        "pf": "Ninguno", "gf": 0, 
        "tipo_base": "Ondulado (A medida)", 
        "pl": "Ninguna", "ap": "B/C", "mat_rigido": "Ninguno",
        "pd": "Ninguno", "gd": 0, 
        "im": "No", "nt": 0, "ba": False, "im_d": "No", "nt_d": 0, "ba_d": False, 
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
    
    # --- FINANZAS (SOLO ADMIN) ---
    if st.session_state.is_admin:
        st.divider()
        st.markdown("### 💰 Finanzas")
        dif_ud = st.selectbox("Dificultad (€/ud)", [0.02, 0.061, 0.091], index=2)
        imp_fijo_pvp = st.number_input("Fijo PVP (€)", value=500.0)
        margen = st.number_input("Multiplicador", step=0.1, value=2.2)
        modo_comercial = st.checkbox("🌟 VISTA OFERTA", value=False)
    else:
        dif_ud, imp_fijo_pvp, margen, modo_comercial = 0.091, 500.0, 2.2, False
    
    # --- GUARDAR (PARA TODOS) ---
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
        st.header("Gestión de Costes")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            with st.expander("📄 Cartoncillo (€/Kg)", expanded=True):
                for k, v in st.session_state.db_precios["cartoncillo"].items():
                    if k != "Ninguno":
                        st.session_state.db_precios["cartoncillo"][k]["precio_kg"] = st.number_input(f"{k} (€/kg)", value=float(v["precio_kg"]), key=f"cost_cart_{k}")
            with st.expander("🧱 Ondulado y Rígidos", expanded=True):
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
                        st.session_state.db_precios["rigidos"][k]["precio_ud"] = st.number_input(f"{k}", value=float(v["precio_ud"]), key=f"cost_rig_{k}")
        with col_c2:
            with st.expander("✨ Acabados", expanded=True):
                for k, v in st.session_state.db_precios["peliculado"].items():
                    if k != "Sin Peliculado":
                        st.session_state.db_precios["peliculado"][k] = st.number_input(f"{k}", value=float(v), key=f"cost_pel_{k}")

with tab_calculadora:
    if not modo_comercial:
        st.header("1. Definición Técnica")
        c_btns = st.columns([1, 4])
        if c_btns[0].button("➕ Forma"):
            nid = max(st.session_state.piezas_dict.keys()) + 1
            st.session_state.piezas_dict[nid] = crear_forma_vacia(nid); st.rerun()
        if c_btns[1].button("🗑 Reiniciar"):
            st.session_state.piezas_dict = {0: crear_forma_vacia(0)}; st.session_state.lista_extras_grabados = []; st.rerun()

        for p_id, p in st.session_state.piezas_dict.items():
            with st.expander(f"🛠 {p.get('nombre', 'Forma')} - {p.get('h',0)}x{p.get('w',0)} mm", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    p['nombre'] = st.text_input("Etiqueta", p.get('nombre', f"Forma {p_id+1}"), key=f"n_{p_id}")
                    p['pliegos'] = st.number_input("Pliegos/Ud", 0.0, 100.0, float(p.get('pliegos', 1.0)), format="%.4f", key=f"p_{p_id}")
                    st.selectbox("Medidas Estándar", list(FORMATOS_STD.keys()), key=f"std_{p_id}", on_change=lambda id=p_id: st.session_state.update({f"h_{id}": FORMATOS_STD[st.session_state[f"std_{id}"]][0], f"w_{id}": FORMATOS_STD[st.session_state[f"std_{id}"]][1]}) if st.session_state[f"std_{id}"] != "Personalizado" else None, args=(p_id,))
                    
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
                    p['pf'] = st.selectbox("C. Frontal", opts_pf, index=idx_pf, key=f"pf_{p_id}")
                    # Auto-set gramaje if changed
                    if p['pf'] != "Ninguno" and p['gf'] == 0: p['gf'] = st.session_state.db_precios["cartoncillo"][p['pf']]["gramaje"]
                    p['gf'] = st.number_input("Gramaje F.", value=int(p.get('gf', 0)), key=f"gf_{p_id}")
                    
                    st.divider()
                    opts_base = ["Ondulado (A medida)", "Rígido (Plancha Estándar)"]
                    idx_tb = opts_base.index(p.get('tipo_base', "Ondulado (A medida)")) if p.get('tipo_base') in opts_base else 0
                    p['tipo_base'] = st.selectbox("Tipo Base", opts_base, index=idx_tb, key=f"tb_{p_id}")
                    
                    if p['tipo_base'] == "Ondulado (A medida)":
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
                    p['pd'] = st.selectbox("C. Dorso", opts_pd, index=idx_pd, key=f"pd_{p_id}")
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
                            cols[idx].write(f"**{q}**: Calculado")
            else:
                cols = st.columns(len(lista_cants))
                for idx, q in enumerate(lista_cants):
                    if st.session_state.is_admin:
                        st.session_state.costes_embalaje_manual[q] = cols[idx].number_input(f"Coste {q}", value=float(st.session_state.costes_embalaje_manual.get(q,0.0)), key=f"em_{q}")
                    else:
                        cols[idx].write(f"**{q}**: Manual")
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
            merma_imp_hojas = st.session_state.mermas_imp_manual.get(q_n, 0)        
            merma_proc_hojas = st.session_state.mermas_proc_manual.get(q_n, 0) 
            coste_f, logs, tech_pap, tech_rig = 0.0, [], 0, 0
            
            for pid, p in st.session_state.piezas_dict.items():
                nb = q_n * p["pliegos"]
                hp_p, hp_a = nb + merma_proc_hojas + merma_imp_hojas, nb + merma_proc_hojas
                m2_p = (p['w']*p['h'])/1_000_000
                tech_pap += hp_p
                
                # --- SOPORTE ---
                c_pl, c_peg = 0.0, 0.0
                if p.get("tipo_base") == "Material Rígido" and p.get("mat_rigido") != "Ninguno":
                     im = st.session_state.db_precios["rigidos"][p["mat_rigido"]]
                     mw, mh = im['w'], im['h']
                     if p['w'] > 0:
                         by = max((mw//p['w'])*(mh//p['h']), (mw//p['h'])*(mh//p['w']))
                         if by > 0:
                             n_pl = math.ceil(hp_a / by)
                             tech_rig += n_pl
                             c_pl = n_pl * im['precio_ud']
                             logs.append(f"🏗️ Rígido: {n_pl} planchas x {im['precio_ud']}€ = {c_pl:.2f}€")
                             if p["pf"] != "Ninguno":
                                 c_peg = hp_a * m2_p * st.session_state.db_precios["planchas"]["Microcanal / Canal 3"]["peg"]
                                 logs.append(f"🧬 Pegado: {c_peg:.2f}€")
                else:
                    m2_pl = (p['pl_w']*p['pl_h'])/1_000_000 if p.get("pl_dif") else m2_p
                    if p["pl"] != "Ninguna":
                        c_pl = hp_a * m2_pl * st.session_state.db_precios["planchas"][p["pl"]][p["ap"]]
                        c_peg = hp_a * m2_pl * st.session_state.db_precios["planchas"][p["pl"]]["peg"] * (1 if p["pf"]!="Ninguno" else 0)
                        logs.append(f"📦 Ondulado: {hp_a:.0f}h x {m2_pl:.4f}m2 x Precio = {c_pl:.2f}€")

                # --- MATERIALES Y PROCESOS ---
                c_mat = (hp_p * m2_p * (p['gf']/1000) * st.session_state.db_precios["cartoncillo"][p["pf"]]["precio_kg"])
                if p["pd"] != "Ninguno":
                     c_mat += (hp_p * m2_p * (p['gd']/1000) * st.session_state.db_precios["cartoncillo"][p["pd"]]["precio_kg"])
                
                def f_o(n): return 60 if n < 100 else (120 if n > 500 else 60 + 0.15*(n-100))
                c_imp = hp_p * m2_p * 6.5 if p["im"]=="Digital" else f_o(nb)*(p.get('nt',0) + (1 if p.get('ba') else 0))
                c_pel = (hp_a * m2_p * st.session_state.db_precios["peliculado"][p["pel"]])
                
                t_db = st.session_state.db_precios["troquelado"]
                cat = "Grande (> 1000x700)" if (p['h']>1000 or p['w']>700) else ("Pequeño (< 1000x700)" if (p['h']<1000 and p['w']<700) else "Mediano (Estándar)")
                c_trq = (t_db[cat]['arranque'] if p.get('cobrar_arreglo',True) else 0) + (hp_a * t_db[cat]['tiro'])
                
                sub = c_mat + c_imp + c_pl + c_peg + c_pel + c_trq; cost_f += sub
                logs.append(f"🔹 {p['nombre']}: Mat {c_mat:.2f} | Imp {c_imp:.2f} | Trq {c_trq:.2f}")

            c_ext = sum(e["coste"] * e["cantidad"] * q_n for e in st.session_state.lista_extras_grabados)
            c_mo = ((seg_man_total/3600)*18*q_n) + (q_n*dif_ud)
            pv_emb = st.session_state.costes_embalaje_manual.get(q_n, 0.0) * 1.4 * q_n
            pvp = ((cost_f + c_ext + c_mo) * margen) + imp_fijo_pvp + pv_emb + tot_pv_trq
            
            res_final.append({"Cant": q_n, "PVP Total": f"{pvp:.2f}€", "Unitario": f"{pvp/q_n:.3f}€"})
            res_tecnico.append({"Cant": q_n, "Hojas Papel": f"{tech_pap:.0f}", "Planchas Rígidas": f"{tech_rig}", "Extras": f"{len(st.session_state.lista_extras_grabados)}"})
            desc_full[q_n] = {"debug": logs}

    # --- RESULTADOS ---
    if st.session_state.is_admin:
        if modo_comercial:
            st.header(f"Oferta: {st.session_state.cli}")
            # --- RENDERIZADO COMERCIAL HTML RESTAURADO ---
            html_piezas = ""
            for p in st.session_state.piezas_dict.values():
                 base_info = f"Rígido: {p['mat_rigido']}" if p.get("tipo_base") == "Material Rígido" else f"Base: {p['pl']} ({p['ap']})"
                 html_piezas += f"<li><b>{p['nombre']}</b>: {p['h']}x{p['w']}mm | {p['pf']} | {base_info} | {p['pel']}</li>"
            
            st.markdown(f"""
            <div class="comercial-box">
                <h2 class="comercial-header">OFERTA: {st.session_state.cli}</h2>
                <p>{st.session_state.desc}</p>
                <ul>{html_piezas}</ul>
                <p><b>Accesorios:</b> {', '.join([e['nombre'] for e in st.session_state.lista_extras_grabados])}</p>
            </div>
            """, unsafe_allow_html=True)
            st.table(pd.DataFrame(res_final))
        else:
            if res_final: st.dataframe(pd.DataFrame(res_final))
    else:
        if res_tecnico:
            st.success("✅ Cálculo OK")
            st.table(pd.DataFrame(res_tecnico))

# --- AUDITORIA ---
if tab_debug:
    with tab_debug:
        if lista_cants and desc_full:
            sq = st.selectbox("Ver Uds:", lista_cants)
            for l in desc_full[sq]["debug"]: st.markdown(l)
