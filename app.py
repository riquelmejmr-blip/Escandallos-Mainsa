import streamlit as st
import pandas as pd

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
    return 120, 170

st.set_page_config(page_title="PLV Pro Calc", layout="wide")
st.title("🛠 Calculadora PLV - Escalado y Desglose")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_input = st.text_input("Cantidades (separadas por comas)", "200, 500, 1000")
    lista_cants = [int(x.strip()) for x in cants_input.split(",") if x.strip().isdigit()]
    
    st.divider()
    min_manip = st.number_input("Minutos Manipulación / Mueble", value=15)
    dificultad_val = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], format_func=lambda x: f"{x} €")
    multiplicador = st.number_input("Multiplicador Comercial", value=2.2)

# --- PIEZAS ---
if 'num_piezas' not in st.session_state: st.session_state.num_piezas = 1

col_btn1, col_btn2 = st.columns([1, 5])
if col_btn1.button("➕ Añadir Pieza"): st.session_state.num_piezas += 1
if col_btn2.button("🗑 Reiniciar"): st.session_state.num_piezas = 1

datos_piezas = []
for i in range(st.session_state.num_piezas):
    with st.expander(f"Configuración Pieza #{i+1}", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            pm = st.number_input(f"Pliegos/Mueble", value=1, key=f"pm{i}")
            an = st.number_input(f"Ancho (mm)", value=700, key=f"an{i}")
            la = st.number_input(f"Largo (mm)", value=1000, key=f"la{i}")
        with c2:
            pf = st.selectbox(f"Cartoncillo Frontal", list(PRECIOS["cartoncillo"].keys()), index=1, key=f"pf{i}")
            gf = st.number_input(f"Gramaje Frontal", value=PRECIOS["cartoncillo"][pf]["gramaje"], key=f"gf{i}")
            pl = st.selectbox(f"Plancha Base", list(PRECIOS["planchas"].keys()), key=f"pl{i}")
            ap = st.selectbox(f"Calidad Plancha", ["C/C", "B/C", "B/B"], key=f"ap{i}") if pl != "Ninguna" and "AC" not in pl else "C/C"
            pd_sel = st.selectbox(f"Cartoncillo Dorso", list(PRECIOS["cartoncillo"].keys()), key=f"pd{i}")
            gd = st.number_input(f"Gramaje Dorso", value=PRECIOS["cartoncillo"][pd_sel]["gramaje"], key=f"gd{i}")
        with c3:
            im = st.selectbox(f"Impresión", ["Digital", "Offset", "No"], key=f"im{i}")
            nt = st.number_input(f"Tintas", 1, 6, 4, key=f"nt{i}") if im == "Offset" else 0
            ba = st.checkbox(f"Barniz", key=f"ba{i}") if im == "Offset" else False
            pe = st.selectbox(f"Peliculado", list(PRECIOS["peliculado"].keys()), key=f"pe{i}")
            co = st.selectbox(f"Corte", ["Troquelado", "Plotter"], key=f"co{i}")
        
        datos_piezas.append({"p": pm, "w": an, "h": la, "pf": pf, "gf": gf, "pla": pl, "acab": ap, "pd": pd_sel, "gd": gd, "imp": im, "nt": nt, "bar": ba, "pel": pe, "cor": co})

# --- EXTRAS ---
st.divider()
extras_sel = st.multiselect("Accesorios de Manipulación", list(PRECIOS["extras"].keys()))
datos_extras = []
if extras_sel:
    cols_ex = st.columns(len(extras_sel))
    for idx, ex_name in enumerate(extras_sel):
        q_ex = cols_ex[idx].number_input(f"Cant. {ex_name}/ud", value=1.0, key=f"ex{idx}")
        datos_extras.append({"nombre": ex_name, "cantidad": q_ex})

# --- CÁLCULOS ---
res_final = []
desgloses = {}

for q_f in lista_cants:
    det = {"Materiales": 0.0, "Impresión": 0.0, "Acabado": 0.0, "Corte": 0.0, "Manipulación": 0.0}
    
    for pz in datos_piezas:
        nb = q_f * pz["p"]
        mn, mi = obtener_mermas(nb)
        h_pap = nb + mn + mi
        h_pro = nb + mn
        m2 = (pz["w"] * pz["h"]) / 1_000_000
        
        # 1. Materiales
        cp1 = h_pap * m2 * (pz["gf"]/1000) * PRECIOS["cartoncillo"][pz["pf"]]["precio_kg"]
        cp2 = h_pap * m2 * (pz["gd"]/1000) * PRECIOS["cartoncillo"][pz["pd"]]["precio_kg"]
        cpl = (h_pro * m2 * PRECIOS["planchas"][pz["pla"]][pz["acab"]]) if pz["pla"] != "Ninguna" else 0
        pasa = (1 if pz["pf"] != "Ninguno" else 0) + (1 if pz["pd"] != "Ninguno" else 0)
        ccn = (h_pro * m2 * PRECIOS["planchas"][pz["pla"]]["peg"] * pasa) if pz["pla"] != "Ninguna" else 0
        det["Materiales"] += (cp1 + cp2 + cpl + ccn)
        
        # 2. Impresión
        if pz["imp"] == "Digital": det["Impresión"] += (h_pap * m2 * 6.5)
        elif pz["imp"] == "Offset":
            base = 60 if h_pap < 100 else (60 + 0.15*(h_pap-100) if h_pap < 500 else (120 if h_pap <= 2000 else 120 + 0.015*(h_pap-2000)))
            det["Impresión"] += (base * (pz["nt"] + (1 if pz["bar"] else 0)))
            
        # 3. Acabado
        det["Acabado"] += (h_pro * m2 * PRECIOS["peliculado"][pz["pel"]])
        
        # 4. Corte
        if pz["cor"] == "Troquelado":
            ft = 107.7 if (pz["h"] > 1000 or pz["w"] > 700) else (80.77 if (pz["h"] == 1000 and pz["w"] == 700) else 48.19)
            vt = 0.135 if (pz["h"] > 1000 or pz["w"] > 700) else (0.09 if (pz["h"] == 1000 and pz["w"] == 700) else 0.06)
            det["Corte"] += (ft + h_pro * vt)
        else: det["Corte"] += (h_pro * 1.5)

    # 5. Manipulación y Extras
    cex = sum(PRECIOS["extras"][e["nombre"]] * e["cantidad"] * q_f for e in datos_extras)
    det["Manipulación"] = ((min_manip/60)*18*q_f) + (q_f*dificultad_val) + cex
    
    coste_f = sum(det.values())
    desgloses[q_f] = det
    res_final.append({"Cantidad": q_f, "Coste Fab": f"{coste_f:.2f}€", "PV Total": f"{coste_f*multiplicador:.2f}€", "Unidad": f"{(coste_f*multiplicador/q_f):.2f}€"})

# --- TABLA Y DESGLOSE ---
st.header("📊 Escalado de Precios")
st.table(pd.DataFrame(res_final))

st.header("🔍 Desglose por Partidas")
for q, d in desgloses.items():
    with st.expander(f"Ver detalle: {q} unidades"):
        df_d = pd.DataFrame(list(d.items()), columns=["Partida", "Coste (€)"])
        st.table(df_d)
        st.write(f"**Beneficio Bruto Estimado:** {(sum(d.values())*(multiplicador-1)):.2f} €")
