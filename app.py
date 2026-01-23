import streamlit as st
import pandas as pd
from fpdf2 import FPDF2
import io

# --- PRECIOS Y PARÁMETROS ---
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
        "Doble Micro / Doble Doble": {"C/C": 1.046, "B/C": 1.100, "B/B": 1.276, "peg": 0.263},
        "AC (Cuero/Cuero)": {"C/C": 2.505, "peg": 0.217}
    },
    "peliculado": {
        "Sin Peliculado": 0,
        "Polipropileno": 0.26,
        "Poliéster brillo": 0.38,
        "Poliéster mate": 0.64
    },
    "laminado_digital": 3.5,
    "extras": {
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

st.set_page_config(page_title="MAINSA PLV - PRO", layout="wide")
st.markdown("""<style> .main { background-color: #f8f9fa; } .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); } </style>""", unsafe_allow_html=True)

st.title("📦 Escandallos Profesionales MAINSA PLV")

# --- GESTIÓN DE PIEZAS ---
if 'piezas_ids' not in st.session_state: st.session_state.piezas_ids = [0]

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ajustes de Proyecto")
    cants_str = st.text_input("Cantidades (ej: 200, 500)", "200")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    st.divider()
    seg_man = st.number_input("Segundos Manipulación / Ud", value=300)
    dif_ud = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], index=2)
    margen = st.number_input("Multiplicador Comercial", value=2.2, step=0.1)

# --- BOTONES CONTROL ---
c1, c2 = st.columns([1, 6])
if c1.button("➕ Añadir Forma"):
    st.session_state.piezas_ids.append(max(st.session_state.piezas_ids) + 1)
    st.rerun()
if c2.button("🗑 Reiniciar Escandallo"):
    st.session_state.piezas_ids = [0]; st.rerun()

datos_pz = []; ids_to_del = []

