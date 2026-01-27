import streamlit as st
import pandas as pd
import json

# --- 1. CONFIGURACIÓN INTERNA (TOTALMENTE OCULTA AL COMERCIAL) ---
MARGEN_COMERCIAL = 2.2
IMPORTE_FIJO_VENTA = 500.0  # Se suma directamente al PVP final
COSTO_HORA_MANIPULACION = 18.0
DIFICULTAD_ESTANDAR = 0.091

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
    "laminado_digital": 3.5,
    "extras_base": {
        "CINTA D/CARA": 0.26, "CINTA LOHMAN": 0.49, "CINTA GEL": 1.2,
        "GOMA TERMINALES": 0.079, "IMAN 20x2mm": 1.145, "TUBOS": 1.06,
        "REMACHES": 0.049, "VELCRO": 0.43, "PUNTO ADHESIVO": 0.08
    }
}

# --- 2. MOTORES TÉCNICOS ---

def calcular_mermas(n, es_digital=False):
    if es_digital: return n * 0.10, 0 
    if n < 100: return 15, 135
    if n < 200: return 30, 150
    if n < 600: return 40, 160
    if n < 1000: return 50, 170
    if n < 2000: return 60, 170
    return 120, 170

def motor_embalajes(tipo, largo, ancho, alto, q):
    if q <= 0: return 0.0
    if tipo == "Plano (Canal 5)":
        dims = sorted([largo, ancho, alto], reverse=True)
        mayor, intermedia = dims[0], dims[1]
        area_base = mayor * intermedia
        coste_250 = (0.00000091 * area_base) + 1.00
        if q >= 250: return coste_250 * ((q / 250) ** -0.32)
        elif q == 100: return 2.69
        elif 100 < q < 250:
            progreso = (q - 100) / (250 - 100)
            return 2.69 + progreso * (coste_250 - 2.69)
        else: return 2.69
    return 0.0

# --- 3. INICIALIZACIÓN ---
st.set_page_config(page_title="MAINSA VENTAS", layout="wide")

def crear_forma_vacia(index):
    return {
        "nombre": f"Forma {index + 1}", "pliegos": 1.0, "w": 0, "h": 0, 
        "pf": "Ninguno", "gf": 0, "pl": "Ninguna", "ap": "C/C", 
        "pd": "Ninguno", "gd": 0, "im": "Offset", "nt": 4, "ba": False, 
        "im_d": "No", "nt_d": 0, "ba_d": False, "pel": "Sin Peliculado", 
        "pel_d": "Sin Peliculado", "ld": False, "ld_d": False, 
        "cor": "Troquelado", "cobrar_arreglo": True
    }

if 'piezas_dict' not in st.session_state: st.session_state.piezas_dict = {0: crear_forma_vacia(0)}
if 'lista_extras_grabados' not in st.session_state: st.session_state.lista_extras_grabados = []
if 'lista_embalajes' not in st.session_state: st.session_state.lista_embalajes = []

st.markdown("""<style>
    .comercial-box { background-color: white; padding: 30px; border: 2px solid #1E88E5; border-radius: 10px; color: #333; }
    .comercial-header { color: #1E88E5; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .comercial-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 1.1em; }
    .comercial-table th { background-color: #1E88E5; color: white; padding: 10px; }
    .comercial-table td { padding: 10px; border: 1px solid #ddd; text-align: center; }
</style>""", unsafe_allow_html=True)

st.title("💼 GESTOR COMERCIAL")

