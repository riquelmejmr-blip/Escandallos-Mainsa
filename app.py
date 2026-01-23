import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

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
    "laminado_digital": 3.5, # Precio por m2
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
        return n * 0.10, 0 # Merma fija 10% total
    if n < 100: return 15, 135
    if n < 200: return 30, 150
    if n < 600: return 40, 160
    if n < 1000: return 50, 170
    if n < 2000: return 60, 170
    return 120, 170

# --- CONFIGURACIÓN PÁGINA ---
st.set_page_config(page_title="MAINSA PLV - PRO", layout="wide")
st.title("📦 Escandallos MAINSA PLV")

# --- SESSION STATE PARA PIEZAS ---
if 'piezas_list' not in st.session_state:
    st.session_state.piezas_list = [{"id": 0}]

# --- PANEL LATERAL ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_str = st.text_input("Cantidades (ej: 200, 500)", "200")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    st.divider()
    segundos_manip = st.number_input("Segundos Manipulación / Unidad", value=300)
    dif_coste = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], index=2, format_func=lambda x: f"{x}€")
    margen_com = st.number_input("Multiplicador Comercial", value=2.2)

# --- ENTRADA DE PIEZAS ---
col_b1, col_b2 = st.columns([1, 6])
if col_b1.button("➕ Añadir Pieza"):
    new_id = st.session_state.piezas_list[-1]["id"] + 1 if st.session_state.piezas_list else 0
    st.session_state.piezas_list.append({"id": new_id})

if col_b2.button("🗑 Reiniciar Todo"):
    st.session_state.piezas_list = [{"id": 0}]
    st.rerun()

