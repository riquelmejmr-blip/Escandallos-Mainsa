import streamlit as st
import pandas as pd # Mantenemos pd solo para Pandas

# --- BASE DE DATOS DE PRECIOS ---
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
        "CINTA D/CARA normal": 0.26, "CINTA LOHMAN 20mm": 0.33, "CINTA LOHMAN 20mm": 0.49,
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
    cants_str = st.text_input("Cantidades (separadas por comas)", "200")
    lista_cantidades = []
    if cants_str:
        for x in cants_str.split(","):
            val = x.strip()
            if val.replace('.','',1).isdigit():
                lista_cantidades.append(int(float(val)))
    
    st.divider()
    segundos_manip = st.number_input("Segundos Manipulación / Unidad", value=300)
    dif_coste = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], index=2, format_func=lambda x: f"{x}€ (Difícil)" if x==0.091 else f"{x}€")
    margen_com = st.number_input("Multiplicador Comercial", value=2.2)

# --- ENTRADA DE PIEZAS ---
if 'num_piezas' not in st.session_state: st.session_state.num_piezas = 1

c_b1, c_b2 = st.columns([1, 6])
if c_b1.button("➕ Añadir Pieza"): st.session_state.num_piezas += 1
if c_b2.button("🗑 Reiniciar"):
    st.session_state.num_piezas = 1
    st.rerun()