# --- 4. PANEL LATERAL ---
with st.sidebar:
    st.header("⚙️ Datos del Proyecto")
    st.session_state.brf = st.text_input("Nº de Briefing", st.session_state.get('brf', ""))
    st.session_state.cli = st.text_input("Cliente", st.session_state.get('cli', ""))
    st.session_state.com = st.text_input("Comercial", st.session_state.get('com', ""))
    st.session_state.ver = st.text_input("Versión", st.session_state.get('ver', "1.0"))
    st.session_state.des = st.text_area("Descripción", st.session_state.get('des', ""))
    st.divider()
    cants_str = st.text_input("Cantidades (ej: 500, 1000)", "0")
    lista_cants = [int(x.strip()) for x in cants_str.split(",") if x.strip().isdigit()]
    
    unidad_t = st.radio("Manipulación en:", ["Segundos", "Minutos"], horizontal=True)
    t_input = st.number_input(f"Tiempo montaje/ud", value=0)
    seg_man_total = t_input * 60 if unidad_t == "Minutos" else t_input
    
    st.divider()
    st.header("📂 Archivos")
    partes_nombre = [st.session_state.brf, st.session_state.cli]
    nombre_archivo = "PV_" + "_".join([str(p).strip() for p in partes_nombre if str(p).strip()]) + ".json"
    
    datos_exp = {
        "brf": st.session_state.brf, "cli": st.session_state.cli, "com": st.session_state.com, 
        "piezas": st.session_state.piezas_dict, "extras": st.session_state.lista_extras_grabados,
        "embalajes": st.session_state.lista_embalajes
    }
    st.download_button("💾 Guardar Proyecto", json.dumps(datos_exp, indent=4), file_name=nombre_archivo)
    
    subida = st.file_uploader("📂 Importar JSON", type=["json"])
    if subida:
        di = json.load(subida)
        st.session_state.piezas_dict = {int(k): v for k, v in di["piezas"].items()}
        st.session_state.lista_extras_grabados = di.get("extras", [])
        st.session_state.lista_embalajes = di.get("embalajes", [])
        st.rerun()

# --- 5. GESTIÓN DE PRODUCTO ---
c1, c2 = st.columns([1, 4])
if c1.button("➕ Forma"):
    nid = max(st.session_state.piezas_dict.keys()) + 1
    st.session_state.piezas_dict[nid] = crear_forma_vacia(nid); st.rerun()
if c2.button("🗑 Reiniciar Todo"):
    st.session_state.piezas_dict = {0: crear_forma_vacia(0)}; st.session_state.lista_extras_grabados = []; st.session_state.lista_embalajes = []; st.rerun()