for i_id in st.session_state.piezas_ids:
    with st.expander(f"🛠 Configuración de Forma", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            nom = st.text_input("Nombre", f"Pieza {i_id+1}", key=f"n_{i_id}")
            pliegos = st.number_input("Pliegos/Mueble", 0.0, 100.0, 1.0, 0.1, key=f"p_{i_id}")
            w = st.number_input("Ancho (mm)", 1, 5000, 700, key=f"w_{i_id}")
            h = st.number_input("Largo (mm)", 1, 5000, 1000, key=f"h_{i_id}")
        with col2:
            pf = st.selectbox("Cartoncillo Frontal", list(PRECIOS["cartoncillo"].keys()), 1, key=f"pf_{i_id}")
            gf = st.number_input("G. Frontal", PRECIOS["cartoncillo"][pf]["gramaje"], key=f"gf_{i_id}") if pf != "Ninguno" else 0
            pl = st.selectbox("Plancha Base", list(PRECIOS["planchas"].keys()), key=f"pl_{i_id}")
            ap = st.selectbox("Calidad", ["C/C", "B/C", "B/B"], 1, key=f"ap_{i_id}") if pl != "Ninguna" else "C/C"
            pd_s = st.selectbox("Cartoncillo Dorso", list(PRECIOS["cartoncillo"].keys()), key=f"pd_{i_id}")
            gd_s = st.number_input("G. Dorso", PRECIOS["cartoncillo"][pd_s]["gramaje"], key=f"gd_{i_id}") if pd_s != "Ninguno" else 0
        with col3:
            im = st.selectbox("Sistema Impresión", ["Offset", "Digital", "No"], key=f"im_{i_id}")
            nt = st.number_input("Tintas", 1, 6, 4, key=f"nt_{i_id}") if im == "Offset" else 0
            ba = st.checkbox("Barniz", key=f"ba_{i_id}") if im == "Offset" else False
            ld = st.checkbox("Laminado Digital", key=f"ld_{i_id}") if im == "Digital" else False
            pel = st.selectbox("Peliculado", list(PRECIOS["peliculado"].keys()), index=(0 if im=="Digital" else 1), key=f"pel_{i_id}")
            cor = st.selectbox("Corte", ["Troquelado", "Plotter"], key=f"cor_{i_id}")
            if st.button("🗑 Eliminar Forma", key=f"del_{i_id}"): ids_to_del.append(i_id)
        
        datos_pz.append({"id": i_id, "nombre": nom, "pliegos": pliegos, "w": w, "h": h, "pf": pf, "gf": gf, "pl": pl, "ap": ap, "pd": pd_s, "gd": gd_s, "im": im, "nt": nt, "ba": ba, "ld": ld, "pel": pel, "cor": cor})

for d_id in ids_to_del: st.session_state.piezas_ids.remove(d_id); st.rerun()

# --- ACCESORIOS ---
st.divider()
sel_ex = st.multiselect("📦 Accesorios de Montaje", list(PRECIOS["extras"].keys()))
l_ex = [{"n": n, "q": 1.0} for n in sel_ex] # Simplificado para el ejemplo

# --- CÁLCULOS ---
res_final = []; desc_full = {}
if lista_cants:
    for q_n in lista_cants:
        tiene_dig = any(d["im"] == "Digital" for d in datos_pz)
        mn_m, _ = calcular_mermas(q_n, es_digital=tiene_dig)
        qp_taller = q_n + mn_m
        det_partidas = []; total_fab = 0.0

        for p in datos_pz:
            nb = q_n * p["pliegos"]
            is_d = p["im"] == "Digital"
            mn, mi = calcular_mermas(nb, es_digital=is_d)
            hc, hp = nb+mn+mi, nb+mn
            m2 = (p["w"]*p["h"])/1000000
            
            c_cart = (hc*m2*(p["gf"]/1000)*PRECIOS["cartoncillo"][p["pf"]]["precio_kg"]) + (hc*m2*(p["gd"]/1000)*PRECIOS["cartoncillo"][p["pd"]]["precio_kg"])
            c_plan, c_con = 0.0, 0.0
            if p["pl"] != "Ninguna":
                c_plan = hp * m2 * PRECIOS["planchas"][p["pl"]][p["ap"]]
                num_pas = (1 if p["pf"]!="Ninguno" else 0) + (1 if p["pd"]!="Ninguno" else 0)
                c_con = hp * m2 * PRECIOS["planchas"][p["pl"]]["peg"] * num_pas
            
            c_imp = 0.0
            if p["im"] == "Digital": c_imp = nb*m2*6.5
            elif p["im"] == "Offset":
                base = 60 if nb<100 else (60+0.15*(nb-100) if nb<500 else (120 if nb<=2000 else 120+0.015*(nb-2000)))
                c_imp = base * (p["nt"] + (1 if p["ba"] else 0))
            
            c_acab = (hp*m2*PRECIOS["peliculado"][p["pel"]]) + (hp*m2*PRECIOS["laminado_digital"] if p["ld"] else 0)
            c_arr, c_tir = 0.0, (hp*1.5 if p["cor"]=="Plotter" else 0.0)
            if p["cor"] == "Troquelado":
                c_arr = 107.7 if (p['h']>1000 or p['w']>700) else (80.77 if (p['h']==1000 and p['w']==700) else 48.19)
                c_tir = hp * (0.135 if (p['h']>1000 or p['w']>700) else (0.09 if (p['h']==1000 and p['w']==700) else 0.06))
            
            det_partidas.append({"Pieza": p["nombre"], "Carton": c_cart, "Plancha": c_plan, "Contra": c_con, "Imp": c_imp, "Acab": c_acab, "Arreglo": c_arr, "Tiraje": c_tir})

        c_man = ((seg_man/3600)*18*qp_taller) + (qp_taller*dif_ud) + sum(PRECIOS["extras"][e["n"]]*e["q"]*qp_taller for e in l_ex)
        t_fab = sum(sum(v for k,v in part.items() if k!="Pieza") for part in det_partidas) + c_man
        desc_full[q_n] = {"det": det_partidas, "man": c_man, "total": t_fab, "qp": qp_taller}
        res_final.append({"Cant": q_n, "Taller": qp_taller, "Fab": f"{t_fab:.2f}€", "Total": f"{t_fab*margen:.2f}€", "Ud": f"{(t_fab*margen/q_n):.2f}€"})

# --- SALIDA DASHBOARD ---
if res_final:
    st.header("📊 Cuadro de Resultados")
    for r in res_final:
        with st.container():
            col_a, col_b, col_c = st.columns(3)
            col_a.metric(f"Cantidad: {r['Cant']} uds", r['Ud'], "PVP Unitario")
            col_b.metric("PVP Total Proyecto", r['Total'])
            col_c.metric("Unidades en Taller", int(r['Taller']), "con mermas")
            
            with st.expander("🔍 Ver Desglose Técnico de Costes"):
                st.table(pd.DataFrame(desc_full[r['Cant']]["det"]).style.format("{:.2f}€", subset=pd.DataFrame(desc_full[r['Cant']]["det"]).columns[1:]))
                st.write(f"**Montaje y Accesorios:** {desc_full[r['Cant']]['man']:.2f}€")
                st.write(f"**Margen Comercial:** x{margen}")
    
    st.divider()
    if st.button("📄 GENERAR OFERTA COMERCIAL (PDF)"):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 18); pdf.cell(190, 10, "OFERTA COMERCIAL - MAINSA PLV", ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("Helvetica", "B", 12); pdf.cell(190, 10, "1. ESPECIFICACIONES TÉCNICAS", ln=True)
            pdf.set_font("Helvetica", "", 10)
            for d in datos_pz: pdf.cell(190, 7, f"- {d['nombre']}: {d['w']}x{d['h']}mm | Impresion: {d['im']}", ln=True)
            pdf.ln(10); pdf.set_font("Helvetica", "B", 12); pdf.cell(190, 10, "2. ESCALA DE PRECIOS", ln=True)
            pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
            pdf.cell(60, 10, "Cantidad", 1, 0, 'C', True); pdf.cell(60, 10, "PVP Total", 1, 0, 'C', True); pdf.cell(60, 10, "PVP Unitario", 1, 1, 'C', True)
            pdf.set_font("Helvetica", "", 10)
            for r in res_final:
                pdf.cell(60, 10, str(r['Cant']), 1, 0, 'C'); pdf.cell(60, 10, r['Total'], 1, 0, 'C'); pdf.cell(60, 10, r['Ud'], 1, 1, 'C')
            st.download_button("📩 Descargar PDF", data=bytes(pdf.output()), file_name="Oferta_Mainsa.pdf")
        except Exception as e: st.error(f"Error PDF: Asegúrate de tener 'fpdf2' en requirements.txt. Detalle: {e}")
