import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PRECIOS ---
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
        "Sin Peliculado": 0, "Polipropileno": 0.26, "Poliéster brillo": 0.38, "Poliéster mate": 0.64
    },
    "laminado_digital": 3.5,
    "extras": {
        "CINTA D/CARA": 0.26, "CINTA LOHMAN": 0.49, "CINTA GEL": 1.2,
        "GOMA TERMINALES": 0.079, "IMAN 20x2mm": 1.145, "TUBOS": 1.06,
        "REMACHES": 0.049, "VELCRO": 0.43, "PUNTO ADHESIVO": 0.08
    }
}

def calcular_mermas(n, es_digital=False):
    if es_digital: return n * 0.10, 0 # 10% fijo para digital
    if n < 100: return 15, 135
    if n < 200: return 30, 150
    if n < 600: return 40, 160
    if n < 1000: return 50, 170
    if n < 2000: return 60, 170
    return 120, 170

st.set_page_config(page_title="MAINSA PLV - PRO", layout="wide")

# Estilo para una interfaz más profesional
st.markdown("""
<style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { background: white; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; }
    .commercial-card { background: #ffffff; padding: 30px; border-radius: 15px; border: 2px solid #1f77b4; }
</style>
""", unsafe_allow_html=True)

st.title("📦 Escandallos Profesionales MAINSA PLV")

# --- GESTIÓN DE PIEZAS ---
if 'ids' not in st.session_state: st.session_state.ids = [0]

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_str = st.text_input("Cantidades", "200, 500, 1000")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    st.divider()
    seg_man = st.number_input("Segundos Manipulación / Ud", value=300)
    dif_ud = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], index=2)
    margen = st.number_input("Multiplicador Comercial", value=2.2, step=0.1)
    st.divider()
    modo_comercial = st.checkbox("🌟 ACTIVAR MODO COMERCIAL", value=False)

# --- BOTONES CONTROL ---
if not modo_comercial:
    c1, c2 = st.columns([1, 5])
    if c1.button("➕ Añadir Forma"):
        st.session_state.ids.append(max(st.session_state.ids) + 1)
        st.rerun()
    if c2.button("🗑 Reiniciar Todo"):
        st.session_state.ids = [0]; st.rerun()

