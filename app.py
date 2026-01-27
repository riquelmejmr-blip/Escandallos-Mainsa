import streamlit as st
import pandas as pd
import json

# --- 1. BASE DE DATOS Y CONSTANTES ---
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
        "Doble Micro / Doble Doble": {"C/C": 1.046, "B/C": 1.1, "B/B": 1.276, "peg": 0.263},
        "AC (Cuero/Cuero)": {"C/C": 2.505, "peg": 0.217}
    },
    "peliculado": {
        "Sin Peliculado": 0, "Polipropileno": 0.26, "Poliéster brillo": 0.38, "Poliéster mate": 0.64
    },
    "extras_base": {
        "CINTA D/CARA": 0.26, "CINTA LOHMAN": 0.49, "CINTA GEL": 1.2,
        "GOMA TERMINALES": 0.079, "IMAN 20x2mm": 1.145, "TUBOS": 1.06,
        "REMACHES": 0.049, "VELCRO": 0.43, "PUNTO ADHESIVO": 0.08
    }
}

# --- LÓGICA ESPECÍFICA CAJA CANAL 5 (MODELO PLANO) ---
def calcular_coste_caja_canal5(m1, m2, m3, q):
    if q <= 0: return 0.0
    # Normalización
    dimensiones = sorted([m1, m2, m3], reverse=True)
    mayor, intermedia, menor = dimensiones[0], dimensiones[1], dimensiones[2]
    
    area_base = mayor * intermedia
    coste_250 = (0.00000091 * area_base) + 1.00
    
    if q >= 250:
        # Curva de aprendizaje
        coste_u = coste_250 * ((q / 250) ** -0.32)
    elif q == 100:
        coste_u = 2.69
    elif 100 < q < 250:
        # Interpolación lineal
        progreso = (q - 100) / (250 - 100)
        coste_u = 2.69 + progreso * (coste_250 - 2.69)
    else:
        # Para menos de 100, mantenemos el precio de 100 por seguridad industrial
        coste_u = 2.69
        
    return coste_u

def calcular_mermas(n, es_digital=False):
    if es_digital: return n * 0.10, 0 
    if n < 100: return 15, 135
    if n < 200: return 30, 150
    if n < 600: return 40, 160
    if n < 1000: return 50, 170
    if n < 2000: return 60, 170
    return 120, 170

# --- 2. INICIALIZACIÓN ---
st.set_page_config(page_title="ESCANDALLO MAINSA", layout="wide")

def crear_forma_vacia(index):
    return {
        "nombre": f"Forma {index + 1}", "tipo_trabajo": "Escandallo Estándar",
        "pliegos": 1.0, "w": 0, "h": 0, "alto": 0,
        "pf": "Ninguno", "gf": 0, "pl": "Ninguna", "ap": "C/C", 
        "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, 
        "im_d": "No", "nt_d": 0, "ba_d": False, "pel": "Sin Peliculado", 
        "pel_d": "Sin Peliculado", "ld": False, "ld_d": False, 
        "cor": "Troquelado", "cobrar_arreglo": True
    }

if 'piezas_dict' not in st.session_state: st.session_state.piezas_dict = {0: crear_forma_vacia(0)}
if 'lista_extras_grabados' not in st.session_state: st.session_state.lista_extras_grabados = []
for key in ['brf', 'com', 'ver', 'cli', 'des']:
    if key not in st.session_state: st.session_state[key] = ""

st.markdown("""<style>
    .comercial-box { background-color: white; padding: 30px; border: 2px solid #1E88E5; border-radius: 10px; color: #333; }
    .header-info { display: flex; justify-content: space-around; background: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
    .comercial-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    .comercial-table th { background-color: #1E88E5; color: white; padding: 10px; }
    .comercial-table td { padding: 10px; border: 1px solid #ddd; text-align: center; }
</style>""", unsafe_allow_html=True)

st.title("ESCANDALLO MAINSA")

