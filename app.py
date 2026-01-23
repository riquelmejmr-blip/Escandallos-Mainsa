import streamlit as st
import pandas as pd

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

st.set_page_config(page_title="Escandallos MAINSA PLV", layout="wide")
st.title("📦 Escandallos MAINSA PLV")

# --- PANEL LATERAL ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_raw = st.text_input("Cantidades (ej: 200, 500)", "200")
    lista_cants = []
    for x in cants_raw.split(","):
        try: lista_cants.append(int(float(x.strip())))
        except: pass
    
    st.divider()
    segundos_mueble = st.number_input("Segundos Manipulación / Unidad", value=300)
    dif_ud = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], index=2, format_func=lambda x: f"{x}€ (Difícil)" if x==0.091 else f"{x}€")
    margen_com = st.number_input("Multiplicador Comercial", value=2.2)

# --- CONFIGURACIÓN DE PIEZAS ---
if 'npz' not in st.session_state: st.session_state.npz = 1
c_btn1, c_btn2 = st.columns([1, 6])
if c_btn1.button("➕ Pieza"): st.session_state.npz += 1
if c_btn2.button("🗑 Reset"): st.session_state.npz = 1

datos_escandallo = []
for i in range(st.session_state.npz):
    with st.expander(f"Forma #{i+1}", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            pz_m = st.number_input(f"Pliegos/Mueble #{i+1}", 1, key=f"pm{i}")
            w_mm = st.number_input(f"Ancho (mm) #{i+1}", 1, 3000, 700, key=f"w{i}")
            h_mm = st.number_input(f"Largo (mm) #{i+1}", 1, 3000, 1000, key=f"h{i}")
        with c2:
            pf = st.selectbox(f"C. Frontal #{i+1}", list(PRECIOS["cartoncillo"].keys()), 1, key=f"pf{i}")
            gf = st.number_input(f"Gramaje F. #{i+1}", PRECIOS["cartoncillo"][pf]["gramaje"], key=f"gf{i}") if pf != "Ninguno" else 0
            pl = st.selectbox(f"Plancha #{i+1}", list(PRECIOS["planchas"].keys()), key=f"pl{i}")
            ap = st.selectbox(f"Calidad #{i+1}", ["C/C", "B/C", "B/B"], 1, key=f"ap{i}") if pl != "Ninguna" and "AC" not in pl else "C/C"
            pd = st.selectbox(f"C. Dorso #{i+1}", list(PRECIOS["cartoncillo"].keys()), 0, key=f"pd{i}")
            gd = st.number_input(f"Gramaje D. #{i+1}", PRECIOS["cartoncillo"][pd]["gramaje"], key=f"gd{i}") if pd != "Ninguno" else 0
        with c3:
            im_f = st.selectbox(f"Impresión F. #{i+1}", ["Offset", "Digital", "No"], key=f"im{i}")
            nt_f = st.number_input(f"Tintas F. #{i+1}", 1, 6, 4, key=f"nt{i}") if im_f == "Offset" else 0
            ba_f = st.checkbox(f"Barniz F. #{i+1}", key=f"ba{i}") if im_f == "Offset" else False
            im_d = "No"; nt_d = 0; ba_d = False
            if pd != "Ninguno":
                im_d = st.selectbox(f"Sistema D. #{i+1}", ["Offset", "Digital", "No"], 2, key=f"imd{i}")
                if im_d == "Offset":
                    nt_d = st.number_input(f"Tintas D. #{i+1}", 1, 6, 1, key=f"ntd{i}")
                    ba_d = st.checkbox(f"Barniz D. #{i+1}", key=f"bad{i}")
            pe = st.selectbox(f"Peliculado #{i+1}", list(PRECIOS["peliculado"].keys()), 1, key=f"pe{i}")
            ld = st.checkbox(f"Laminado Digital #{i+1}", key=f"ld{i}") if (im_f=="Digital" or im_d=="Digital") else False
            co = st.selectbox(f"Corte #{i+1}", ["Troquelado", "Plotter"], 0, key=f"co{i}")
        datos_escandallo.append({"p":pz_m,"w":w_mm,"h":h_mm,"pf":pf,"gf":gf,"pl":pl,"ap":ap,"pd":pd,"gd":gd,"im_f":im_f,"nt_f":nt_f,"ba_f":ba_f,"im_d":im_d,"nt_d":nt_d,"ba_d":ba_d,"pe":pe,"ld":ld,"co":co})

# --- ACCESORIOS ---
st.divider()
acc_sel = st.multiselect("Accesorios / Extras", list(PRECIOS["extras"].keys()))
l_ext = []
if acc_sel:
    cx = st.columns(len(acc_sel))
    for j, n in enumerate(acc_sel):
        q = cx[j].number_input(f"Uds {n}/ud", 1.0, key=f"acc{j}")
        l_ext.append({"n": n, "q": q})

# --- MOTOR DE CÁLCULO ---
res_t = []; desc_t = {}
for q_obj in lista_cants:
    # APLICAMOS MERMA AL MANIPULADO
    mn_mueble, _ = obtener_mermas(q_obj)
    q_proceso_mueble = q_obj + mn_mueble
    
    coste_formas = 0.0; det_f = []
    for idx, pz in enumerate(datos_escandallo):
        nb = q_obj * pz["p"]
        mn_p, mi_p = obtener_mermas(nb)
        hp = nb + mn_p + mi_p
        hpro = nb + mn_p
        m2 = (pz["w"] * pz["h"]) / 1_000_000
        
        c_mat = (hp * m2 * (pz["gf"]/1000) * PRECIOS["cartoncillo"][pz["pf"]]["precio_kg"]) + (hp * m2 * (pz["gd"]/1000) * PRECIOS["cartoncillo"][pz["pd"]]["precio_kg"])
        if pz["pl"] != "Ninguna":
            c_mat += (hpro * m2 * PRECIOS["planchas"][pz["pl"]][pz["ap"]])
            num_p = (1 if pz["pf"] != "Ninguno" else 0) + (1 if pz["pd"] != "Ninguno" else 0)
            c_mat += (hpro * m2 * PRECIOS["planchas"][pz["pl"]]["peg"] * num_p)
            
        c_imp = 0.0
        if pz["im_f"] == "Digital": c_imp += (nb * m2 * 6.5)
        elif pz["im_f"] == "Offset":
            base_f = 60 if nb < 100 else (60 + 0.15*(nb-100) if nb < 500 else (120 if nb <= 2000 else 120 + 0.015*(nb-2000)))
            c_imp += base_f * (pz["nt_f"] + (1 if pz["ba_f"] else 0))
        if pz["im_d"] == "Digital": c_imp += (nb * m2 * 6.5)
        elif pz["im_d"] == "Offset":
            base_d = 60 if nb < 100 else (60 + 0.15*(nb-100) if nb < 500 else (120 if nb <= 2000 else 120 + 0.015*(nb-2000)))
            c_imp += base_d * (pz["nt_d"] + (1 if pz["ba_d"] else 0))
            
        c_ac = hpro * m2 * PRECIOS["peliculado"][pz["pe"]]
        if pz["ld"]: c_ac += (hpro * m2 * 0.40)
        
        if pz["co"] == "Troquelado":
            ff = 107.7 if (pz["h"] > 1000 or pz["w"] > 700) else (80.77 if (pz["h"] == 1000 and pz["w"] == 700) else 48.19)
            vv = 0.135 if (pz["h"] > 1000 or pz["w"] > 700) else (0.09 if (pz["h"] == 1000 and pz["w"] == 700) else 0.06)
            c_co = ff + (hpro * vv)
        else: c_co = hpro * 1.5
        
        s_pz = c_mat + c_imp + c_ac + c_co
        coste_formas += s_pz
        det_f.append({"Pieza": idx+1, "Mat": c_mat, "Imp": c_imp, "Acab": c_ac, "Corte": c_co, "Total": s_pz})

    # Manipulación sobre UNIDADES DE PROCESO
    c_man = ((segundos_mueble / 3600) * 18 * q_proceso_mueble) + (q_proceso_mueble * dif_ud)
    c_ex = sum(PRECIOS["extras"][e["n"]] * e["q"] * q_proceso_mueble for e in l_ext)
    
    c_fab = coste_formas + c_man + c_ex
    pvp = c_fab * margen_com
    desc_t[q_obj] = {"det": det_f, "man": c_man + c_ex, "total": c_fab, "q_proc": q_proceso_mueble}
    res_t.append({"Cantidad": q_obj, "Uds. Proceso": q_proceso_mueble, "C. Fab": f"{c_fab:.2f}€", "PVP Proyecto": f"{pvp:.2f}€", "PVP Unidad": f"{(pvp/q_obj):.2f}€"})

# --- SALIDA DE DATOS ---
if len(res_t) > 0:
    st.header("📊 Resumen del Escandallo")
    df_res = pd.DataFrame(res_t)
    st.dataframe(df_res, use_container_width=True)
    
    for q, info in desc_t.items():
        with st.expander(f"Ver detalle: {q} uds (Procesando {info['q_proc']} por mermas)"):
            st.table(pd.DataFrame(info["det"]).style.format("{:.2f}€", subset=["Mat", "Imp", "Acab", "Corte", "Total"]))
            st.write(f"**Mano de Obra y Accesorios (sobre {info['q_proc']} uds):** {info['man']:.2f} €")
            st.write(f"**COSTE TOTAL FABRICACIÓN:** {info['total']:.2f} €")
            st.write(f"**PVP FINAL (x{margen_com}): {(info['total']*margen_com):.2f} €**")
else:
    st.info("Introduce una cantidad en el menú lateral para calcular.")