datos_pz = []; ids_del = []
for i_id in st.session_state.ids:
    if modo_comercial:
        # En modo comercial solo guardamos los datos, no mostramos editores
        pass 
    else:
        with st.expander(f"🛠 Configuración Forma {i_id + 1}", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                nom = st.text_input("Nombre", f"Pieza {i_id+1}", key=f"n_{i_id}")
                pliegos = st.number_input("Pliegos/Mueble", 0.0, 100.0, 1.0, 0.1, key=f"p_{i_id}")
                w = st.number_input("Ancho (mm)", 1, 5000, 700, key=f"w_{i_id}")
                h = st.number_input("Largo (mm)", 1, 5000, 1000, key=f"h_{i_id}")
            with col2:
                pf = st.selectbox("C. Frontal", list(PRECIOS["cartoncillo"].keys()), 1, key=f"pf_{i_id}")
                gf = st.number_input("G. Frontal", PRECIOS["cartoncillo"][pf]["gramaje"], key=f"gf_{i_id}") if pf != "Ninguno" else 0
                pl = st.selectbox("Plancha", list(PRECIOS["planchas"].keys()), key=f"pl_{i_id}")
                ap = st.selectbox("Calidad", ["C/C", "B/C", "B/B"], 1, key=f"ap_{i_id}") if pl != "Ninguna" else "C/C"
                pd_s = st.selectbox("C. Dorso", list(PRECIOS["cartoncillo"].keys()), key=f"pd_{i_id}")
                gd_s = st.number_input("G. Dorso", PRECIOS["cartoncillo"][pd_s]["gramaje"], key=f"gd_{i_id}") if pd_s != "Ninguno" else 0
            with col3:
                im = st.selectbox("Impresión", ["Offset", "Digital", "No"], key=f"im_{i_id}")
                nt = st.number_input("Tintas", 1, 6, 4, key=f"nt_{i_id}") if im == "Offset" else 0
                ba = st.checkbox("Barniz", key=f"ba_{i_id}") if im == "Offset" else False
                ld = st.checkbox("Laminado Digital", key=f"ld_{i_id}") if im == "Digital" else False
                pel = st.selectbox("Peliculado", list(PRECIOS["peliculado"].keys()), index=(0 if im=="Digital" else 1), key=f"pel_{i_id}")
                cor = st.selectbox("Corte", ["Troquelado", "Plotter"], key=f"cor_{i_id}")
                if st.button("🗑 Borrar", key=f"del_{i_id}"): ids_del.append(i_id)
            
            datos_pz.append({"id": i_id, "nombre": nom, "pliegos": pliegos, "w": w, "h": h, "pf": pf, "gf": gf, "pl": pl, "ap": ap, "pd": pd_s, "gd": gd_s, "im": im, "nt": nt, "ba": ba, "ld": ld, "pel": pel, "cor": cor})

for d_id in ids_del: st.session_state.ids.remove(d_id); st.rerun()

# --- CÁLCULOS ---
res_final = []; desc_q = {}
if lista_cants and datos_pz:
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
                pas = (1 if p["pf"]!="Ninguno" else 0) + (1 if p["pd"]!="Ninguno" else 0)
                c_con = hp * m2 * PRECIOS["planchas"][p["pl"]]["peg"] * pas
            
            c_imp = (nb*m2*6.5) if p["im"] == "Digital" else (0.0 if p["im"] == "No" else (60 if nb<100 else (60+0.15*(nb-100) if nb<500 else (120 if nb<=2000 else 120+0.015*(nb-2000)))) * (p["nt"] + (1 if p["ba"] else 0)))
            c_acab = (hp*m2*PRECIOS["peliculado"][p["pel"]]) + (hp*m2*PRECIOS["laminado_digital"] if p["ld"] else 0)
            c_arr, c_tir = 0.0, (hp*1.5 if p["cor"]=="Plotter" else 0.0)
            if p["cor"] == "Troquelado":
                c_arr = 107.7 if (p['h']>1000 or p['w']>700) else (80.77 if (p['h']==1000 and p['w']==700) else 48.19)
                c_tir = hp * (0.135 if (p['h']>1000 or p['w']>700) else (0.09 if (p['h']==1000 and p['w']==700) else 0.06))
            
            det_partidas.append({"Pieza": p["nombre"], "Carton": c_cart, "Plancha": c_plan, "Contra": c_con, "Imp": c_imp, "Acab": c_acab, "Arreglo": c_arr, "Tiraje": c_tir})

        c_man = ((seg_man/3600)*18*qp_taller) + (qp_taller*dif_ud)
        t_fab = sum(sum(v for k,v in part.items() if k!="Pieza") for part in det_partidas) + c_man
        desc_q[q_n] = {"det": det_partidas, "man": c_man, "total": t_fab, "qp": qp_taller}
        res_final.append({"Cant": q_n, "Ud": f"{(t_fab*margen/q_n):.2f}€", "Total": f"{(t_fab*margen):.2f}€"})

# --- VISTA DE SALIDA ---
if modo_comercial:
    st.markdown(f"""
    <div class="commercial-card">
        <h2 style='text-align: center; color: #1f77b4;'>OFERTA COMERCIAL - MAINSA PLV</h2>
        <hr>
        <h4>1. Formatos y Componentes</h4>
        <ul>
            {" ".join([f"<li><b>{p['nombre']}:</b> {p['w']}x{p['h']} mm - {p['im']}</li>" for p in datos_pz])}
        </ul>
        <br>
        <h4>2. Escala de Precios de Venta</h4>
        <table style='width:100%; border-collapse: collapse;'>
            <tr style='background-color: #1f77b4; color: white;'>
                <th style='padding: 10px; border: 1px solid #ddd;'>Cantidad</th>
                <th style='padding: 10px; border: 1px solid #ddd;'>PVP Total</th>
                <th style='padding: 10px; border: 1px solid #ddd;'>Precio Unitario</th>
            </tr>
            {" ".join([f"<tr><td style='padding: 10px; border: 1px solid #ddd; text-align: center;'>{r['Cant']} uds</td><td style='padding: 10px; border: 1px solid #ddd; text-align: center;'>{r['Total']}</td><td style='padding: 10px; border: 1px solid #ddd; text-align: center;'><b>{r['Ud']}</b></td></tr>" for r in res_final])}
        </table>
        <p style='font-size: 0.8em; color: gray; margin-top: 20px;'>* Precios sin IVA. Validez del presupuesto: 15 días.</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("💡 Consejo: Pulsa Ctrl+P (o Cmd+P en Mac) para guardar esta oferta como PDF.")
else:
    if res_final:
        st.header("📊 Resumen Técnico")
        cols = st.columns(len(res_final))
        for idx, r in enumerate(res_final):
            cols[idx].metric(f"{r['Cant']} uds", r['Ud'], "PVP/ud")
        
        for q, i in desc_q.items():
            with st.expander(f"🔍 Desglose Técnico {q} uds"):
                st.table(pd.DataFrame(i["det"]).style.format("{:.2f}€", subset=pd.DataFrame(i["det"]).columns[1:]))
                st.write(f"**Manipulación y Merma Taller:** {i['man']:.2f}€ | **Total Fab:** {i['total']:.2f}€")
