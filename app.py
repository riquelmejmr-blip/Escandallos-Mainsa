import streamlit as st
import pandas as pd

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

# --- CONFIGURACIÓN PÁGINA ---
st.set_page_config(page_title="Escandallos MAINSA PLV", layout="wide")
st.title("📦 Escandallos MAINSA PLV")

# --- PANEL LATERAL ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_str = st.text_input("Cantidades (separadas por comas)", "200")
    
    # Procesar cantidades de forma segura
    lista_cantidades = []
    if cants_str:
        for x in cants_str.split(","):
            val = x.strip()
            if val.isdigit():
                lista_cantidades.append(int(val))
    
    st.divider()
    segundos_manip = st.number_input("Segundos Manipulación / Unidad", value=300)
    dif_coste = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], index=2, format_func=lambda x: f"{x}€ (Difícil)" if x==0.091 else f"{x}€")
    margen_com = st.number_input("Multiplicador Comercial", value=2.2)

# --- ENTRADA DE PIEZAS ---
if 'num_piezas' not in st.session_state:
    st.session_state.num_piezas = 1

col_b1, col_b2 = st.columns([1, 6])
if col_b1.button("➕ Añadir Pieza"):
    st.session_state.num_piezas += 1
if col_b2.button("🗑 Reiniciar"):
    st.session_state.num_piezas = 1
    st.rerun()

