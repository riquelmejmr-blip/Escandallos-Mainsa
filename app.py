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

st.set_page_config(page_title="PLV Expert Pro", layout="wide")
st.title("🛠 Calculadora de Costes PLV")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_input = st.text_input("Cantidades (separadas por comas)", "200, 500, 1000")
    lista_cants = [int(x.strip()) for x in cants_input.split(",") if x.strip().isdigit()]
    st.divider()
    min_manip = st.number_input("Minutos Manipulación / Mueble", value=15)
    dif_val = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], format_func=lambda x: f"{x} €")
    mult = st.number_input("Multiplicador Comercial", value=2.2)

# --- PIEZAS ---
if 'n_piezas' not in st.session_state: st.session_state.n_piezas = 1
colb1, colb2 = st.columns([1, 5])
if colb1.button("➕ Pieza"): st.session_state.n_piezas += 1
if colb2.button("🗑 Reset"): st.session_state.n_piezas = 1

datos_piezas = []
for i in range(st.session_state.n_piezas):
    with st.expander(f"Pieza #{i+1}", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            pm = st.number_input(f"Pliegos/Mueble", 1, key=f"pm{i}")
            an = st.number_input(f"Ancho (mm)", 700, key=f"an{i}")
            la = st.number_input(f"Largo (mm)", 1000, key=f"la{i}")
        with c2:
            pf = st.selectbox(f"C. Frontal", list(PRECIOS["cartoncillo"].keys()), 1, key=f"pf{i}")
            gf = st.number_input(f"Gramaje F.", PRECIOS["cartoncillo"][pf]["gramaje"], key=f"gf{i}")
            pl = st.selectbox(f"Plancha", list(PRECIOS["planchas"].keys()), key=f"pl{i}")
            ap = st.selectbox(f"Calidad", ["C/C", "B/C", "B/B"], key=f"ap{i}") if pl != "Ninguna" and "AC" not in pl else "C/C"
            pd = st.selectbox(f"C. Dorso", list(PRECIOS["cartoncillo"].keys()), key=f"pd{i}")
            gd = st.number_input(f"Gramaje D.", PRECIOS["cartoncillo"][pd]["gramaje"], key=f"gd{i}")
        with c3:
            im = st.selectbox(f"Impresión", ["Offset", "Digital", "No"], key=f"im{i}")
            nt = st.number_input(f"Tintas", 1, 6, 4, key=f"nt{i}") if im == "Offset" else 0
            ba = st.checkbox(f"Barniz", key=f"ba{i}") if im == "Offset" else False
            pe = st.selectbox(f"Peliculado", list(PRECIOS["peliculado"].keys()), key=f"pe{i}")
            co = st.selectbox(f"Corte", ["Troquelado", "Plotter"], key=f"co{i}")
        datos_piezas.append({"p":pm,"w":an,"h":la,"pf":pf,"gf":gf,"pl":pl,"ap":ap,"pd":pd,"gd":gd,"im":im,"nt":nt,"ba":ba,"pe":pe,"co":co})

# --- EXTRAS ---
st.divider()
ex_sel = st.multiselect("Accesorios", list(PRECIOS["extras"].keys()))
d_ex = []
if ex_sel:
    cx = st.columns(len(ex_sel))
    for j, name in enumerate(ex_sel):
        q = cx[j].number_input(f"Cant. {name}/ud", 1.0, key=f"ex{j}")
        d_ex.append({"n": name, "q": q})

# --- CÁLCULOS ---
res = []
desgloses = {}

for q_f in lista_cants:
    d = {"Materiales": 0.0, "Impresión": 0.0, "Acabado": 0.0, "Corte": 0.0, "Manipulación": 0.0}
    for pz in datos_piezas:
        nb = q_f * pz["p"] # HOJAS NETAS
        mn, mi = obtener_mermas(nb)
        hpap = nb + mn + mi # HOJAS COMPRA PAPEL
        hpro = nb + mn      # HOJAS PROCESO
        m2 = (pz["w"] * pz["h"]) / 1_000_000

        # Materiales
        d["Materiales"] += (hpap * m2 * (pz["gf"]/1000) * PRECIOS["cartoncillo"][pz["pf"]]["precio_kg"])
        d["Materiales"] += (hpap * m2 * (pz["gd"]/1000) * PRECIOS["cartoncillo"][pz["pd"]]["precio_kg"])
        if pz["pl"] != "Ninguna":
            d["Materiales"] += (hpro * m2 * PRECIOS["planchas"][pz["pl"]][pz["ap"]])
            pas = (1 if pz["pf"] != "Ninguno" else 0) + (1 if pz["pd"] != "Ninguno" else 0)
            d["Materiales"] += (hpro * m2 * PRECIOS["planchas"][pz["pl"]]["peg"] * pas)

        # Impresión (SOBRE HOJAS NETAS 'nb')
        if pz["im"] == "Digital": d["Impresión"] += (nb * m2 * 6.5)
        elif pz["im"] == "Offset":
            # Usamos 'nb' en lugar de 'hpap' según tu corrección
            base = 60 if nb < 100 else (60 + 0.15*(nb-100) if nb < 500 else (120 if nb <= 2000 else 120 + 0.015*(nb-2000)))
            d["Impresión"] += (base * (pz["nt"] + (1 if pz["ba"] else 0)))

        # Acabado y Corte
        d["Acabado"] += (hpro * m2 * PRECIOS["peliculado"][pz["pe"]])
        if pz["co"] == "Troquelado":
            ft = 107.7 if (pz["h"] > 1000 or pz["w"] > 700) else (80.77 if (pz["h"] == 1000 and pz["w"] == 700) else 48.19)
            vt = 0.135 if (pz["h"] > 1000 or pz["w"] > 700) else (0.09 if (pz["h"] == 1000 and pz["w"] == 700) else 0.06)
            d["Corte"] += (ft + hpro * vt)
        else: d["Corte"] += (hpro * 1.5)

    # Manipulación
    ce = sum(PRECIOS["extras"][e["n"]] * e["q"] * q_f for e in d_ex)
    d["Manipulación"] = ((min_manip/60)*18*q_f) + (q_f*dif_val) + ce
    
    cf = sum(d.values())
    desgloses[q_f] = d
    res.append({"Cantidad": q_f, "C. Fab": f"{cf:.2f}€", "PV Total": f"{cf*mult:.2f}€", "Unidad": f"{(cf*mult/q_f):.2f}€"})

st.header("📊 Escalado")
st.table(pd.DataFrame(res))
for q, de in desgloses.items():
    with st.expander(f"Detalle {q} uds"):
        st.table(pd.DataFrame(list(de.items()), columns=["Partida", "Coste (€)"]))import streamlit as st
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

st.set_page_config(page_title="PLV Expert Pro", layout="wide")
st.title("🛠 Calculadora de Costes PLV")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_input = st.text_input("Cantidades (separadas por comas)", "200, 500, 1000")
    lista_cants = [int(x.strip()) for x in cants_input.split(",") if x.strip().isdigit()]
    st.divider()
    min_manip = st.number_input("Minutos Manipulación / Mueble", value=15)
    dif_val = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], format_func=lambda x: f"{x} €")
    mult = st.number_input("Multiplicador Comercial", value=2.2)

