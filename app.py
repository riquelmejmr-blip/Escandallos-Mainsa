import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN Y PRECIOS ---
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
        "CINTA D/CARA normal": 0.26, "CINTA LOHMAN 20mm": 0.33, "CINTA LOHMAN 35mm": 0.49,
        "CINTA GEL ROJA": 0.45, "CINTA GEL TESA": 1.2, "GOMA TERMINALES": 0.079,
        "IMAN 20x2mm": 1.145, "Tubos 30mm": 0.93, "Tubos 60mm": 1.06,
        "Bridas": 0.13, "REMACHES": 0.049, "VELCRO TIRA": 0.43, "PUNTO ADHESIVO": 0.08,
        "PIEZA Harrison 867696": 0.09, "PIEZA Harrison 867702": 0.172
    }
}

def calcular_mermas(n, es_digital=False):
    if es_digital:
        return n * 0.10, 0 # 10% Fijo
    if n < 100: return 15, 135
    if n < 200: return 30, 150
    if n < 600: return 40, 160
    if n < 1000: return 50, 170
    if n < 2000: return 60, 170
    return 120, 170

st.set_page_config(page_title="MAINSA PLV - Escandallos", layout="wide")
st.title("📦 Escandallos MAINSA PLV")

# --- GESTIÓN DE PIEZAS ---
if 'piezas_ids' not in st.session_state:
    st.session_state.piezas_ids = [0]

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_str = st.text_input("Cantidades (ej: 200, 500)", "200")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    st.divider()
    seg_man = st.number_input("Segundos Manipulación / Unidad", value=300)
    dif_ud = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], index=2, format_func=lambda x: f"{x}€")
    margen = st.number_input("Multiplicador Comercial", value=2.2)

# --- BOTONES CONTROL ---
c1, c2 = st.columns([1, 6])
if c1.button("➕ Añadir Pieza"):
    st.session_state.piezas_ids.append(max(st.session_state.piezas_ids) + 1)
    st.rerun()
if c2.button("🗑 Reiniciar Todo"):
    st.session_state.piezas_ids = [0]
    st.rerun()

datos_pz = []
ids_to_del = []