datos_usuario = []
for i in range(st.session_state.num_piezas):
    with st.expander(f"Configuración Forma #{i+1}", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            pliegos = st.number_input(f"Pliegos/Mueble #{i+1}", 1, key=f"p{i}")
            ancho = st.number_input(f"Ancho (mm) #{i+1}", 1, 5000, 700, key=f"w{i}")
            largo = st.number_input(f"Largo (mm) #{i+1}", 1, 5000, 1000, key=f"h{i}")
        with c2:
            pf = st.selectbox(f"C. Frontal #{i+1}", list(PRECIOS["cartoncillo"].keys()), index=1, key=f"pf{i}")
            gf = st.number_input(f"G. Frontal #{i+1}", PRECIOS["cartoncillo"][pf]["gramaje"], key=f"gf{i}") if pf != "Ninguno" else 0
            pl = st.selectbox(f"Plancha Base #{i+1}", list(PRECIOS["planchas"].keys()), key=f"pl{i}")
            ap = st.selectbox(f"Calidad Plancha #{i+1}", ["C/C", "B/C", "B/B"], index=1, key=f"ap{i}") if pl != "Ninguna" and "AC" not in pl else "C/C"
            pd = st.selectbox(f"C. Dorso #{i+1}", list(PRECIOS["cartoncillo"].keys()), index=0, key=f"pd{i}")
            gd = st.number_input(f"G. Dorso #{i+1}", PRECIOS["cartoncillo"][pd]["gramaje"], key=f"gd{i}") if pd != "Ninguno" else 0
        with c3:
            im_f = st.selectbox(f"Impresión F. #{i+1}", ["Offset", "Digital", "No"], key=f"imf{i}")
            nt_f = st.number_input(f"Tintas F. #{i+1}", 1, 6, 4, key=f"ntf{i}") if im_f == "Offset" else 0
            ba_f = st.checkbox(f"Barniz F. #{i+1}", key=f"baf{i}") if im_f == "Offset" else False
            
            im_d = "No"; nt_d = 0; ba_d = False
            if pd != "Ninguno":
                im_d = st.selectbox(f"Sistema Dorso #{i+1}", ["Offset", "Digital", "No"], index=2, key=f"imd{i}")
                if im_d == "Offset":
                    nt_d = st.number_input(f"Tintas D. #{i+1}", 1, 6, 1, key=f"ntd{i}")
                    ba_d = st.checkbox(f"Barniz D. #{i+1}", key=f"bad{i}")
            
            pel = st.selectbox(f"Peliculado #{i+1}", list(PRECIOS["peliculado"].keys()), index=1, key=f"pel{i}")
            ld = st.checkbox(f"Laminado Digital #{i+1}", key=f"ld{i}") if (im_f=="Digital" or im_d=="Digital") else False
            corte = st.selectbox(f"Corte #{i+1}", ["Troquelado", "Plotter"], key=f"cor{i}")
            
        datos_usuario.append({
            "pliegos": pliegos, "w": ancho, "h": largo, "pf": pf, "gf": gf, "pl": pl, "ap": ap, "pd": pd, "gd": gd,
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
    for j, nombre_ex in enumerate(sel_extras):
        uds_ex = cols_ex[j].number_input(f"Uds {nombre_ex}/ud", 1.0, key=f"ex_input_{j}")
        datos_extras.append({"n": nombre_ex, "q": uds_ex})

# --- MOTOR DE CÁLCULO ---
resultados_finales = []
desgloses_por_q = {}

if lista_cantidades:
    for q_neta in lista_cantidades:
        # MERMA DEL MANIPULADO: se calcula sobre el total de muebles
        m_normal_mueble, _ = obtener_mermas(q_neta)
        q_procesada_taller = q_neta + m_normal_mueble
        
        coste_acumulado_formas = 0.0
        lista_detalle_formas = []
        
        for idx, pz in enumerate(datos_usuario):
            # Unidades por pieza
            nb = q_neta * pz["pliegos"]
            m_norm_p, m_imp_p = obtener_mermas(nb)
            h_compra = nb + m_norm_p + m_imp_p
            h_proceso = nb + m_norm_p
            m2 = (pz["w"] * pz["h"]) / 1_000_000
            
            # 1. Coste Materiales
            c_mat = (h_compra * m2 * (pz["gf"]/1000) * PRECIOS["cartoncillo"][pz["pf"]]["precio_kg"]) + \
                    (h_compra * m2 * (pz["gd"]/1000) * PRECIOS["cartoncillo"][pz["pd"]]["precio_kg"])
            if pz["pl"] != "Ninguna":
                c_mat += (h_proceso * m2 * PRECIOS["planchas"][pz["pl"]][pz["ap"]])
                num_pasadas = (1 if pz["pf"] != "Ninguno" else 0) + (1 if pz["pd"] != "Ninguno" else 0)
                c_mat += (h_proceso * m2 * PRECIOS["planchas"][pz["pl"]]["peg"] * num_pasadas)
            
            # 2. Impresión (sobre netas)
            c_imp = 0.0
            def calc_offset(n): return 60 if n < 100 else (60 + 0.15*(n-100) if n < 500 else (120 if n <= 2000 else 120 + 0.015*(n-2000)))
            if pz["im_f"] == "Digital": c_imp += (nb * m2 * 6.5)
            elif pz["im_f"] == "Offset": c_imp += calc_offset(nb) * (pz["nt_f"] + (1 if pz["ba_f"] else 0))
            if pz["im_d"] == "Digital": c_imp += (nb * m2 * 6.5)
            elif pz["im_d"] == "Offset": c_imp += calc_offset(nb) * (pz["nt_d"] + (1 if pz["ba_d"] else 0))
            
            # 3. Acabado y Corte
            c_acab = (h_proceso * m2 * PRECIOS["peliculado"][pz["pel"]])
            if pz["ld"]: c_acab += (h_proceso * m2 * 0.40)
            
            if pz["corte"] == "Troquelado":
                f_fijo = 107.7 if (pz["h"] > 1000 or pz["w"] > 700) else (80.77 if (pz["h"] == 1000 and pz["w"] == 700) else 48.19)
                v_var = 0.135 if (pz["h"] > 1000 or pz["w"] > 700) else (0.09 if (pz["h"] == 1000 and pz["w"] == 700) else 0.06)
                c_corte = f_fijo + (h_proceso * v_var)
            else: c_corte = h_proceso * 1.5
            
            subtotal_pz = c_mat + c_imp + c_acab + c_corte
            coste_acumulado_formas += subtotal_pz
            lista_detalle_formas.append({"Pieza": idx+1, "Mat": c_mat, "Imp": c_imp, "Acab": c_acab, "Corte": c_corte, "Total": subtotal_pz})

        # 4. Manipulación sobre UNIDADES DE PROCESO
        c_mano_obra = ((segundos_manip / 3600) * 18 * q_procesada_taller) + (q_procesada_taller * dif_coste)
        c_extras = sum(PRECIOS["extras"][e["n"]] * e["q"] * q_procesada_taller for e in datos_extras)
        
        coste_fab_total = coste_acumulado_formas + c_mano_obra + c_extras
        pvp_total = coste_fab_total * margen_com
        
        desgloses_por_q[q_neta] = {"det": lista_detalle_formas, "manip_total": c_mano_obra + c_extras, "fab_total": coste_fab_total, "q_proc": q_procesada_taller}
        resultados_finales.append({
            "Cantidad Neta": q_neta, 
            "Uds. en Taller": q_procesada_taller, 
            "Coste Fab.": f"{coste_fab_total:.2f}€", 
            "PVP Proyecto": f"{pvp_total:.2f}€", 
            "PV Unidad": f"{(pvp_total/q_neta):.2f}€"
        })

# --- VISUALIZACIÓN ---
if resultados_finales:
    st.header("📊 Resumen de Resultados")
    df_res = pd.DataFrame(resultados_finales)
    st.dataframe(df_res, use_container_width=True)
    
    for q, info in desgloses_por_q.items():
        with st.expander(f"Ver detalle: {q} uds netas (Procesando {info['q_proc']} en taller)"):
            st.table(pd.DataFrame(info["det"]).style.format("{:.2f}€", subset=["Mat", "Imp", "Acab", "Corte", "Total"]))
            st.write(f"**Mano de Obra y Accesorios (sobre {info['q_proc']} uds):** {info['manip_total']:.2f} €")
            st.write(f"**COSTE TOTAL FABRICACIÓN:** {info['fab_total']:.2f} €")
            st.write(f"**PVP PROYECTO (x{margen_com}): {(info['fab_total']*margen_com):.2f} €**")
else:
    st.info("Introduce una cantidad en el panel lateral para iniciar el escandallo.")