datos_usuario = []
for idx, pieza_ref in enumerate(st.session_state.piezas_list):
    p_id = pieza_ref["id"]
    with st.expander(f"Forma #{idx+1}", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            nom_p = st.text_input(f"Nombre Pieza", f"Parte {idx+1}", key=f"nom{p_id}")
            pliegos = st.number_input(f"Pliegos/Mueble", 0.0, 100.0, 1.0, 0.1, key=f"p{p_id}")
            ancho = st.number_input(f"Ancho (mm)", 1, 5000, 700, key=f"w{p_id}")
            largo = st.number_input(f"Largo (mm)", 1, 5000, 1000, key=f"h{p_id}")
        with c2:
            pf_s = st.selectbox(f"C. Frontal", list(PRECIOS["cartoncillo"].keys()), 1, key=f"pf{p_id}")
            gf_s = st.number_input(f"G. Frontal", PRECIOS["cartoncillo"][pf_s]["gramaje"], key=f"gf{p_id}") if pf_s != "Ninguno" else 0
            pl_s = st.selectbox(f"Plancha Base", list(PRECIOS["planchas"].keys()), key=f"pl{p_id}")
            ap_s = st.selectbox(f"Calidad Plancha", ["C/C", "B/C", "B/B"], 1, key=f"ap{p_id}") if pl_s != "Ninguna" and "AC" not in pl_s else "C/C"
            pd_s = st.selectbox(f"C. Dorso", list(PRECIOS["cartoncillo"].keys()), index=0, key=f"pd{p_id}")
            gd_s = st.number_input(f"G. Dorso", PRECIOS["cartoncillo"][pd_s]["gramaje"], key=f"gd{p_id}") if pd_s != "Ninguno" else 0
        with c3:
            im_f = st.selectbox(f"Sistema Frontal", ["Offset", "Digital", "No"], key=f"imf{p_id}")
            # Lógica Digital: Sin pelicular por defecto y Laminado Digital
            def_pel = 0 if im_f == "Digital" else 1
            
            nt_f = st.number_input(f"Tintas F.", 1, 6, 4, key=f"ntf{p_id}") if im_f == "Offset" else 0
            ba_f = st.checkbox(f"Barniz F.", key=f"baf{p_id}") if im_f == "Offset" else False
            
            lam_dig = False
            if im_f == "Digital":
                lam_dig = st.checkbox(f"Laminado Digital (3.5€/m2)", key=f"ld{p_id}")
            
            pel_s = st.selectbox(f"Peliculado", list(PRECIOS["peliculado"].keys()), index=def_pel, key=f"pel{p_id}")
            corte_s = st.selectbox(f"Corte", ["Troquelado", "Plotter"], key=f"cor{p_id}")
            
            if st.button("🗑 Eliminar esta pieza", key=f"del{p_id}"):
                st.session_state.piezas_list.pop(idx)
                st.rerun()
            
        datos_usuario.append({
            "nombre": nom_p, "pliegos": pliegos, "w": ancho, "h": largo, "pf": pf_s, "gf": gf_s, 
            "pl": pl_s, "ap": ap_s, "pd": pd_s, "gd": gd_s, "im_f": im_f, "nt_f": nt_f, 
            "ba_f": ba_f, "pel": pel_s, "ld": lam_dig, "corte": corte_s
        })

# --- ACCESORIOS ---
st.divider()
st.subheader("📦 Accesorios de Manipulación")
sel_extras = st.multiselect("Seleccionar elementos extra", list(PRECIOS["extras"].keys()))
datos_extras = []
if sel_extras:
    cols_ex = st.columns(len(sel_extras))
    for j, n_ex in enumerate(sel_extras):
        u_ex = cols_ex[j].number_input(f"Uds {n_ex}/ud", 1.0, key=f"ex_v_{j}")
        datos_extras.append({"n": n_ex, "q": u_ex})

# --- MOTOR DE CÁLCULO ---
resultados_finales = []
desgloses_por_q = {}

if lista_cants:
    for q_neta in lista_cants:
        coste_acum_fab = 0.0
        lista_det_partidas = []
        
        # Mermas de manipulación (dependen de si hay digital en el proyecto)
        tiene_digital = any(p["im_f"] == "Digital" for p in datos_usuario)
        mn_manip, _ = calcular_mermas(q_neta, es_digital=tiene_digital)
        q_proc_taller = q_neta + mn_manip
        
        for pz in datos_usuario:
            nb = q_neta * pz["pliegos"]
            es_dig_p = pz["im_f"] == "Digital"
            mn_p, mi_p = calcular_mermas(nb, es_digital=es_dig_p)
            h_compra = nb + mn_p + mi_p
            h_proceso = nb + mn_p
            m2 = (pz["w"] * pz["h"]) / 1_000_000
            
            # 1. Materia Prima: Cartoncillo
            c_cart = (h_compra * m2 * (pz["gf"]/1000) * PRECIOS["cartoncillo"][pz["pf"]]["precio_kg"]) + \
                     (h_compra * m2 * (pz["gd"]/1000) * PRECIOS["cartoncillo"][pz["pd"]]["precio_kg"])
            
            # 2. Materia Prima: Plancha
            c_plancha = 0.0
            c_contra = 0.0
            if pz["pl"] != "Ninguna":
                c_plancha = (h_proceso * m2 * PRECIOS["planchas"][pz["pl"]][pz["ap"]])
                pas = (1 if pz["pf"] != "Ninguno" else 0) + (1 if pz["pd"] != "Ninguno" else 0)
                c_contra = (h_proceso * m2 * PRECIOS["planchas"][pz["pl"]]["peg"] * pas)
            
            # 3. Impresión
            c_imp = 0.0
            def f_off(n): return 60 if n < 100 else (60 + 0.15*(n-100) if n < 500 else (120 if n <= 2000 else 120 + 0.015*(n-2000)))
            if pz["im_f"] == "Digital": c_imp = (nb * m2 * 6.5)
            elif pz["im_f"] == "Offset": c_imp = f_off(nb) * (pz["nt_f"] + (1 if pz["ba_f"] else 0))
            
            # 4. Acabado (Peliculado / Laminado)
            c_acab = (h_proceso * m2 * PRECIOS["peliculado"][pz["pel"]])
            if pz["ld"]: c_acab += (h_proceso * m2 * PRECIOS["laminado_digital"])
            
            # 5. Troquelado (Arreglo + Tiraje)
            c_trq_arr = 0.0
            c_trq_tir = 0.0
            if pz["corte"] == "Troquelado":
                c_trq_arr = 107.7 if (pz["h"] > 1000 or pz["w"] > 700) else (80.77 if (pz["h"] == 1000 and pz["w"] == 700) else 48.19)
                v_v = 0.135 if (pz["h"] > 1000 or pz["w"] > 700) else (0.09 if (pz["h"] == 1000 and pz["w"] == 700) else 0.06)
                c_trq_tir = h_proceso * v_v
            else:
                c_trq_tir = h_proceso * 1.5 # Plotter como tiraje variable
                
            lista_det_partidas.append({
                "Pieza": pz["nombre"], "Cartoncillo": c_cart, "Plancha": c_plancha, "Contra.": c_contra,
                "Imp.": c_imp, "Acabado": c_acab, "Trq. Arr.": c_trq_arr, "Trq. Tir.": c_trq_tir
            })

        # 6. Manipulación y Extras
        c_mano = ((segundos_manip / 3600) * 18 * q_proc_taller) + (q_proc_taller * dif_coste)
        c_ext = sum(PRECIOS["extras"][e["n"]] * e["q"] * q_proc_taller for e in datos_extras)
        
        # Totales
        coste_total_pz = sum(sum(v for k,v in p.items() if k != "Pieza") for p in lista_det_partidas)
        coste_fab_total = coste_total_pz + c_mano + c_ext
        pv_total = coste_fab_total * margen_com
        
        desgloses_por_q[q_neta] = {"det": lista_det_partidas, "man": c_mano + c_ext, "fab": coste_fab_total, "qp": q_proc_taller}
        resultados_finales.append({
            "Cantidad": q_neta, "Taller": q_proc_taller, "C. Fab": f"{coste_fab_total:.2f}€", 
            "Venta Total": f"{pv_total:.2f}€", "PVP Ud": f"{(pv_total/q_neta):.2f}€"
        })

# --- SALIDA ---
if resultados_finales:
    st.header("📊 Resumen de Resultados")
    st.dataframe(pd.DataFrame(resultados_finales), use_container_width=True)
    
    for q, info in desgloses_por_q.items():
        with st.expander(f"🔍 Desglose Detallado: {q} uds", expanded=False):
            df_pz = pd.DataFrame(info["det"])
            st.table(df_pz.style.format("{:.2f}€", subset=df_pz.columns[1:]))
            st.write(f"**Manipulación y Extras:** {info['man']:.2f} €")
            st.write(f"**COSTE TOTAL FABRICACIÓN:** {info['fab']:.2f} €")

    # --- GENERACIÓN DE PDF ---
    st.divider()
    st.subheader("📄 Generar Oferta Comercial (PDF)")
    
    if st.button("Descargar PDF para Comercial"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "PRESUPUESTO COMERCIAL - MAINSA PLV", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "1. Resumen de Formatos / Piezas", ln=True)
        pdf.set_font("Arial", "", 10)
        for pz in datos_usuario:
            pdf.cell(190, 7, f"- {pz['nombre']}: {pz['w']}x{pz['h']}mm | {pz['pliegos']} pliegos/ud | Imp: {pz['im_f']}", ln=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "2. Manipulacion y Acabado", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 7, f"Tiempo estimado: {segundos_manip} segundos/unidad", ln=True)
        if sel_extras:
            pdf.cell(190, 7, f"Accesorios incluidos: {', '.join(sel_extras)}", ln=True)

        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "3. Escala de Precios", ln=True)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(60, 10, "Cantidad", border=1)
        pdf.cell(60, 10, "PVP Total", border=1)
        pdf.cell(60, 10, "PVP Unitario", border=1, ln=True)
        
        pdf.set_font("Arial", "", 11)
        for r in resultados_finales:
            pdf.cell(60, 10, str(r['Cantidad']), border=1)
            pdf.cell(60, 10, r['Venta Total'], border=1)
            pdf.cell(60, 10, r['PVP Ud'], border=1, ln=True)
            
        pdf_output = pdf.output(dest='S')
        st.download_button("Click aquí para descargar PDF", data=bytes(pdf_output), file_name="Oferta_Mainsa_PLV.pdf", mime="application/pdf")

else:
    st.info("Introduce datos para generar el escandallo.")