for i_id in st.session_state.piezas_ids:
    with st.expander(f"Configuración Forma (ID: {i_id})", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            nom = st.text_input("Nombre Pieza", f"Parte {i_id+1}", key=f"n_{i_id}")
            pliegos = st.number_input("Pliegos/Mueble", 0.0, 100.0, 1.0, 0.1, key=f"p_{i_id}")
            w = st.number_input("Ancho (mm)", 1, 5000, 700, key=f"w_{i_id}")
            h = st.number_input("Largo (mm)", 1, 5000, 1000, key=f"h_{i_id}")
        with col2:
            pf = st.selectbox("C. Frontal", list(PRECIOS["cartoncillo"].keys()), 1, key=f"pf_{i_id}")
            gf = st.number_input("G. Frontal", PRECIOS["cartoncillo"][pf]["gramaje"], key=f"gf_{i_id}") if pf != "Ninguno" else 0
            pl = st.selectbox("Plancha Base", list(PRECIOS["planchas"].keys()), key=f"pl_{i_id}")
            ap = st.selectbox("Calidad", ["C/C", "B/C", "B/B"], 1, key=f"ap_{i_id}") if pl != "Ninguna" else "C/C"
            pd_s = st.selectbox("C. Dorso", list(PRECIOS["cartoncillo"].keys()), key=f"pd_{i_id}")
            gd_s = st.number_input("G. Dorso", PRECIOS["cartoncillo"][pd_s]["gramaje"], key=f"gd_{i_id}") if pd_s != "Ninguno" else 0
        with col3:
            im = st.selectbox("Imp. Frontal", ["Offset", "Digital", "No"], key=f"im_{i_id}")
            nt = st.number_input("Tintas F.", 1, 6, 4, key=f"nt_{i_id}") if im == "Offset" else 0
            ba = st.checkbox("Barniz F.", key=f"ba_{i_id}") if im == "Offset" else False
            ld = st.checkbox("Laminado Digital (3.5€/m2)", key=f"ld_{i_id}") if im == "Digital" else False
            pel = st.selectbox("Peliculado", list(PRECIOS["peliculado"].keys()), index=(0 if im=="Digital" else 1), key=f"pel_{i_id}")
            cor = st.selectbox("Corte", ["Troquelado", "Plotter"], key=f"cor_{i_id}")
            if st.button("🗑 Borrar Pieza", key=f"del_{i_id}"): ids_to_del.append(i_id)
        
        datos_pz.append({"id": i_id, "nombre": nom, "pliegos": pliegos, "w": w, "h": h, "pf": pf, "gf": gf, "pl": pl, "ap": ap, "pd": pd_s, "gd": gd_s, "im": im, "nt": nt, "ba": ba, "ld": ld, "pel": pel, "cor": cor})

for d_id in ids_to_del:
    st.session_state.piezas_ids.remove(d_id)
    st.rerun()

# --- ACCESORIOS ---
st.divider()
sel_ex = st.multiselect("Accesorios de Manipulación", list(PRECIOS["extras"].keys()))
l_ex = []
if sel_ex:
    cols = st.columns(len(sel_ex))
    for j, n in enumerate(sel_ex):
        q = cols[j].number_input(f"Cant. {n}/ud", 1.0, key=f"ex_{j}")
        l_ex.append({"n": n, "q": q})

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
                pas = (1 if p["pf"]!="Ninguno" else 0) + (1 if p["pd"]!="Ninguno" else 0)
                c_con = hp * m2 * PRECIOS["planchas"][p["pl"]]["peg"] * pas
            
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
            
            det_partidas.append({"Pieza": p["nombre"], "Cartoncillo": c_cart, "Plancha": c_plan, "Contra.": c_con, "Imp.": c_imp, "Acabado": c_acab, "Arreglo": c_arr, "Tiraje": c_tir})

        c_man = ((seg_man/3600)*18*qp_taller) + (qp_taller*dif_ud) + sum(PRECIOS["extras"][e["n"]]*e["q"]*qp_taller for e in l_ex)
        t_fab = sum(sum(v for k,v in part.items() if k!="Pieza") for part in det_partidas) + c_man
        desc_full[q_n] = {"det": det_partidas, "man": c_man, "total": t_fab, "qp": qp_taller}
        res_final.append({"Cant": q_n, "Taller": qp_taller, "Coste Fab": f"{t_fab:.2f}€", "PV Total": f"{t_fab*margen:.2f}€", "PV Ud": f"{(t_fab*margen/q_n):.2f}€"})

# --- SALIDA ---
if res_final:
    st.header("📊 Resumen Escandallo")
    st.dataframe(pd.DataFrame(res_final), use_container_width=True)
    
    for q, i in desc_full.items():
        with st.expander(f"🔍 Desglose Técnico {q} uds"):
            st.table(pd.DataFrame(i["det"]).style.format("{:.2f}€", subset=pd.DataFrame(i["det"]).columns[1:]))
            st.write(f"**Manipulación y Extras (sobre {i['qp']} uds):** {i['man']:.2f} €")
            st.write(f"**COSTE TOTAL FABRICACIÓN:** {i['total']:.2f} €")

    st.divider()
    st.subheader("📝 Exportar Oferta Comercial")
    # Generar un CSV con formato que Excel entiende
    csv_data = "CANTIDAD;PVP TOTAL;PVP UNITARIO\n"
    for r in res_final:
        csv_data += f"{r['Cant']};{r['PV Total']};{r['PV Ud']}\n"
    
    st.download_button("Descargar Resumen Comercial (Excel)", data=csv_data, file_name="Oferta_Mainsa_PLV.csv", mime="text/csv")
else:
    st.info("Introduce datos para calcular.")