for p_id, p in st.session_state.piezas_dict.items():
    with st.expander(f"🛠 {p['nombre']} - {p['h']}x{p['w']} mm", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            p['nombre'] = st.text_input("Etiqueta", p['nombre'], key=f"n_{p_id}")
            p['pliegos'] = st.number_input("Pliegos/Ud", 0.0, 100.0, float(p['pliegos']), key=f"p_{p_id}")
            p['h'] = st.number_input("Largo mm", 0, 5000, int(p['h']), key=f"h_{p_id}")
            p['w'] = st.number_input("Ancho mm", 0, 5000, int(p['w']), key=f"w_{p_id}")
            p['im'] = st.selectbox("Sistema Cara", ["Offset", "Digital", "No"], index=["Offset", "Digital", "No"].index(p['im']), key=f"im_{p_id}")
            if p['im'] == "Offset":
                p['nt'] = st.number_input("Tintas F.", 0, 6, int(p.get('nt',4)), key=f"nt_{p_id}")
                p['ba'] = st.checkbox("Barniz F.", p.get('ba',False), key=f"ba_{p_id}")
            elif p['im'] == "Digital": p['ld'] = st.checkbox("Laminado Digital F.", p.get('ld',False), key=f"ld_{p_id}")
            p['pel'] = st.selectbox("Peliculado Cara", list(PRECIOS["peliculado"].keys()), index=list(PRECIOS["peliculado"].keys()).index(p.get('pel', 'Sin Peliculado')), key=f"pel_{p_id}")
        
        with col2:
            pf_prev = p['pf']; p['pf'] = st.selectbox("C. Frontal", list(PRECIOS["cartoncillo"].keys()), index=list(PRECIOS["cartoncillo"].keys()).index(p['pf']), key=f"pf_{p_id}")
            if p['pf'] != pf_prev: p['gf'] = PRECIOS["cartoncillo"][p['pf']]["gramaje"]
            if p['pf'] != "Ninguno": p['gf'] = st.number_input("Gramaje F.", value=int(p['gf']), key=f"gf_{p_id}")
            p['pl'] = st.selectbox("Soporte Base", list(PRECIOS["planchas"].keys()), index=list(PRECIOS["planchas"].keys()).index(p['pl']), key=f"pl_{p_id}")
            p['ap'] = st.selectbox("Calidad", ["C/C", "B/C", "B/B"], index=["C/C", "B/C", "B/B"].index(p.get('ap', 'C/C')), key=f"ap_{p_id}")
            p['pd'] = st.selectbox("C. Dorso", list(PRECIOS["cartoncillo"].keys()), index=list(PRECIOS["cartoncillo"].keys()).index(p.get('pd', 'Ninguno')), key=f"pd_{p_id}")
            if p['pd'] != "Ninguno": p['gd'] = st.number_input("Gramaje D.", value=int(p.get('gd',0)), key=f"gd_{p_id}")
            
        with col3:
            p['cor'] = st.selectbox("Corte", ["Troquelado", "Plotter"], index=["Troquelado", "Plotter"].index(p.get('cor', 'Troquelado')), key=f"cor_{p_id}")
            p['cobrar_arreglo'] = st.checkbox("¿Cobrar Arreglo?", value=p.get('cobrar_arreglo', True), key=f"arr_{p_id}")
            if p['pd'] != "Ninguno":
                p['im_d'] = st.selectbox("Sistema Dorso", ["Offset", "Digital", "No"], index=["Offset", "Digital", "No"].index(p.get('im_d', 'No')), key=f"imd_{p_id}")
                if p['im_d'] == "Offset":
                    p['nt_d'] = st.number_input("Tintas D.", 0, 6, int(p.get('nt_d',0)), key=f"ntd_{p_id}")
                    p['ba_d'] = st.checkbox("Barniz D.", p.get('ba_d',False), key=f"bad_{p_id}")
                elif p['im_d'] == "Digital": p['ld_d'] = st.checkbox("Laminado Digital D.", p.get('ld_d',False), key=f"ldd_{p_id}")
                p['pel_d'] = st.selectbox("Peliculado Dorso", list(PRECIOS["peliculado"].keys()), index=list(PRECIOS["peliculado"].keys()).index(p.get('pel_d', 'Sin Peliculado')), key=f"peld_{p_id}")
            if st.button("🗑 Borrar Forma", key=f"del_{p_id}"): del st.session_state.piezas_dict[p_id]; st.rerun()

st.divider(); st.subheader("📦 Accesorios y Embalajes")
col_acc, col_emb = st.columns(2)

with col_acc:
    ex_sel = st.selectbox("Añadir extra:", ["---"] + list(PRECIOS["extras_base"].keys()))
    if st.button("➕ Añadir Accesorio") and ex_sel != "---":
        st.session_state.lista_extras_grabados.append({"nombre": ex_sel, "coste": PRECIOS["extras_base"][ex_sel], "cantidad": 1.0}); st.rerun()
    for i, ex in enumerate(st.session_state.lista_extras_grabados):
        ca, cb = st.columns([4, 1])
        ex['cantidad'] = ca.number_input(f"{ex['nombre']} (Cant/Ud)", value=float(ex['cantidad']), key=f"exq_{i}")
        if cb.button("🗑", key=f"exd_{i}"): st.session_state.lista_extras_grabados.pop(i); st.rerun()

with col_emb:
    tipo_em = st.selectbox("Tipo de Caja:", ["Plano (Canal 5)", "En Volumen", "Guainas"])
    if st.button("➕ Añadir Embalaje"):
        st.session_state.lista_embalajes.append({"tipo": tipo_em, "l": 0, "w": 0, "a": 0, "uds": 1}); st.rerun()
    for i, em in enumerate(st.session_state.lista_embalajes):
        with st.info(f"Embalaje {i+1}"):
            ce1, ce2, ce3, ce4, ce5 = st.columns(5)
            em['l'], em['w'], em['a'], em['uds'] = ce1.number_input("L", value=em['l'], key=f"el_{i}"), ce2.number_input("W", value=em['w'], key=f"ew_{i}"), ce3.number_input("A", value=em['a'], key=f"ea_{i}"), ce4.number_input("C/U", value=em['uds'], key=f"eu_{i}")
            if ce5.button("🗑", key=f"ed_{i}"): st.session_state.lista_embalajes.pop(i); st.rerun()

# --- 6. MOTOR DE CÁLCULO ---
res_final = []
if lista_cants and st.session_state.piezas_dict and sum(lista_cants) > 0:
    for q_n in lista_cants:
        tiene_dig = any(pz["im"] == "Digital" or pz.get("im_d") == "Digital" for pz in st.session_state.piezas_dict.values())
        mn_m, _ = calcular_mermas(q_n, es_digital=tiene_dig); qp_taller = q_n + mn_m; coste_f = 0.0
        
        for p in st.session_state.piezas_dict.values():
            nb = q_n * p["pliegos"]; mn, mi = calcular_mermas(nb, p["im"]=="Digital")
            hc, hp = nb+mn+mi, nb+mn; m2 = (p["w"]*p["h"])/1_000_000
            
            c_mat = (hc*m2*(p.get('gf',0)/1000)*PRECIOS["cartoncillo"][p["pf"]]["precio_kg"])
            c_mat += (hc*m2*(p.get('gd',0)/1000)*PRECIOS["cartoncillo"][p.get('pd','Ninguno')]["precio_kg"])
            if p["pl"] != "Ninguna":
                c_mat += hp * m2 * PRECIOS["planchas"][p["pl"]][p.get('ap','C/C')]
                pas = (1 if p["pf"]!="Ninguno" else 0) + (1 if p.get('pd','Ninguno')!="Ninguno" else 0)
                c_mat += hp * m2 * PRECIOS["planchas"][p["pl"]]["peg"] * pas
            
            def f_o(n): return 60 if n < 100 else (120 if n > 500 else 60 + 0.15*(n-100))
            c_imp = (nb*m2*6.5 if p["im"]=="Digital" else (f_o(nb)*(p.get('nt',4)+(1 if p.get('ba') else 0)) if p["im"]=="Offset" else 0))
            c_imp += (nb*m2*6.5 if p.get('im_d')=="Digital" else (f_o(nb)*(p.get('nt_d',0)+(1 if p.get('ba_d') else 0)) if p.get('im_d')=="Offset" else 0))
            c_aca = (hp*m2*PRECIOS["peliculado"][p.get('pel','Sin Peliculado')]) + (hp*m2*3.5 if p.get("ld") else 0)
            c_aca += (hp*m2*PRECIOS["peliculado"].get(p.get('pel_d','Sin Peliculado'), 0)) + (hp*m2*3.5 if p.get("ld_d") else 0)
            
            l_p, w_p = p['h'], p['w']
            if l_p > 1000 or w_p > 700: v_arr, v_tir = 107.80, 0.135
            elif l_p < 1000 and w_p < 700: v_arr, v_tir = 48.19, 0.06
            else: v_arr, v_tir = 80.77, 0.09
            
            coste_f += (v_arr if p.get('cobrar_arreglo') else 0) + (hp * v_tir if p['cor']=="Troquelado" else hp*1.5)
            coste_f += (c_mat + c_imp + c_aca)

        c_ext_tot = sum(e["coste"] * e["cantidad"] * qp_taller for e in st.session_state.lista_extras_grabados)
        c_em_tot = sum(motor_embalajes(em['tipo'], em['l'], em['w'], em['a'], q_n*em['uds']) * (q_n*em['uds']) for em in st.session_state.lista_embalajes)
        c_mo = ((seg_man_total/3600)*COSTO_HORA_MANIPULACION*qp_taller) + (qp_taller*DIFICULTAD_ESTANDAR)
        
        # --- NUEVA FÓRMULA PVP: (Costes * Margen) + 500 Fijos ---
        total_costes_taller = coste_f + c_mo + c_ext_tot + c_em_tot
        pvp_total = (total_costes_taller * MARGEN_COMERCIAL) + IMPORTE_FIJO_VENTA
        
        res_final.append({"Cant": f"{q_n} uds", "PVP TOTAL": f"{pvp_total:.2f}€", "UNITARIO": f"{pvp_total/q_n:.2f}€"})

# --- 7. SALIDA VISUAL ---
if res_final:
    st.divider()
    st.markdown(f"""<div class="comercial-box">
        <h2 class="comercial-header">OFERTA COMERCIAL - {st.session_state.cli}</h2>
        <table class="comercial-table">
            <tr><th>Cantidad</th><th>Precio de Venta</th><th>Precio Unitario</th></tr>
            {"".join([f"<tr><td>{r['Cant']}</td><td><b>{r['PVP TOTAL']}</b></td><td>{r['UNITARIO']}</td></tr>" for r in res_final])}
        </table>
    </div>""", unsafe_allow_html=True)
