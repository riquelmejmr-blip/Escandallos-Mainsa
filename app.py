import streamlit as st
import pandas as pd

# --- PRECIOS Y CONFIGURACIÓN ---
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
        "Microcanal": {"C/C": 0.684, "B/C": 0.726, "B/B": 0.819, "peg": 0.217},
        "Canal 3": {"C/C": 0.684, "B/C": 0.726, "B/B": 0.819, "peg": 0.217},
        "Doble de Micro": {"C/C": 1.129, "B/C": 1.149, "B/B": 1.251, "peg": 0.263},
        "Doble Doble": {"C/C": 1.129, "B/C": 1.149, "B/B": 1.251, "peg": 0.263},
        "AC (Cuero/Cuero)": {"C/C": 2.505, "peg": 0.217}
    },
    "peliculado": {
        "Sin Peliculado": 0,
        "Polipropileno": 0.26,
        "Poliéster brillo": 0.38,
        "Poliéster mate": 0.64
    },
    "extras": {
        "CINTA D/CARA normal": 0.26, "CINTA LOHMAN 20mm": 0.33, "CINTA LOHMAN 35mm": 0.49,
        "CINTA GEL ROJA": 0.45, "CINTA GEL TESA": 1.2, "GOMA TERMINALES": 0.079,
        "IMAN 20x2mm": 1.145, "Tubos 30mm": 0.93, "Tubos 60mm": 1.06,
        "Bridas": 0.13, "REMACHES": 0.049, "VELCRO TIRA": 0.43, "PUNTO ADHESIVO": 0.08,
        "PIEZA Harrison 867696": 0.09, "PIEZA Harrison 867702": 0.172
    }
}

def obtener_mermas(n):
    if n < 100: return 15, 135
    if n < 200: return 30, 150
    if n < 600: return 40, 160
    if n < 1000: return 50, 170
    if n < 2000: return 60, 170
    if n < 3000: return 100, 170
    return 120, 170

st.set_page_config(page_title="Calculadora PLV Expert", layout="wide")
st.title("🚀 Escandallos Profesionales PLV")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_in = st.text_input("Cantidades (ej: 200, 500, 1000)", "200")
    lista_cants = [int(x.strip()) for x in cants_in.split(",") if x.strip().isdigit()]
    
    st.divider()
    minutos_mueble = st.number_input("Minutos Manipulación / Unidad", value=5)
    dif_ud = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], index=2, format_func=lambda x: f"{x}€ (Difícil)" if x==0.091 else f"{x}€")
    margen = st.number_input("Multiplicador Comercial", value=2.2)

# --- PIEZAS ---
if 'npz' not in st.session_state: st.session_state.npz = 1
col1, col2 = st.columns([1, 6])
if col1.button("➕ Pieza"): st.session_state.npz += 1
if col2.button("🗑 Reset"): st.session_state.npz = 1

