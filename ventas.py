import streamlit as st
import pandas as pd
import json

# --- 0. CONFIGURACIÓN DE ACCESO (USUARIOS) ---
# Puedes añadir aquí los usuarios que necesites
USUARIOS = {
    "comercial1": "mainsa2026",
    "comercial2": "ventas2026",
    "admin": "adminmainsa"
}

def check_password():
    """Devuelve True si el usuario ha introducido credenciales válidas."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True

    # Diseño de la pantalla de Login
    st.markdown("""<style>
        .login-box { 
            max-width: 400px; 
            margin: 100px auto; 
            padding: 20px; 
            border: 1px solid #ddd; 
            border-radius: 10px; 
            background: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
    </style>""", unsafe_allow_html=True)

    with st.container():
        st.title("🔐 Acceso Mainsa Ventas")
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Entrar"):
            if user in USUARIOS and USUARIOS[user] == password:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("⚠️ Usuario o contraseña incorrectos")
    return False

# --- 1. CONFIGURACIÓN INTERNA (OCULTA) ---
MARGEN_COMERCIAL = 2.2
IMPORTE_FIJO_VENTA = 500.0
COSTO_HORA_MANIPULACION = 18.0
DIFICULTAD_ESTANDAR = 0.091

# Si no pasa el login, detenemos la ejecución aquí
if not check_password():
    st.stop()

# --- SI LLEGA AQUÍ, EL USUARIO ESTÁ LOGUEADO ---

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

# (Aquí irían el resto de funciones calcular_mermas y motor_embalajes idénticas a las anteriores)
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
        area_base = dims[0] * dims[1]
        coste_250 = (0.00000091 * area_base) + 1.00
        if q >= 250: return coste_250 * ((q / 250) ** -0.32)
        elif q == 100: return 2.69
        elif 100 < q < 250:
            progreso = (q - 100) / (250 - 100)
            return 2.69 + progreso * (coste_250 - 2.69)
        else: return 2.69
    return 0.0

# --- INICIALIZACIÓN DE ESTADO ---
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

# --- EL RESTO DE LA ESTRUCTURA DE LA INTERFAZ Y CÁLCULOS QUE YA TENEMOS ---
# (Formas, Extras, Embalajes y Motor de Cálculo PVP con el Fijo de 500€ al final)

st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.update({"authenticated": False}))

# ... (Insertar aquí el resto del código de la interfaz que ya validamos)