# --- 3. PANEL LATERAL ---
with st.sidebar:
    st.header("⚙️ Ajustes Globales")
    st.session_state.brf = st.text_input("Nº de Briefing", st.session_state.brf)
    st.session_state.cli = st.text_input("Cliente", st.session_state.cli)
    st.session_state.com = st.text_input("Nº de Comercial", st.session_state.com)
    st.session_state.ver = st.text_input("Versión", st.session_state.ver)
    st.session_state.des = st.text_area("Descripción", st.session_state.des)
    st.divider()
    cants_str = st.text_input("Cantidades (separadas por coma)", "0")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    unidad_t = st.radio("Manipulación en:", ["Segundos", "Minutos"], horizontal=True)
    t_input = st.number_input(f"Tiempo ({unidad_t})", value=0)
    seg_man_total = t_input * 60 if unidad_t == "Minutos" else t_input
    dif_ud = st.selectbox("Dificultad (€/ud)", [0.02, 0.061, 0.091], index=2)
    imp_fijo = st.number_input("Importe Fijo por Trabajo (€)", value=500)
    margen = st.number_input("Multiplicador Comercial", value=2.2, step=0.1)
    st.divider()
    modo_comercial = st.checkbox("🌟 VISTA OFERTA COMERCIAL", value=False)
    