datos = []
for i in range(st.session_state.npz):
    with st.expander(f"Forma #{i+1}", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            pz_m = st.number_input("Pliegos por Mueble", 1, key=f"pm{i}")
            w = st.number_input("Ancho (mm)", 700, key=f"w{i}")
            h = st.number_input("Largo (mm)", 1000, key=f"h{i}")
        with c2:
            pf = st.selectbox("C. Frontal", list(PRECIOS["cartoncillo"].keys()), index=1, key=f"pf{i}")
            gf = st.number_input("Gramaje F.", PRECIOS["cartoncillo"][pf]["gramaje"], key=f"gf{i}")
            pl = st.selectbox("Plancha", list(PRECIOS["planchas"].keys()), key=f"pl{i}")
            ap = st.selectbox("Calidad", ["C/C", "B/C", "B/B"], index=1, key=f"ap{i}") if pl != "Ninguna" and "AC" not in pl else "C/C"
            pd = st.selectbox("C. Dorso", list(PRECIOS["cartoncillo"].keys()), index=0, key=f"pd{i}")
            gd = st.number_input("Gramaje D.", PRECIOS["cartoncillo"][pd]["gramaje"], key=f"gd{i}")
        with c3:
            im = st.selectbox("Impresión", ["Offset", "Digital", "No"], index=0, key=f"im{i}")
            nt = st.number_input("Tintas", 1, 6, 4, key=f"nt{i}") if im == "Offset" else 0
            ba = st.checkbox("Barniz", key=f"ba{i}") if im == "Offset" else False
            pe = st.selectbox("Peliculado", list(PRECIOS["peliculado"].keys()), index=1, key=f"pe{i}")
            co = st.selectbox("Corte", ["Troquelado", "Plotter"], index=0, key=f"co{i}")
        datos.append({"p":pz_m,"w":w,"h":h,"pf":pf,"gf":gf,"pl":pl,"ap":ap,"pd":pd,"gd":gd,"im":im,"nt":nt,"ba":ba,"pe":pe,"co":co})

# --- ACCESORIOS ---
st.divider()
acc_sel = st.multiselect("Accesorios", list(PRECIOS["extras"].keys()))
d_acc = []
if acc_sel:
    c_acc = st.columns(len(acc_sel))
    for j, name in enumerate(acc_sel):
        q_acc = c_acc[j].number_input(f"Cant. {name}/ud", 1.0, key=f"acc{j}")
        d_acc.append({"n": name, "q": q_acc})

# --- CÁLCULOS ---
res_esc = []
det_cant = {}

for q in lista_cants:
    pz_detalles = []
    total_q = 0.0
    
    for i, pz in enumerate(datos):
        nb = q * pz["p"]
        mn, mi = obtener_mermas(nb)
        hp = nb + mn + mi
        hpro = nb + mn
        m2 = (pz["w"] * pz["h"]) / 1_000_000
        
        # Mat
        c_mat = (hp * m2 * (pz["gf"]/1000) * PRECIOS["cartoncillo"][pz["pf"]]["precio_kg"]) + \
                (hp * m2 * (pz["gd"]/1000) * PRECIOS["cartoncillo"][pz["pd"]]["precio_kg"])
        if pz["pl"] != "Ninguna":
            c_mat += (hpro * m2 * PRECIOS["planchas"][pz["pl"]][pz["ap"]])
            pas = (1 if pz["pf"] != "Ninguno" else 0) + (1 if pz["pd"] != "Ninguno" else 0)
            c_mat += (hpro * m2 * PRECIOS["planchas"][pz["pl"]]["peg"] * pas)
            
        # Imp
        c_imp = 0
        if pz["im"] == "Digital": c_imp = nb * m2 * 6.5
        elif pz["im"] == "Offset":
            base = 60 if nb < 100 else (60 + 0.15*(nb-100) if nb < 500 else (120 if nb <= 2000 else 120 + 0.015*(nb-2000)))
            c_imp = base * (pz["nt"] + (1 if pz["ba"] else 0))
            
        # Acab & Corte
        c_pe = hpro * m2 * PRECIOS["peliculado"][pz["pe"]]
        if pz["co"] == "Troquelado":
            ft = 107.7 if (pz["h"] > 1000 or pz["w"] > 700) else (80.77 if (pz["h"] == 1000 and pz["w"] == 700) else 48.19)
            vt = 0.135 if (pz["h"] > 1000 or pz["w"] > 700) else (0.09 if (pz["h"] == 1000 and pz["w"] == 700) else 0.06)
            c_co = ft + hpro * vt
        else: c_co = hpro * 1.5
        
        pz_coste = c_mat + c_imp + c_pe + c_co
        total_q += pz_coste
        pz_detalles.append({"Pieza": i+1, "Mat": c_mat, "Imp": c_imp, "Acab": c_pe, "Corte": c_co, "Total": pz_coste})

    # Manip
    c_man = ((minutos_mueble/60)*18*q) + (q*dif_ud) + sum(PRECIOS["extras"][e["n"]] * e["q"] * q for e in d_acc)
    total_proy = total_q + c_man
    
    det_cant[q] = {"piezas": pz_detalles, "manip": c_man, "total": total_proy}
    res_esc.append({"Q": q, "Fabricación": f"{total_proy:.2f}€", "Venta Total": f"{total_proy*margen:.2f}€", "Unitario": f"{(total_proy*margen/q):.2f}€"})

# --- RESULTADOS ---
st.header("📊 Resultado del Escandallo")
st.table(pd.DataFrame(res_esc))

for q, info in det_cant.items():
    with st.expander(f"🔍 Desglose Técnico para {q} unidades"):
        st.write("**Coste por cada Pieza/Forma:**")
        st.table(pd.DataFrame(info["piezas"]).style.format("{:.2f}€", subset=["Mat", "Imp", "Acab", "Corte", "Total"]))
        st.write(f"**Mano de Obra y Accesorios:** {info['manip']:.2f} €")
        st.write(f"**COSTE TOTAL FABRICACIÓN:** {info['total']:.2f} €")
        st.write(f"**PVP FINAL (x{margen}): {(info['total']*margen):.2f} €**")