# --- PIEZAS ---
if 'n_piezas' not in st.session_state: st.session_state.n_piezas = 1
colb1, colb2 = st.columns([1, 5])
if colb1.button("➕ Pieza"): st.session_state.n_piezas += 1
if colb2.button("🗑 Reset"): st.session_state.n_piezas = 1

datos_piezas = []
for i in range(st.session_state.n_piezas):
    with st.expander(f"Pieza #{i+1}", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            pm = st.number_input(f"Pliegos/Mueble", 1, key=f"pm{i}")
            an = st.number_input(f"Ancho (mm)", 700, key=f"an{i}")
            la = st.number_input(f"Largo (mm)", 1000, key=f"la{i}")
        with c2:
            pf = st.selectbox(f"C. Frontal", list(PRECIOS["cartoncillo"].keys()), 1, key=f"pf{i}")
            gf = st.number_input(f"Gramaje F.", PRECIOS["cartoncillo"][pf]["gramaje"], key=f"gf{i}")
            pl = st.selectbox(f"Plancha", list(PRECIOS["planchas"].keys()), key=f"pl{i}")
            ap = st.selectbox(f"Calidad", ["C/C", "B/C", "B/B"], key=f"ap{i}") if pl != "Ninguna" and "AC" not in pl else "C/C"
            pd = st.selectbox(f"C. Dorso", list(PRECIOS["cartoncillo"].keys()), key=f"pd{i}")
            gd = st.number_input(f"Gramaje D.", PRECIOS["cartoncillo"][pd]["gramaje"], key=f"gd{i}")
        with c3:
            im = st.selectbox(f"Impresión", ["Offset", "Digital", "No"], key=f"im{i}")
            nt = st.number_input(f"Tintas", 1, 6, 4, key=f"nt{i}") if im == "Offset" else 0
            ba = st.checkbox(f"Barniz", key=f"ba{i}") if im == "Offset" else False
            pe = st.selectbox(f"Peliculado", list(PRECIOS["peliculado"].keys()), key=f"pe{i}")
            co = st.selectbox(f"Corte", ["Troquelado", "Plotter"], key=f"co{i}")
        datos_piezas.append({"p":pm,"w":an,"h":la,"pf":pf,"gf":gf,"pl":pl,"ap":ap,"pd":pd,"gd":gd,"im":im,"nt":nt,"ba":ba,"pe":pe,"co":co})

# --- EXTRAS ---
st.divider()
ex_sel = st.multiselect("Accesorios", list(PRECIOS["extras"].keys()))
d_ex = []
if ex_sel:
    cx = st.columns(len(ex_sel))
    for j, name in enumerate(ex_sel):
        q = cx[j].number_input(f"Cant. {name}/ud", 1.0, key=f"ex{j}")
        d_ex.append({"n": name, "q": q})

# --- CÁLCULOS ---
res = []
desgloses = {}

for q_f in lista_cants:
    d = {"Materiales": 0.0, "Impresión": 0.0, "Acabado": 0.0, "Corte": 0.0, "Manipulación": 0.0}
    for pz in datos_piezas:
        nb = q_f * pz["p"] # HOJAS NETAS
        mn, mi = obtener_mermas(nb)
        hpap = nb + mn + mi # HOJAS COMPRA PAPEL
        hpro = nb + mn      # HOJAS PROCESO
        m2 = (pz["w"] * pz["h"]) / 1_000_000

        # Materiales
        d["Materiales"] += (hpap * m2 * (pz["gf"]/1000) * PRECIOS["cartoncillo"][pz["pf"]]["precio_kg"])
        d["Materiales"] += (hpap * m2 * (pz["gd"]/1000) * PRECIOS["cartoncillo"][pz["pd"]]["precio_kg"])
        if pz["pl"] != "Ninguna":
            d["Materiales"] += (hpro * m2 * PRECIOS["planchas"][pz["pl"]][pz["ap"]])
            pas = (1 if pz["pf"] != "Ninguno" else 0) + (1 if pz["pd"] != "Ninguno" else 0)
            d["Materiales"] += (hpro * m2 * PRECIOS["planchas"][pz["pl"]]["peg"] * pas)

        # Impresión (SOBRE HOJAS NETAS 'nb')
        if pz["im"] == "Digital": d["Impresión"] += (nb * m2 * 6.5)
        elif pz["im"] == "Offset":
            # Usamos 'nb' en lugar de 'hpap' según tu corrección
            base = 60 if nb < 100 else (60 + 0.15*(nb-100) if nb < 500 else (120 if nb <= 2000 else 120 + 0.015*(nb-2000)))
            d["Impresión"] += (base * (pz["nt"] + (1 if pz["ba"] else 0)))

        # Acabado y Corte
        d["Acabado"] += (hpro * m2 * PRECIOS["peliculado"][pz["pe"]])
        if pz["co"] == "Troquelado":
            ft = 107.7 if (pz["h"] > 1000 or pz["w"] > 700) else (80.77 if (pz["h"] == 1000 and pz["w"] == 700) else 48.19)
            vt = 0.135 if (pz["h"] > 1000 or pz["w"] > 700) else (0.09 if (pz["h"] == 1000 and pz["w"] == 700) else 0.06)
            d["Corte"] += (ft + hpro * vt)
        else: d["Corte"] += (hpro * 1.5)

    # Manipulación
    ce = sum(PRECIOS["extras"][e["n"]] * e["q"] * q_f for e in d_ex)
    d["Manipulación"] = ((min_manip/60)*18*q_f) + (q_f*dif_val) + ce
    
    cf = sum(d.values())
    desgloses[q_f] = d
    res.append({"Cantidad": q_f, "C. Fab": f"{cf:.2f}€", "PV Total": f"{cf*mult:.2f}€", "Unidad": f"{(cf*mult/q_f):.2f}€"})

st.header("📊 Escalado")
st.table(pd.DataFrame(res))
for q, de in desgloses.items():
    with st.expander(f"Detalle {q} uds"):
        st.table(pd.DataFrame(list(de.items()), columns=["Partida", "Coste (€)"]))