# --- 4. GESTIÓN DE FORMAS ---
if not modo_comercial:
    if st.button("➕ Añadir Nueva Forma"):
        nid = max(st.session_state.piezas_dict.keys()) + 1
        st.session_state.piezas_dict[nid] = crear_forma_vacia(nid); st.rerun()

    for p_id, p in st.session_state.piezas_dict.items():
        with st.expander(f"🛠 {p['nombre']}", expanded=True):
            # Selector de tipo de cálculo
            p['tipo_trabajo'] = st.selectbox("Tipo de Pieza", ["Escandallo Estándar", "Caja Canal 5 (Plano)", "En Volumen (Próximamente)", "Guainas (Próximamente)"], index=["Escandallo Estándar", "Caja Canal 5 (Plano)", "En Volumen (Próximamente)", "Guainas (Próximamente)"].index(p.get('tipo_trabajo', "Escandallo Estándar")), key=f"tipo_{p_id}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                p['nombre'] = st.text_input("Etiqueta", p['nombre'], key=f"n_{p_id}")
                p['h'] = st.number_input("Largo mm", 0, 5000, int(p['h']), key=f"h_{p_id}")
                p['w'] = st.number_input("Ancho mm", 0, 5000, int(p['w']), key=f"w_{p_id}")
                if p['tipo_trabajo'] == "Caja Canal 5 (Plano)":
                    p['alto'] = st.number_input("Alto mm", 0, 5000, int(p.get('alto',0)), key=f"alt_{p_id}")

            if p['tipo_trabajo'] == "Escandallo Estándar":
                with col1:
                    p['pliegos'] = st.number_input("Pliegos/Ud", 0.0, 100.0, float(p['pliegos']), key=f"p_{p_id}")
                    p['im'] = st.selectbox("Sistema Cara", ["Offset", "Digital", "No"], key=f"im_{p_id}")
                    p['pel'] = st.selectbox("Peliculado Cara", list(PRECIOS["peliculado"].keys()), key=f"pel_{p_id}")
                with col2:
                    p['pf'] = st.selectbox("C. Frontal", list(PRECIOS["cartoncillo"].keys()), key=f"pf_{p_id}")
                    p['gf'] = st.number_input("Gramaje F.", value=int(p['gf']), key=f"gf_{p_id}")
                    p['pl'] = st.selectbox("Plancha Base", list(PRECIOS["planchas"].keys()), key=f"pl_{p_id}")
                    p['ap'] = st.selectbox("Calidad", ["C/C", "B/C", "B/B"], key=f"ap_{p_id}")
                with col3:
                    p['cor'] = st.selectbox("Corte", ["Troquelado", "Plotter"], key=f"cor_{p_id}")
                    p['cobrar_arreglo'] = st.checkbox("¿Cobrar Arreglo?", value=p.get('cobrar_arreglo', True), key=f"arr_{p_id}")
            else:
                with col2:
                    st.info(f"✨ Modelo Matemático: {p['tipo_trabajo']}")
                    st.write("Cálculo basado en modelo industrial parametrizado.")
            
            if st.button("🗑 Borrar Forma", key=f"del_{p_id}"): 
                del st.session_state.piezas_dict[p_id]; st.rerun()

# --- 5. MOTOR DE CÁLCULO ACTUALIZADO ---
res_final, desc_full = [], {}
if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
    for q_n in lista_cants:
        coste_f, det_f = 0.0, []
        # Calcular mermas globales solo para piezas estándar
        tiene_dig = any(pz["im"] == "Digital" for pz in st.session_state.piezas_dict.values() if pz['tipo_trabajo']=="Escandallo Estándar")
        mn_m, _ = calcular_mermas(q_n, es_digital=tiene_dig); qp_taller = q_n + mn_m
        
        for p_id, p in st.session_state.piezas_dict.items():
            if p['tipo_trabajo'] == "Caja Canal 5 (Plano)":
                # --- APLICAR PROMPT DE CAJAS ---
                coste_u_caja = calcular_coste_caja_canal5(p['h'], p['w'], p['alto'], q_n)
                sub = coste_u_caja * q_n
                coste_f += sub
                det_f.append({"Pieza": p["nombre"] + " (Caja)", "Subtotal": sub, "Nota": "Modelo Caja Canal 5"})
            else:
                # --- LÓGICA ESTÁNDAR ---
                nb = q_n * p["pliegos"]
                mn, mi = calcular_mermas(nb, p["im"]=="Digital")
                hc, hp = nb+mn+mi, nb+mn; m2 = (p["w"]*p["h"])/1_000_000
                c_cf = (hc*m2*(p.get('gf',0)/1000)*PRECIOS["cartoncillo"][p["pf"]]["precio_kg"])
                c_cd = (hc*m2*(p.get('gd',0)/1000)*PRECIOS["cartoncillo"][p["pd"]]["precio_kg"])
                c_pla = hp * m2 * PRECIOS["planchas"][p["pl"]][p["ap"]] if p["pl"] != "Ninguna" else 0
                
                # Arreglo y tiraje con el criterio de 1000x700
                if p['h'] > 1000 or p['w'] > 700: v_arr, v_tir = 107.80, 0.135
                elif p['h'] < 1000 and p['w'] < 700: v_arr, v_tir = 48.19, 0.06
                else: v_arr, v_tir = 80.77, 0.09
                
                c_arr = v_arr if (p["cor"]=="Troquelado" and p.get('cobrar_arreglo', True)) else 0
                c_tir = (hp * v_tir) if p["cor"]=="Troquelado" else hp*1.5
                
                sub = c_cf + c_cd + c_pla + c_arr + c_tir
                coste_f += sub
                det_f.append({"Pieza": p["nombre"], "Subtotal": sub, "Nota": "Escandallo Estándar"})

        c_ext_tot = sum(e["coste"] * e["cantidad"] * qp_taller for e in st.session_state.lista_extras_grabados)
        c_mo = ((seg_man_total/3600)*18*qp_taller) + (qp_taller*dif_ud)
        t_fab = coste_f + c_mo + c_ext_tot + imp_fijo
        res_final.append({"Cant": q_n, "Total": f"{(t_fab*margen):.2f}€", "Ud": f"{(t_fab*margen/q_n):.2f}€"})

# --- 6. SALIDA ---
if modo_comercial:
    # (Mantenemos la lógica de visualización de la oferta comercial de la v27)
    st.subheader("Vista Comercial Generada")
    st.table(res_final)
else:
    if res_final:
        st.header(f"📊 Resultados: {st.session_state.cli}")
        st.dataframe(pd.DataFrame(res_final), use_container_width=True)