datos_usuario = []
for i in range(st.session_state.num_piezas):
    with st.expander(f"Configuración Forma #{i+1}", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            pliegos = st.number_input(f"Pliegos/Mueble #{i+1}", 1, key=f"pliegos_{i}")
            ancho = st.number_input(f"Ancho (mm) #{i+1}", 1.0, 5000.0, 700.0, key=f"ancho_{i}")
            largo = st.number_input(f"Largo (mm) #{i+1}", 1.0, 5000.0, 1000.0, key=f"largo_{i}")
        with c2:
            p_frontal = st.selectbox(f"C. Frontal #{i+1}", list(PRECIOS["cartoncillo"].keys()), index=1, key=f"pf_{i}")
            g_frontal = st.number_input(f"G. Frontal #{i+1}", PRECIOS["cartoncillo"][p_frontal]["gramaje"], key=f"gf_{i}") if p_frontal != "Ninguno" else 0
            plancha = st.selectbox(f"Plancha Base #{i+1}", list(PRECIOS["planchas"].keys()), key=f"pl_{i}")
            calidad = st.selectbox(f"Calidad Plancha #{i+1}", ["C/C", "B/C", "B/B"], index=1, key=f"ap_{i}") if plancha != "Ninguna" and "AC" not in plancha else "C/C"
            p_dorso = st.selectbox(f"C. Dorso #{i+1}", list(PRECIOS["cartoncillo"].keys()), index=0, key=f"pdorso_{i}")
            g_dorso = st.number_input(f"G. Dorso #{i+1}", PRECIOS["cartoncillo"][p_dorso]["gramaje"], key=f"gd_{i}") if p_dorso != "Ninguno" else 0
        with c3:
            im_f = st.selectbox(f"Sistema Frontal #{i+1}", ["Offset", "Digital", "No"], key=st.session_state.num_piezas + i + 100)
            nt_f = st.number_input(f"Tintas F. #{i+1}", 1, 6, 4, key=f"ntf_{i}") if im_f == "Offset" else 0
            ba_f = st.checkbox(f"Barniz F. #{i+1}", key=f"baf_{i}") if im_f == "Offset" else False
            
            im_d = "No"; nt_d = 0; ba_d = False
            if p_dorso != "Ninguno":
                im_d = st.selectbox(f"Sistema Dorso #{i+1}", ["Offset", "Digital", "No"], index=2, key=f"imd_{i}")
                if im_d == "Offset":
                    nt_d = st.number_input(f"Tintas D. #{i+1}", 1, 6, 1, key=f"ntd_{i}")
                    ba_d = st.checkbox(f"Barniz D. #{i+1}", key=f"bad_{i}")
            
            pel = st.selectbox(f"Peliculado #{i+1}", list(PRECIOS["peliculado"].keys()), index=1, key=f"pel_{i}")
            ld = st.checkbox(f"Laminado Digital #{i+1}", key=f"ld_{i}") if (im_f=="Digital" or im_d=="Digital") else False
            corte = st.selectbox(f"Corte #{i+1}", ["Troquelado", "Plotter"], key=f"cor_{i}")
            
        datos_usuario.append({
            "pliegos": pliegos, "w": ancho, "h": largo, "pf": p_frontal, "gf": g_frontal, 
            "pl": plancha, "ap": calidad, "pd": p_dorso, "gd": g_dorso,
            "im_f": im_f, "nt_f": nt_f, "ba_f": ba_f, "im_d": im_d, "nt_d": nt_d, "ba_d": ba_d,
            "pel": pel, "ld": ld, "corte": corte
        })

# --- ACCESORIOS ---
st.divider()
st.subheader("📦 Accesorios de Manipulación")
sel_extras = st.multiselect("Seleccionar elementos extra", list(PRECIOS["extras"].keys()))
datos_extras = []
if sel_extras:
    cols_ex = st.columns(len(sel_extras))
    for j, n_ex in enumerate(sel_extras):
        u_ex = cols_ex[j].number_input(f"Uds {n_ex}/ud", 1.0, key=f"extra_val_{j}")
        datos_extras.append({"n": n_ex, "q": u_ex})

# --- MOTOR DE CÁLCULO ---
resultados_finales = []
desgloses_por_q = {}

if lista_cantidades:
    for q_neta in lista_cantidades:
        # MERMA DEL MANIPULADO: se calcula sobre el total de muebles
        m_norm_mueble, _ = obtener_mermas(q_neta)
        q_procesada = q_neta + m_norm_mueble
        
        coste_acum_formas = 0.0
        lista_det_formas = []
        
        for idx, pz in enumerate(datos_usuario):
            nb = q_neta * pz["pliegos"]
            mn_p, mi_p = obtener_mermas(nb)
            h_compra = nb + mn_p + mi_p
            h_proceso = nb + mn_p
            m2 = (pz["w"] * pz["h"]) / 1_000_000
            
            # 1. Materiales
            c_mat = (h_compra * m2 * (pz["gf"]/1000) * PRECIOS["cartoncillo"][pz["pf"]]["precio_kg"]) + \
                    (h_compra * m2 * (pz["gd"]/1000) * PRECIOS["cartoncillo"][pz["pd"]]["precio_kg"])
            if pz["pl"] != "Ninguna":
                c_mat += (h_proceso * m2 * PRECIOS["planchas"][pz["pl"]][pz["ap"]])
                pas = (1 if pz["pf"] != "Ninguno" else 0) + (1 if pz["pd"] != "Ninguno" else 0)
                c_mat += (h_proceso * m2 * PRECIOS["planchas"][pz["pl"]]["peg"] * pas)
            
            # 2. Impresión
            c_imp = 0.0
            def f_off(n): return 60 if n < 100 else (60 + 0.15*(n-100) if n < 500 else (120 if n <= 2000 else 120 + 0.015*(n-2000)))
            if pz["im_f"] == "Digital": c_imp += (nb * m2 * 6.5)
            elif pz["im_f"] == "Offset": c_imp += f_off(nb) * (pz["nt_f"] + (1 if pz["ba_f"] else 0))
            if pz["im_d"] == "Digital": c_imp += (nb * m2 * 6.5)
            elif pz["im_d"] == "Offset": c_imp += f_off(nb) * (pz["nt_d"] + (1 if pz["ba_d"] else 0))
            
            # 3. Acabado y Corte
            c_acab = (h_proceso * m2 * PRECIOS["peliculado"][pz["pel"]])
            if pz["ld"]: c_acab += (h_proceso * m2 * 0.40)
            if pz["corte"] == "Troquelado":
                f_f = 107.7 if (pz["h"] > 1000 or pz["w"] > 700) else (80.77 if (pz["h"] == 1000 and pz["w"] == 700) else 48.19)
                v_v = 0.135 if (pz["h"] > 1000 or pz["w"] > 700) else (0.09 if (pz["h"] == 1000 and pz["w"] == 700) else 0.06)
                c_cor = f_f + (h_proceso * v_v)
            else: c_cor = h_proceso * 1.5
            
            sub_pz = c_mat + c_imp + c_acab + c_cor
            coste_acum_formas += sub_pz
            lista_det_formas.append({"Pieza": idx+1, "Mat": c_mat, "Imp": c_imp, "Acab": c_acab, "Corte": c_cor, "Total": sub_pz})

        # 4. Manipulación sobre UNIDADES DE PROCESO (Netas + Merma Normal)
        c_mano = ((segundos_manip / 3600) * 18 * q_procesada) + (q_procesada * dif_coste)
        c_ext = sum(PRECIOS["extras"][ex["n"]] * ex["q"] * q_procesada for ex in datos_extras)
        
        c_fab_total = coste_acum_formas + c_mano + c_ext
        pv_total = c_fab_total * margen_com
        
        desgloses_por_q[q_neta] = {"det": lista_det_formas, "man_total": c_mano + c_ext, "fab": c_fab_total, "qp": q_procesada}
        resultados_finales.append({
            "Cantidad Neta": q_neta, "Uds. Taller": q_procesada, "C. Fab.": f"{c_fab_total:.2f}€", 
            "PVP Proyecto": f"{pv_total:.2f}€", "PV Unidad": f"{(pv_total/q_neta):.2f}€"
        })

# --- SALIDA ---
if len(resultados_finales) > 0:
    st.header("📊 Resumen del Escandallo")
    df_res = pd.DataFrame(resultados_finales) # Ahora pd siempre es la librería
    st.dataframe(df_res, use_container_width=True)
    for q, info in desgloses_por_q.items():
        with st.expander(f"Detalle: {q} uds netas (Proceso: {info['qp']} uds)"):
            st.table(pd.DataFrame(info["det"]).style.format("{:.2f}€", subset=["Mat", "Imp", "Acab", "Corte", "Total"]))
            st.write(f"**Manipulación y Accesorios (sobre {info['qp']} uds):** {info['man_total']:.2f} €")
            st.write(f"**COSTE TOTAL FABRICACIÓN:** {info['fab']:.2f} €")
            st.write(f"**PVP PROYECTO (x{margen_com}): {(info['fab']*margen_com):.2f} €**")
else:
    st.info("Introduce cantidades en el lateral para calcular.")
