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

st.set_page_config(page_title="Escandallos MAINSA PLV", layout="wide")
st.title("📦 Escandallos MAINSA PLV")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    cants_raw = st.text_input("Cantidades (ej: 200, 500, 1000)", "200")
    lista_cants = []
    for x in cants_raw.split(","):
        try: lista_cants.append(int(float(x.strip())))
        except: pass
    
    st.divider()
    segundos_mueble = st.number_input("Segundos Manipulación / Unidad", value=300)
    dif_ud = st.selectbox("Dificultad Unitaria", [0.02, 0.061, 0.091], index=2, format_func=lambda x: f"{x}€ (Difícil)" if x==0.091 else f"{x}€")
    margen_com = st.number_input("Multiplicador Comercial", value=2.2)

# --- GESTIÓN DE PIEZAS ---
if 'npz' not in st.session_state: st.session_state.npz = 1

col_btn1, col_btn2 = st.columns([1, 6])
if col_btn1.button("➕ Añadir Pieza"): st.session_state.npz += 1
if col_btn2.button("🗑 Reset"): st.session_state.npz = 1

datos_escandallo = []
for i in range(st.session_state.npz):
    with st.expander(f"Forma #{i+1}", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            pz_m = st.number_input(f"Pliegos/Mueble #{i+1}", 1, key=f"pm{i}")
            w_mm = st.number_input(f"Ancho (mm) #{i+1}", min_value=1, value=700, key=f"w{i}")
            h_mm = st.number_input(f"Largo (mm) #{i+1}", min_value=1, value=1000, key=f"h{i}")
        
        with c2:
            # Frontal
            pf = st.selectbox(f"C. Frontal #{i+1}", list(PRECIOS["cartoncillo"].keys()), index=1, key=f"pf{i}")
            gf = 0
            if pf != "Ninguno":
                gf = st.number_input(f"Gramaje Frontal #{i+1}", PRECIOS["cartoncillo"][pf]["gramaje"], key=f"gf{i}")
            
            # Plancha
            pl = st.selectbox(f"Plancha #{i+1}", list(PRECIOS["planchas"].keys()), key=f"pl{i}")
            ap = st.selectbox(f"Calidad Plancha #{i+1}", ["C/C", "B/C", "B/B"], index=1, key=f"ap{i}") if pl != "Ninguna" and "AC" not in pl else "C/C"
            
            # Dorso
            pd_sel = st.selectbox(f"C. Dorso #{i+1}", list(PRECIOS["cartoncillo"].keys()), index=0, key=f"pd{i}")
            gd = 0
            if pd_sel != "Ninguno":
                gd = st.number_input(f"Gramaje Dorso #{i+1}", PRECIOS["cartoncillo"][pd_sel]["gramaje"], key=f"gd{i}")
        
        with c3:
            # Impresión Frontal
            st.markdown("**Impresión Frontal**")
            im_sel = st.selectbox(f"Sistema Frontal #{i+1}", ["Offset", "Digital", "No"], index=0, key=f"im{i}")
            nt_val = st.number_input(f"Tintas F. #{i+1}", 1, 6, 4, key=f"nt{i}") if im_sel == "Offset" else 0
            ba_val = st.checkbox(f"Barniz F. #{i+1}", key=f"ba{i}") if im_sel == "Offset" else False
            
            # Impresión Dorso (Solo si hay cartoncillo en dorso)
            nt_dorso = 0
            ba_dorso = False
            im_dorso_sel = "No"
            if pd_sel != "Ninguno":
                st.markdown("**Impresión Dorso**")
                im_dorso_sel = st.selectbox(f"Sistema Dorso #{i+1}", ["Offset", "Digital", "No"], index=2, key=f"imd{i}")
                if im_dorso_sel == "Offset":
                    nt_dorso = st.number_input(f"Tintas D. #{i+1}", 1, 6, 1, key=f"ntd{i}")
                    ba_dorso = st.checkbox(f"Barniz D. #{i+1}", key=f"bad{i}")

            st.divider()
            pe_sel = st.selectbox(f"Peliculado #{i+1}", list(PRECIOS["peliculado"].keys()), index=1, key=f"pe{i}")
            # Opción especial si es digital
            lam_dig = False
            if im_sel == "Digital" or im_dorso_sel == "Digital":
                lam_dig = st.checkbox(f"Laminado Digital Específico #{i+1}", key=f"ld{i}")
            
            co_sel = st.selectbox(f"Corte #{i+1}", ["Troquelado", "Plotter"], index=0, key=f"co{i}")
        
        datos_escandallo.append({
            "p":pz_m, "w":w_mm, "h":h_mm, "pf":pf, "gf":gf, "pl":pl, "ap":ap, "pd":pd_sel, "gd":gd, 
            "im_f":im_sel, "nt_f":nt_val, "ba_f":ba_val, 
            "im_d":im_dorso_sel, "nt_d":nt_dorso, "ba_d":ba_dorso,
            "pe":pe_sel, "ld":lam_dig, "co":co_sel
        })

# --- ACCESORIOS ---
st.divider()
acc_seleccionados = st.multiselect("Accesorios / Extras", list(PRECIOS["extras"].keys()))
lista_extras = []
if acc_seleccionados:
    cols_acc = st.columns(len(acc_seleccionados))
    for j, name in enumerate(acc_seleccionados):
        q_acc = cols_acc[j].number_input(f"Uds {name}/mueble", 1.0, key=f"acc{j}")
        lista_extras.append({"n": name, "q": q_acc})

# --- MOTOR DE CÁLCULO ---
res_tabla = []
desgloses_tecnicos = {}

for cant_objetivo in lista_cants:
    coste_total_formas = 0.0
    detalles_formas = []
    for idx, pieza in enumerate(datos_escandallo):
        netas_pieza = cant_objetivo * pieza["p"]
        mn, mi = obtener_mermas(netas_pieza)
        h_compra = netas_pieza + mn + mi
        h_proceso = netas_pieza + mn
        m2_pieza = (pieza["w"] * pieza["h"]) / 1_000_000
        
        # Mats
        coste_mats = (h_compra * m2_pieza * (pieza["gf"]/1000) * PRECIOS["cartoncillo"][pieza["pf"]]["precio_kg"]) + \
                     (h_compra * m2_pieza * (pieza["gd"]/1000) * PRECIOS["cartoncillo"][pieza["pd"]]["precio_kg"])
        if pieza["pl"] != "Ninguna":
            coste_mats += (h_proceso * m2_pieza * PRECIOS["planchas"][pieza["pl"]][pieza["ap"]])
            num_p = (1 if pieza["pf"] != "Ninguno" else 0) + (1 if pieza["pd"] != "Ninguno" else 0)
            coste_mats += (h_proceso * m2_pieza * PRECIOS["planchas"][pieza["pl"]]["peg"] * num_p)
            
        # Impresión (FRONTAL + DORSO) sobre HOJAS NETAS
        coste_imp = 0.0
        # Frontal
        if pieza["im_f"] == "Digital": coste_imp += (netas_pieza * m2_pieza * 6.5)
        elif pieza["im_f"] == "Offset":
            base_f = 60 if netas_pieza < 100 else (60 + 0.15*(netas_pieza-100) if netas_pieza < 500 else (120 if netas_pieza <= 2000 else 120 + 0.015*(netas_pieza-2000)))
            coste_imp += base_f * (pieza["nt_f"] + (1 if pieza["ba_f"] else 0))
        # Dorso
        if pieza["im_d"] == "Digital": coste_imp += (netas_pieza * m2_pieza * 6.5)
        elif pieza["im_d"] == "Offset":
            base_d = 60 if netas_pieza < 100 else (60 + 0.15*(netas_pieza-100) if netas_pieza < 500 else (120 if netas_pieza <= 2000 else 120 + 0.015*(netas_pieza-2000)))
            coste_imp += base_d * (pieza["nt_d"] + (1 if pieza["ba_d"] else 0))
            
        # Acab & Corte
        coste_acab = h_proceso * m2_pieza * PRECIOS["peliculado"][pieza["pe"]]
        if pieza["ld"]: coste_acab += (h_proceso * m2_pieza * 0.40) # Plus laminado digital estimado
        
        if pieza["co"] == "Troquelado":
            f_f = 107.7 if (pieza["h"] > 1000 or pieza["w"] > 700) else (80.77 if (pieza["h"] == 1000 and pieza["w"] == 700) else 48.19)
            v_v = 0.135 if (pieza["h"] > 1000 or pieza["w"] > 700) else (0.09 if (pieza["h"] == 1000 and pieza["w"] == 700) else 0.06)
            coste_cor = f_f + (h_proceso * v_v)
        else: coste_cor = h_proceso * 1.5
        
        sub_pz = coste_mats + coste_imp + coste_acab + coste_cor
        coste_total_formas += sub_pz
        detalles_formas.append({"Pieza": idx+1, "Mat": coste_mats, "Imp": coste_imp, "Acab": coste_acab, "Corte": coste_cor, "Total": sub_pz})

    # Manipulación (Cálculo en SEGUNDOS)
    coste_man = ((segundos_mueble / 3600) * 18 * cant_objetivo) + (cant_objetivo * dif_ud)
    coste_ext = sum(PRECIOS["extras"][e["n"]] * e["q"] * cant_objetivo for e in lista_extras)
    
    coste_total_fab = coste_total_formas + coste_man + coste_ext
    pvp_total = coste_total_fab * margen_com
    
    desgloses_tecnicos[cant_objetivo] = {"detalles": detalles_formas, "man": coste_man + coste_ext, "total": coste_total_fab}
    res_tabla.append({"Cantidad": cant_objetivo, "C. Fab Total": f"{coste_total_fab:.2f}€", "PVP Proyecto": f"{pvp_total:.2f}€", "PVP Unidad": f"{(pvp_total/cant_objetivo):.2f}€"})

# --- SALIDA ---
if res_tabla:
    st.header("📊 Resumen del Escandallo")
    st.dataframe(pd.DataFrame(res_tabla), use_container_width=True)
    st.header("🔍 Desglose por Cantidad")
    for q_uds, info in desgloses_tecnicos.items():
        with st.expander(f"Ver detalle para {q_uds} unidades"):
            st.table(pd.DataFrame(info["detalles"]).style.format("{:.2f}€", subset=["Mat", "Imp", "Acab", "Corte", "Total"]))
            st.write(f"**Mano de Obra (Segundos) y Accesorios:** {info['man']:.2f} €")
            st.write(f"**COSTE TOTAL FABRICACIÓN:** {info['total']:.2f} €")
            st.write(f"**PVP FINAL (x{margen_com}): {(info['total']*margen_com):.2f} €**")
