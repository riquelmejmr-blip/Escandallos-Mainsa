"""MAINSA Compras: visor interno de costes guardados en JSON V44/V45.

Arranque: python -m streamlit run app-compras.py
Solo necesita Streamlit. No modifica archivos ni recalcula tarifas o escandallos.
"""

import csv
import hashlib
import html
import io
import json
import math
import re
import unicodedata

import streamlit as st


ETIQUETAS = {
    "cartoncillo": "Cartoncillo", "ondulado": "Plancha ondulada",
    "rigidos": "Materiales rígidos", "extras": "Extras y accesorios",
    "embalajes_compra": "Embalajes", "contracolado": "Contracolado",
    "impresion": "Impresión", "peliculado": "Peliculado y laminado",
    "corte": "Corte · troquelado / plotter", "stamping": "Stamping",
    "manipulacion": "Manipulación", "dificultad": "Dificultad de producción",
    "externos": "Servicios externos",
}
MATERIALES = ("cartoncillo", "ondulado", "rigidos", "extras", "embalajes_compra")
PROCESOS = ("contracolado", "impresion", "peliculado", "corte", "stamping", "manipulacion", "dificultad", "externos")
DETALLE = ("Cartoncillo Cara", "Cartoncillo Dorso", "Plancha Ondulado", "Material Rígido", "Contracolado", "Impresión", "Peliculado", "Corte (Troquel/Plotter)", "Stamping")
LIMITE_BYTES = 10 * 1024 * 1024


def numero(value):
    """Un dato ausente, booleano o inválido nunca se interpreta como cero."""
    if type(value) not in (int, float):
        return None
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (OverflowError, ValueError):
        return None


def texto(value, defecto=""):
    return str(value) if isinstance(value, (str, int, float)) and not isinstance(value, bool) else defecto


def euros(value, decimales=2):
    value = numero(value)
    if value is None:
        return "No disponible"
    formatted = f"{value:,.{decimales}f}".translate(str.maketrans({",": ".", ".": ","}))
    return formatted + " €"


def entero(value):
    return f"{int(value):,}".replace(",", ".")


def suma_conocida(values):
    values = list(values)
    return sum(values) if values and all(numero(v) is not None for v in values) else None


def mapa(value):
    return value if isinstance(value, dict) else {}


def registros(value):
    return [r for r in value if isinstance(r, dict)] if isinstance(value, list) else []


def leer_json(content, filename="Escandallo.json"):
    if len(content) > LIMITE_BYTES:
        raise ValueError("El archivo supera los 10 MB. Exporta solo el escandallo que necesitas.")
    try:
        raw = json.loads(content.decode("utf-8-sig"), parse_constant=lambda _: (_ for _ in ()).throw(ValueError("El JSON contiene números no válidos.")))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("El archivo no es un JSON válido en UTF-8. Selecciona el JSON interno de MAINSA.") from exc
    return normalizar_proyecto(raw, filename, hashlib.sha256(content).hexdigest())


def normalizar_proyecto(raw, filename="Escandallo.json", identidad=None):
    if not isinstance(raw, dict):
        raise ValueError("El archivo debe contener un proyecto MAINSA en formato JSON.")
    summary, purchases = mapa(raw.get("resumen_costes")), mapa(raw.get("compras_legible"))
    quantities = set()
    for key in set(summary) | set(purchases):
        if isinstance(key, str) and re.fullmatch(r"[1-9]\d{0,11}", key) and (
            isinstance(summary.get(key), dict) or isinstance(purchases.get(key), dict)
        ):
            quantities.add(int(key))
    if not quantities:
        raise ValueError("Este JSON no contiene un desglose de costes por cantidad. Ábrelo en MAINSA, pulsa Calcular y exporta de nuevo el JSON interno.")
    pieces = raw.get("piezas")
    pieces = registros(list(pieces.values()) if isinstance(pieces, dict) else pieces)
    return {
        "raw": raw, "cantidades": sorted(quantities), "piezas": pieces,
        "archivo": filename, "referencia": texto(raw.get("brf"), "Sin referencia"),
        "version": texto(raw.get("version")), "cliente": texto(raw.get("cli"), "Cliente sin indicar"),
        "descripcion": texto(raw.get("desc"), "Escandallo sin descripción"),
        "motor": texto(mapa(raw.get("_schema")).get("app"), "MAINSA · versión no indicada"),
        "id": identidad or hashlib.sha256(json.dumps(raw, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest(),
    }


def vista_cantidad(project, cantidad):
    if cantidad not in project["cantidades"]:
        raise ValueError("No hay un cálculo guardado para esta cantidad.")
    raw = project["raw"]
    summary = mapa(mapa(raw.get("resumen_costes")).get(str(cantidad)))
    purchase = mapa(mapa(raw.get("compras_legible")).get(str(cantidad)))
    warnings, rows = [], []
    for source in (summary, purchase):
        if numero(source.get("Cantidad")) is not None and source["Cantidad"] != cantidad:
            warnings.append("La cantidad del desglose no coincide con la opción seleccionada.")
    for group, keys, primary, secondary in (
        ("Materiales", MATERIALES, mapa(summary.get("materiales")), mapa(purchase.get("Materiales"))),
        ("Procesos", PROCESOS, mapa(summary.get("procesos")), mapa(purchase.get("Procesos"))),
    ):
        for key in dict.fromkeys((*keys, *primary, *secondary)):
            a, b = numero(primary.get(key)), numero(secondary.get(key))
            amount = a if key in primary else b
            if a is not None and b is not None and abs(a - b) > 0.02:
                warnings.append(f"Los resúmenes no coinciden en {ETIQUETAS.get(key, key)}. Se muestra resumen_costes.")
            rows.append({"grupo": group, "clave": key, "concepto": ETIQUETAS.get(key, key), "total": amount, "unitario": amount / cantidad if amount is not None else None})
    totals = mapa(summary.get("totales"))
    calculated = [suma_conocida(r["total"] for r in rows if r["grupo"] == group) for group in ("Materiales", "Procesos")]
    material = numero(totals.get("materiales_total"))
    material = calculated[0] if material is None else material
    process = numero(totals.get("procesos_total"))
    process = calculated[1] if process is None else process
    total = numero(totals.get("coste_total_compra_estimado"))
    total = suma_conocida((material, process)) if total is None else total
    for label, subtotal, saved in zip(("materiales", "procesos"), calculated, (material, process)):
        if subtotal is not None and saved is not None and abs(subtotal - saved) > 0.02:
            warnings.append(f"La suma de {label} difiere del total guardado. Revisa el JSON en MAINSA.")
    if total is not None and material is not None and process is not None and abs(material + process - total) > 0.02:
        warnings.append("El coste total guardado no coincide con materiales más procesos.")
    if any(r["total"] is None for r in rows):
        warnings.append("Hay partidas sin un importe válido guardado. Se indican como no disponibles; no se consideran cero.")
    optional = summary.get("opcionales_a_parte")
    optional = optional if isinstance(optional, dict) else mapa(purchase.get("Opcionales (a parte)"))
    optionals = []
    for key, label in (("rellenado", "Rellenado"), ("armado", "Armado")):
        amount = numero(optional.get(key + "_total_coste"))
        unit = numero(optional.get(key + "_unit_coste"))
        if amount is None and unit is not None:
            amount = unit * cantidad
        optionals.append({"concepto": label, "total": amount})
    details = registros(purchase.get("Detalle piezas"))
    pending = []
    if any((numero(p.get("pv_troquel")) or 0) > 0 for p in project["piezas"]):
        pending.append("Fabricación del troquel: el JSON contiene un precio de venta, pero no identifica su coste de compra. No está sumado al total.")
    if (numero(mapa(raw.get("params")).get("imp_fijo_pvp")) or 0) > 0:
        pending.append("Desarrollo: el importe fijo del JSON es de venta. Su coste de compra no está identificado ni sumado al total.")
    if not details:
        pending.append("Este JSON no incluye detalle por formato. Se muestran los costes agregados que sí contiene.")
    return {
        "cantidad": cantidad, "filas": rows, "materiales": material, "procesos": process,
        "total": total, "unitario": total / cantidad if total is not None else None,
        "opcionales": optionals, "opcionales_total": suma_conocida(o["total"] for o in optionals),
        "formas": details, "embalajes": registros(purchase.get("Detalle embalajes")),
        "externos": registros(purchase.get("Detalle externos")), "extras": registros(purchase.get("Extras (detalle)")),
        "avisos": list(dict.fromkeys(warnings)), "pendientes": pending,
    }


def crear_csv(project, view):
    def amount(value):
        return "NO DISPONIBLE" if value is None else f"{value:.4f}".replace(".", ",")

    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter=";", quoting=csv.QUOTE_ALL, lineterminator="\r\n")

    def row(values):
        # Evita fórmulas de hoja de cálculo procedentes de nombres importados.
        writer.writerow(["'" + str(v) if str(v).startswith(("=", "+", "-", "@", "\t", "\r")) else str(v) for v in values])

    for key, value in (("Referencia", project["referencia"]), ("Revisión", project["version"]), ("Cliente", project["cliente"]), ("Cantidad", view["cantidad"])):
        row((key, value))
    row(("Fuente", "Costes guardados en el JSON. Opcionales separados del total."))
    row(())
    row(("Grupo", "Concepto", "Coste unitario EUR", "Coste total EUR"))
    for r in view["filas"]:
        row((r["grupo"], r["concepto"], amount(r["unitario"]), amount(r["total"])))
    row(("Total base", "Coste de compra", amount(view["unitario"]), amount(view["total"])))
    for r in view["opcionales"]:
        row(("Opcional separado", r["concepto"], amount(r["total"] / view["cantidad"] if r["total"] is not None else None), amount(r["total"])))
    for detail in view["formas"]:
        for key in DETALLE:
            row(("Formato: " + texto(detail.get("Pieza")), key, "", amount(numero(detail.get(key)))))
    for detail in view["embalajes"]:
        row(("Detalle embalaje", texto(detail.get("nombre")), amount(numero(detail.get("coste_caja_compra"))), amount(numero(detail.get("coste_total_compra")))))
    for detail in view["externos"]:
        row(("Detalle externo", texto(detail.get("concepto")), "", amount(numero(detail.get("coste_total")))))
    for message in view["pendientes"]:
        row(("Pendiente", message))
    for message in view["avisos"]:
        row(("Revisar", message))
    return stream.getvalue().encode("utf-8-sig")


def cargar_proyecto(project, demo=False):
    st.session_state.compras_proyecto = project
    st.session_state.compras_demo = demo
    st.session_state.buscar_partida = ""
    st.session_state.grupo_partidas = "Todas"


def tabla_costes(rows):
    return [{"Grupo": r["grupo"], "Concepto": r["concepto"], "€/unidad": euros(r["unitario"], 3), "Coste total": euros(r["total"])} for r in rows]


def mostrar_detalles(project, view):
    st.subheader("Detalle por formato")
    if not view["formas"]:
        st.info("Este archivo no contiene detalle por formato.")
    for index, detail in enumerate(view["formas"]):
        # Mantener el orden evita confundir disposiciones con nombres iguales.
        piece = project["piezas"][index] if index < len(project["piezas"]) else {}
        if piece.get("nombre") != detail.get("Pieza"):
            piece = next((p for p in project["piezas"] if p.get("nombre") == detail.get("Pieza")), {})
        name = texto(detail.get("Pieza"), f"Formato {index + 1}")
        with st.expander(f"{index + 1:02d} · {name} · {euros(numero(detail.get('Subtotal Pieza')))}"):
            dimensions = [numero(piece.get(k)) for k in ("h", "w")]
            if all(v is not None for v in dimensions):
                st.text(f"Formato: {entero(max(dimensions))} × {entero(min(dimensions))} mm")
            if piece.get("tipo_base") == "Material Rígido":
                st.text("Soporte: " + texto(piece.get("mat_rigido"), "Rígido"))
            else:
                st.text("Plancha: " + texto(piece.get("pl"), "No indicada") + " · " + texto(piece.get("ap")))
            st.text("Corte: " + texto(detail.get("Corte Seleccionado"), "No indicado"))
            st.dataframe([{"Concepto": k, "Coste total": euros(numero(detail.get(k)))} for k in DETALLE], hide_index=True, width="stretch")
    st.subheader("Embalajes, extras y externos")
    tabs = st.tabs(("Embalajes", "Extras y accesorios", "Servicios externos"))
    with tabs[0]:
        if view["embalajes"]:
            st.dataframe([{
                "Embalaje": texto(d.get("nombre")), "Material": texto(d.get("material")), "Tipo": texto(d.get("tipo")),
                "Cajas": texto(d.get("cajas"), "No disponible"), "Unidades/caja": texto(d.get("uds_por_caja"), "No disponible"),
                "Coste/caja": euros(numero(d.get("coste_caja_compra")), 3), "Coste total": euros(numero(d.get("coste_total_compra"))),
            } for d in view["embalajes"]], hide_index=True, width="stretch")
        else:
            st.info("Sin detalle de embalajes guardado. Consulta el importe agregado del desglose.")
    with tabs[1]:
        if view["extras"]:
            st.dataframe([{"Extra": texto(d.get("nombre")), "Coste por elemento": euros(numero(d.get("coste")), 4), "Elementos/unidad de producto": texto(d.get("cantidad"), "No disponible")} for d in view["extras"]], hide_index=True, width="stretch")
            st.caption("El total de estas partidas está incluido en Extras y accesorios del desglose.")
        else:
            st.info("Sin detalle de extras guardado. Consulta el importe agregado del desglose.")
    with tabs[2]:
        if view["externos"]:
            st.dataframe([{"Servicio": texto(d.get("concepto")), "Modalidad": texto(d.get("modo")), "Coste total": euros(numero(d.get("coste_total")))} for d in view["externos"]], hide_index=True, width="stretch")
        else:
            st.info("Sin detalle de externos guardado. Consulta el importe agregado del desglose.")


def main():
    st.set_page_config(page_title="MAINSA · Compras", page_icon="📦", layout="wide")
    st.markdown("""<style>
    .stApp{background:#f5f5f1}h1,h2,h3{color:#203944}section[data-testid=stSidebar]{background:#203944}
    section[data-testid=stSidebar] h2,section[data-testid=stSidebar] p,section[data-testid=stSidebar] label{color:#e6ecec}
    [data-testid=stMetric]{background:white;border:1px solid #e0e4dc;border-radius:8px;padding:18px}
    [data-testid=stMetricValue]{font-size:1.8rem;color:#9d5736}
    .project-card{background:#203944;color:white;padding:25px 30px;border-radius:9px;margin:12px 0 22px}
    .project-card h2{color:white;margin:8px 0 12px;font-size:1.7rem}.project-card small{color:#b4cbd3}
    .project-card p{margin:3px 0 0;color:#c7d5da}.demo-tag{color:#e5ac85;font-size:.7rem;letter-spacing:1.2px}
    </style>""", unsafe_allow_html=True)
    if "compras_proyecto" not in st.session_state:
        cargar_proyecto(normalizar_proyecto(DEMO_DATA, "MAINSA_DEMO_COMPRAS.json"), demo=True)
    with st.sidebar:
        st.title("MAINSA")
        st.subheader("Departamento de Compras")
        uploaded = st.file_uploader("Importar JSON V44 / V45", type=["json"], key="archivo_compras")
        if uploaded is not None:
            content = uploaded.getvalue()
            digest = hashlib.sha256(content).hexdigest()
            if st.session_state.get("compras_ultimo_upload") != digest:
                try:
                    project = leer_json(content, uploaded.name)
                    cargar_proyecto(project)
                    st.session_state.compras_ultimo_upload = digest
                except ValueError as exc:
                    st.error(str(exc) + " Se mantiene el escandallo anterior.")
        if st.button("Cargar ejemplo de demostración", width="stretch"):
            cargar_proyecto(normalizar_proyecto(DEMO_DATA, "MAINSA_DEMO_COMPRAS.json"), demo=True)
        st.download_button("Descargar JSON de ejemplo", json.dumps(DEMO_DATA, ensure_ascii=False, indent=2).encode("utf-8"), "MAINSA_DEMO_COMPRAS.json", "application/json", width="stretch")
        st.divider()
        st.caption("Uso interno · Costes de compra")
        st.caption("El archivo se carga en memoria en el proceso de Streamlit. Esta aplicación no lo guarda en disco ni lo envía a otros servicios.")
    project = st.session_state.compras_proyecto
    st.title("Compras, con todo el detalle.")
    st.caption("Del escandallo a cada material y proceso de producción.")
    escape = lambda value: html.escape(texto(value), quote=True)
    badge = '<span class="demo-tag"> · DEMOSTRACIÓN · DATOS FICTICIOS</span>' if st.session_state.get("compras_demo", False) else ""
    st.markdown(f'<div class="project-card"><small>{escape(project["referencia"])} · VERSIÓN {escape(project["version"] or "Sin revisión")}</small>{badge}<h2>{escape(project["descripcion"])}</h2><p>{escape(project["cliente"])} · {len(project["piezas"])} formatos</p><small>{escape(project["archivo"])} · {escape(project["motor"])}</small></div>', unsafe_allow_html=True)
    values = project["cantidades"]
    quantity = st.selectbox("Cantidad a producir", values, index=values.index(250) if 250 in values else 0, format_func=lambda q: entero(q) + " unidades", key="cantidad_" + project["id"][:16])
    view = vista_cantidad(project, quantity)
    st.caption("Solo cantidades con desglose guardado. Se conservan los costes del JSON; no se actualizan tarifas ni se recalcula el escandallo.")
    for warning in view["avisos"]:
        st.warning(warning)
    for col, label, value, digits in zip(st.columns(4), ("Coste total de compra", "Materiales", "Procesos", "Coste por unidad"), (view["total"], view["materiales"], view["procesos"], view["unitario"]), (2, 2, 2, 3)):
        col.metric(label, euros(value, digits))
    st.caption("Coste base de producción. Los opcionales se muestran aparte.")
    st.subheader("Desglose de compra")
    left, right = st.columns((3, 1))
    with left:
        group = st.radio("Tipo de partida", ("Todas", "Materiales", "Procesos"), horizontal=True, key="grupo_partidas")
    with right:
        query = st.text_input("Buscar partida", key="buscar_partida", placeholder="Impresión, corte…")
    normalize = lambda value: "".join(c for c in unicodedata.normalize("NFD", value.casefold()) if unicodedata.category(c) != "Mn")
    rows = [r for r in view["filas"] if (group == "Todas" or r["grupo"] == group) and normalize(query.strip()) in normalize(r["concepto"])]
    if rows:
        st.dataframe(tabla_costes(rows), hide_index=True, width="stretch")
    else:
        st.info("No hay partidas que coincidan con los filtros.")
    st.caption("Los filtros solo afectan al listado. Los totales corresponden a la tirada completa, con los descuentos guardados.")
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", project["referencia"])[:100] or "Escandallo"
    st.download_button("Descargar informe CSV completo", crear_csv(project, view), f"{filename}_{quantity}_COMPRAS.csv", "text/csv", key="descargar_csv", type="primary")
    st.subheader("Opcionales · a parte")
    for col, optional in zip(st.columns(2), view["opcionales"]):
        col.metric(optional["concepto"], euros(optional["total"]))
    st.caption("Costes internos guardados de rellenado y armado. No están incluidos en el coste base. Total opcionales: " + euros(view["opcionales_total"]))
    mostrar_detalles(project, view)
    st.subheader("Comparación de cantidades")
    comparison = []
    for q in values:
        other = vista_cantidad(project, q)
        comparison.append({"Cantidad": entero(q) + (" · seleccionada" if q == quantity else ""), "Materiales": euros(other["materiales"]), "Procesos": euros(other["procesos"]), "Coste total": euros(other["total"]), "€/unidad": euros(other["unitario"], 3), "Opcionales aparte": euros(other["opcionales_total"])})
    st.dataframe(comparison, hide_index=True, width="stretch")
    if view["pendientes"]:
        st.subheader("Información pendiente de compra")
        for pending in view["pendientes"]:
            st.info(pending)
    st.divider()
    st.caption("MAINSA · Compras V1 · Consulta interna de costes. Un desglose guardado no permite verificar si el proyecto se recalculó antes de exportarlo.")


# El ejemplo ficticio se incluye en el mismo archivo para funcionar sin recursos adicionales.
DEMO_DATA = json.loads('{"brf": "DEMO-001", "version": "A", "comercial_1": "", "comercial_2": "", "cli": "Proyecto de demostración", "desc": "Expositor de sobremesa", "notas": "Datos ficticios calculados con el motor MAINSA V45.", "_schema": {"app": "MAINSA ADMIN V45", "piezas_index_base": 1}, "cants_str": "100,250,500", "manip": {"unidad_t": "Segundos", "t_input": 45.0, "rellenado": {"enabled": true, "t_input": 10.0}, "armado": {"enabled": true, "t_input": 30.0}}, "params": {"dif_ud": 0.05, "dif_preset_sel": "0,050", "repeticion_proyecto": false, "imp_fijo_pvp": 250.0, "margen": 2.2, "descuento_procesos": 0.0, "margen_extras": 1.4, "margen_embalajes": 1.4}, "db_precios": {"cartoncillo": {"Ninguno": {"precio_kg": 0.0, "gramaje": 0}, "Reverso Gris": {"precio_kg": 0.96, "gramaje": 220}, "Zenith": {"precio_kg": 1.55, "gramaje": 350}, "Reverso Madera": {"precio_kg": 0.975, "gramaje": 400}, "Folding Kraft": {"precio_kg": 1.9, "gramaje": 340}, "Folding Blanco": {"precio_kg": 1.82, "gramaje": 350}}, "planchas": {"Ninguna": {"C/C": 0.0, "B/C": 0.0, "B/B": 0.0, "B/B TEST": 0.0, "peg": 0.0}, "Canal 3 / Micro": {"Cuero/Cuero SQ": 0.768, "Blanco 1 cara SQ": 0.783, "Blanco 2 caras SQ": 0.889, "peg": 0.2353}, "Doble Micro": {"Cuero/Cuero SQ": 1.22, "Blanco 1 cara SQ": 1.241, "Blanco 2 caras SQ": 1.488, "Test blanco 2 caras": 1.441, "Kraft blanco/Kraft": 1.421, "Kraft blanco/Kraft SQ": 1.603, "Estucada ET160-F095-F095-F095-BB115": 1.339, "peg": 0.2726}, "Doble Doble": {"Cuero/Cuero SQ": 1.22, "Blanco 1 cara SQ": 1.283, "peg": 0.2726}, "Canal 5": {"Test blanco 2 caras SQ": 1.121, "peg": 0.2353}, "Especial - Plancha AC": {"Plancha AC": 2.922, "peg": 0.2353}, "Especial - Micro estucada": {"ET160-M095-BB125": 1.013, "peg": 0.2353}, "Microcanal / Canal 3": {"C/C": 0.702, "B/C": 0.725, "B/B": 0.805, "B/B TEST": 1.038, "peg": 0.2353}, "Doble Micro / Doble Doble": {"C/C": 1.128, "B/C": 1.187, "B/B": 1.378, "B/B TEST": 1.334, "peg": 0.2726}, "AC (Cuero/Cuero)": {"C/C": 2.505, "peg": 0.2353}}, "rigidos": {"Ninguno": {"precio_ud": 0.0, "w": 0, "h": 0}, "PVC TRANSPARENTE 300 MICRAS": {"precio_ud": 1.8, "w": 1000, "h": 700}, "PVC TRANSPARENTE 500 MICRAS": {"precio_ud": 2.99, "w": 1000, "h": 700}, "PVC TRANSPARENTE 700 MICRAS": {"precio_ud": 4.22, "w": 1000, "h": 700}, "PVC BLANCO MATE 300 MICRAS": {"precio_ud": 1.76, "w": 1000, "h": 700}, "PVC BLANCO MATE 500 MICRAS": {"precio_ud": 2.94, "w": 1000, "h": 700}, "PVC BLANCO MATE 700 MICRAS": {"precio_ud": 4.11, "w": 1000, "h": 700}, "APET 300 MICRAS": {"precio_ud": 1.35, "w": 1000, "h": 700}, "APET 500 MICRAS": {"precio_ud": 2.25, "w": 1000, "h": 700}, "PET G 0,5mm": {"precio_ud": 8.87, "w": 1250, "h": 2050}, "PET G 0,7mm": {"precio_ud": 11.22, "w": 1250, "h": 2050}, "PET G 1mm": {"precio_ud": 13.61, "w": 1250, "h": 2050}, "POLIPROPILENO COMPACTO BLANCO/ NATURAL 300 MICRAS": {"precio_ud": 1.0, "w": 1000, "h": 700}, "POLIPROPILENO COMPACTO BLANCO/ NATURAL 500 MICRAS": {"precio_ud": 1.67, "w": 1000, "h": 700}, "POLIPROPILENO COMPACTO BLANCO/ NATURAL 800 MICRAS": {"precio_ud": 2.67, "w": 1000, "h": 700}, "COMPACTO 1,5 MM": {"precio_ud": 1.8, "w": 1050, "h": 750}, "COMPACTO 2 MM": {"precio_ud": 2.15, "w": 1050, "h": 750}, "COMPACTO 3 MM": {"precio_ud": 3.0, "w": 1050, "h": 750}, "POLIPROPILENO CELULAR 3,5 MM": {"precio_ud": 15.0, "w": 3050, "h": 2050}}, "peliculado": {"Sin Peliculado": 0.0, "Polipropileno": 0.2709, "Poliéster brillo": 0.53, "Poliéster mate": 0.79}, "laminado_digital": 3.5, "extras_base": {"CINTA D/CARA": 0.26, "CINTA LOHMAN": 0.49, "CINTA GEL": 1.2, "GOMA TERMINALES": 0.079, "IMAN 20x2mm": 1.145, "TUBOS": 1.06, "REMACHES": 0.049, "VELCRO": 0.43, "PUNTO ADHESIVO": 0.08, "Soporte Balda Blanco": 0.08, "Soporte Balda Negro": 0.1, "PUNTO ADHESIVO REDONDO 30mm GEL": 0.085}, "troquelado": {"Pequeño (< 1000x700)": {"arranque": 50.12, "tiro": 0.0624}, "Mediano (Estándar)": {"arranque": 84.0, "tiro": 0.0936}, "Grande (> 1000x700)": {"arranque": 112.01, "tiro": 0.1398}}, "stamping": {"arreglo": 176.4, "pisada": 0.2117, "pelicula_m2": 0.4095}, "flexografia": {"arreglo": 180.0}, "plotter": {"precio_hoja": 2.03}, "narba": {"contracolado_a_mano_m2": 0.6864, "peliculado_menor_50x70_hoja": 0.0572, "guillotina_impresion_corte": 0.0175, "guillotina_plancha_corte": 0.1398}}, "db_descuentos": {"cartoncillo": 5.0, "ondulado_rigidos": 7.0, "narba": 3.0}, "piezas": {"1": {"nombre": "Cuerpo principal", "pliegos": 1.0, "w": 700, "h": 1000, "pf": "Zenith", "gf": 350, "pd": "Ninguno", "gd": 0, "tipo_base": "Ondulado/Cartón", "pl": "Doble Micro", "ap": "Blanco 1 cara SQ", "pl_dif": false, "pl_h": 1000, "pl_w": 700, "mat_rigido": "Ninguno", "rig_manual": false, "rig_w": 0, "rig_h": 0, "rig_precio_ud": 0.0, "im": "Offset", "nt": 4, "ba": false, "im_d": "No", "nt_d": 0, "ba_d": false, "pel": "Polipropileno", "pel_d": "Sin Peliculado", "ld": false, "ld_d": false, "fr24": false, "fr24_rate": 0.05, "cor_default": "Troquelado", "cor_by_qty": {"100": "Troquelado", "250": "Troquelado", "500": "Troquelado"}, "cobrar_arreglo": true, "pv_troquel": 225.0, "troquel_piezas": 0, "stamping": false, "stamping_w": 0, "stamping_h": 0, "stamping_cobrar_arreglo": true, "flexografia": false, "contracolado_a_mano": false}, "2": {"nombre": "Bandeja interior", "pliegos": 1.0, "w": 600, "h": 800, "pf": "Ninguno", "gf": 0, "pd": "Ninguno", "gd": 0, "tipo_base": "Ondulado/Cartón", "pl": "Canal 3 / Micro", "ap": "Cuero/Cuero SQ", "pl_dif": false, "pl_h": 0, "pl_w": 0, "mat_rigido": "Ninguno", "rig_manual": false, "rig_w": 0, "rig_h": 0, "rig_precio_ud": 0.0, "im": "No", "nt": 0, "ba": false, "im_d": "No", "nt_d": 0, "ba_d": false, "pel": "Sin Peliculado", "pel_d": "Sin Peliculado", "ld": false, "ld_d": false, "fr24": false, "fr24_rate": 0.05, "cor_default": "Troquelado", "cor_by_qty": {}, "cobrar_arreglo": true, "pv_troquel": 150.0, "troquel_piezas": 0, "stamping": false, "stamping_w": 0, "stamping_h": 0, "stamping_cobrar_arreglo": true, "flexografia": false, "contracolado_a_mano": false}, "3": {"nombre": "Cartela superior", "pliegos": 1.0, "w": 500, "h": 700, "pf": "Ninguno", "gf": 0, "pd": "Ninguno", "gd": 0, "tipo_base": "Material Rígido", "pl": "Ninguna", "ap": "B/C", "pl_dif": false, "pl_h": 0, "pl_w": 0, "mat_rigido": "COMPACTO 2 MM", "rig_manual": false, "rig_w": 0, "rig_h": 0, "rig_precio_ud": 0.0, "im": "Digital", "nt": 0, "ba": false, "im_d": "No", "nt_d": 0, "ba_d": false, "pel": "Sin Peliculado", "pel_d": "Sin Peliculado", "ld": true, "ld_d": false, "fr24": false, "fr24_rate": 0.05, "cor_default": "Plotter", "cor_by_qty": {}, "cobrar_arreglo": true, "pv_troquel": 0.0, "troquel_piezas": 0, "stamping": true, "stamping_w": 100, "stamping_h": 60, "stamping_cobrar_arreglo": true, "flexografia": false, "contracolado_a_mano": false}}, "extras": [{"nombre": "Cinta doble cara", "coste": 0.26, "cantidad": 2.0}, {"nombre": "Soporte de balda", "coste": 0.08, "cantidad": 4.0}], "embalajes": [{"id": "emb_0", "nombre": "Caja individual", "tipo": "Embalaje en Plano", "material": "Canal 5", "dims": {"L": 400.0, "W": 300.0, "H": 150.0}, "uds_por_caja": 1, "costes": {"100": 2.0725999999999996, "250": 1.121, "500": 0.8037999999999998}}], "externos": [{"id": "ext_0", "concepto": "Preparación de kits", "modo": "Unitario (€/ud)", "costes": {"100": 0.3, "250": 0.25, "500": 0.2}}], "mermas_imp": {"1": {"100": {"cara": 100, "dorso": 0}, "250": {"cara": 100, "dorso": 0}, "500": {"cara": 100, "dorso": 0}}, "2": {"100": {"cara": 0, "dorso": 0}, "250": {"cara": 0, "dorso": 0}, "500": {"cara": 0, "dorso": 0}}, "3": {"100": {"cara": 0, "dorso": 0}, "250": {"cara": 0, "dorso": 0}, "500": {"cara": 0, "dorso": 0}}}, "mermas_imp_digital": {"100": 10, "250": 10, "500": 10}, "mermas_proc": {"1": {"100": 30, "250": 40, "500": 40}, "2": {"100": 30, "250": 40, "500": 40}, "3": {"100": 30, "250": 40, "500": 40}}, "impresiones_by_qty": {}, "impresiones_by_qty_fmt": {}, "impresiones_by_qty_fmt_enabled": {"1": false}, "compras_legible": {"100": {"Cantidad": 100, "Materiales": {"cartoncillo": 82.97537499999999, "ondulado": 149.594406, "rigidos": 133.9665, "extras": 84.0, "embalajes_compra": 207.25999999999996}, "Procesos": {"contracolado": 24.062402, "impresion": 590.25, "peliculado": 158.662343, "corte": 413.668, "stamping": 204.24041, "manipulacion": 22.5, "dificultad": 5.0, "externos": 30.0}, "Detalle piezas": [{"Pieza": "Cuerpo principal", "Cartoncillo Cara": 82.97537499999999, "Cartoncillo Dorso": 0.0, "Plancha Ondulado": 105.02583, "Material Rígido": 0.0, "Contracolado": 24.062402, "Contracolado a mano": false, "Impresión": 340.0, "Peliculado": 23.912342999999996, "Corte (Troquel/Plotter)": 93.28296, "Stamping": 0.0, "Subtotal Pieza": 669.2589099999999, "Corte Seleccionado": "Troquelado"}, {"Pieza": "Bandeja interior", "Cartoncillo Cara": 0.0, "Cartoncillo Dorso": 0.0, "Plancha Ondulado": 44.568576, "Material Rígido": 0.0, "Contracolado": 0.0, "Contracolado a mano": false, "Impresión": 0.0, "Peliculado": 0.0, "Corte (Troquel/Plotter)": 56.48504, "Stamping": 0.0, "Subtotal Pieza": 101.053616, "Corte Seleccionado": "Troquelado"}, {"Pieza": "Cartela superior", "Cartoncillo Cara": 0.0, "Cartoncillo Dorso": 0.0, "Plancha Ondulado": 0.0, "Material Rígido": 133.9665, "Contracolado": 0.0, "Contracolado a mano": false, "Impresión": 250.25, "Peliculado": 134.75, "Corte (Troquel/Plotter)": 263.9, "Stamping": 204.24041, "Subtotal Pieza": 987.10691, "Corte Seleccionado": "Plotter"}], "Detalle embalajes": [{"nombre": "Caja individual", "tipo": "Embalaje en Plano", "material": "Canal 5", "uds_por_caja": 1, "cajas": 100, "coste_caja_compra": 2.0725999999999996, "coste_total_compra": 207.25999999999996, "coste_unit_compra": 2.0725999999999996}], "Detalle externos": [{"concepto": "Preparación de kits", "modo": "Unitario (€/ud)", "tipo_aplicado": "unitario", "valor_input": 0.3, "coste_total": 30.0}], "Extras (detalle)": [{"nombre": "Cinta doble cara", "coste": 0.26, "cantidad": 2.0}, {"nombre": "Soporte de balda", "coste": 0.08, "cantidad": 4.0}], "Opcionales (a parte)": {"rellenado_total": 11.0, "armado_total": 33.0, "rellenado_unit": 0.11, "armado_unit": 0.33, "rellenado_total_coste": 5.0, "armado_total_coste": 15.0, "rellenado_unit_coste": 0.05, "armado_unit_coste": 0.15, "margen_aplicado": 2.2}}, "250": {"Cantidad": 250, "Materiales": {"cartoncillo": 140.697375, "ondulado": 333.710598, "rigidos": 295.926, "extras": 210.0, "embalajes_compra": 280.25}, "Procesos": {"contracolado": 53.677665999999995, "impresion": 984.0, "peliculado": 371.842919, "corte": 762.6791999999999, "stamping": 238.50553, "manipulacion": 56.25, "dificultad": 12.5, "externos": 62.5}, "Detalle piezas": [{"Pieza": "Cuerpo principal", "Cartoncillo Cara": 140.697375, "Cartoncillo Dorso": 0.0, "Plancha Ondulado": 234.28839000000002, "Material Rígido": 0.0, "Contracolado": 53.677665999999995, "Contracolado a mano": false, "Impresión": 392.5, "Peliculado": 53.34291899999999, "Corte (Troquel/Plotter)": 107.80968, "Stamping": 0.0, "Subtotal Pieza": 982.3160299999998, "Corte Seleccionado": "Troquelado"}, {"Pieza": "Bandeja interior", "Cartoncillo Cara": 0.0, "Cartoncillo Dorso": 0.0, "Plancha Ondulado": 99.42220799999998, "Material Rígido": 0.0, "Contracolado": 0.0, "Contracolado a mano": false, "Impresión": 0.0, "Peliculado": 0.0, "Corte (Troquel/Plotter)": 66.16952, "Stamping": 0.0, "Subtotal Pieza": 165.591728, "Corte Seleccionado": "Troquelado"}, {"Pieza": "Cartela superior", "Cartoncillo Cara": 0.0, "Cartoncillo Dorso": 0.0, "Plancha Ondulado": 0.0, "Material Rígido": 295.926, "Contracolado": 0.0, "Contracolado a mano": false, "Impresión": 591.5, "Peliculado": 318.5, "Corte (Troquel/Plotter)": 588.6999999999999, "Stamping": 238.50553, "Subtotal Pieza": 2033.1315299999997, "Corte Seleccionado": "Plotter"}], "Detalle embalajes": [{"nombre": "Caja individual", "tipo": "Embalaje en Plano", "material": "Canal 5", "uds_por_caja": 1, "cajas": 250, "coste_caja_compra": 1.121, "coste_total_compra": 280.25, "coste_unit_compra": 1.121}], "Detalle externos": [{"concepto": "Preparación de kits", "modo": "Unitario (€/ud)", "tipo_aplicado": "unitario", "valor_input": 0.25, "coste_total": 62.5}], "Extras (detalle)": [{"nombre": "Cinta doble cara", "coste": 0.26, "cantidad": 2.0}, {"nombre": "Soporte de balda", "coste": 0.08, "cantidad": 4.0}], "Opcionales (a parte)": {"rellenado_total": 27.500000000000004, "armado_total": 82.5, "rellenado_unit": 0.11000000000000001, "armado_unit": 0.33, "rellenado_total_coste": 12.5, "armado_total_coste": 37.5, "rellenado_unit_coste": 0.05, "armado_unit_coste": 0.15, "margen_aplicado": 2.2}}, "500": {"Cantidad": 500, "Materiales": {"cartoncillo": 230.88799999999998, "ondulado": 621.3921479999999, "rigidos": 545.8634999999999, "extras": 420.0, "embalajes_compra": 401.8999999999999}, "Procesos": {"contracolado": 99.951516, "impresion": 1640.25, "peliculado": 724.0781939999999, "corte": 1308.0091999999997, "stamping": 292.04478, "manipulacion": 112.5, "dificultad": 25.0, "externos": 100.0}, "Detalle piezas": [{"Pieza": "Cuerpo principal", "Cartoncillo Cara": 230.88799999999998, "Cartoncillo Dorso": 0.0, "Plancha Ondulado": 436.26113999999995, "Material Rígido": 0.0, "Contracolado": 99.951516, "Contracolado a mano": false, "Impresión": 480.0, "Peliculado": 99.32819399999998, "Corte (Troquel/Plotter)": 130.50768, "Stamping": 0.0, "Subtotal Pieza": 1476.93653, "Corte Seleccionado": "Troquelado"}, {"Pieza": "Bandeja interior", "Cartoncillo Cara": 0.0, "Cartoncillo Dorso": 0.0, "Plancha Ondulado": 185.13100799999998, "Material Rígido": 0.0, "Contracolado": 0.0, "Contracolado a mano": false, "Impresión": 0.0, "Peliculado": 0.0, "Corte (Troquel/Plotter)": 81.30152, "Stamping": 0.0, "Subtotal Pieza": 266.432528, "Corte Seleccionado": "Troquelado"}, {"Pieza": "Cartela superior", "Cartoncillo Cara": 0.0, "Cartoncillo Dorso": 0.0, "Plancha Ondulado": 0.0, "Material Rígido": 545.8634999999999, "Contracolado": 0.0, "Contracolado a mano": false, "Impresión": 1160.25, "Peliculado": 624.75, "Corte (Troquel/Plotter)": 1096.1999999999998, "Stamping": 292.04478, "Subtotal Pieza": 3719.10828, "Corte Seleccionado": "Plotter"}], "Detalle embalajes": [{"nombre": "Caja individual", "tipo": "Embalaje en Plano", "material": "Canal 5", "uds_por_caja": 1, "cajas": 500, "coste_caja_compra": 0.8037999999999998, "coste_total_compra": 401.8999999999999, "coste_unit_compra": 0.8037999999999998}], "Detalle externos": [{"concepto": "Preparación de kits", "modo": "Unitario (€/ud)", "tipo_aplicado": "unitario", "valor_input": 0.2, "coste_total": 100.0}], "Extras (detalle)": [{"nombre": "Cinta doble cara", "coste": 0.26, "cantidad": 2.0}, {"nombre": "Soporte de balda", "coste": 0.08, "cantidad": 4.0}], "Opcionales (a parte)": {"rellenado_total": 55.00000000000001, "armado_total": 165.0, "rellenado_unit": 0.11000000000000001, "armado_unit": 0.33, "rellenado_total_coste": 25.0, "armado_total_coste": 75.0, "rellenado_unit_coste": 0.05, "armado_unit_coste": 0.15, "margen_aplicado": 2.2}}}, "resumen_costes": {"100": {"Cantidad": 100, "materiales": {"cartoncillo": 82.9754, "ondulado": 149.5944, "rigidos": 133.9665, "extras": 84.0, "embalajes_compra": 207.26}, "procesos": {"contracolado": 24.0624, "impresion": 590.25, "peliculado": 158.6623, "corte": 413.668, "stamping": 204.2404, "manipulacion": 22.5, "dificultad": 5.0, "externos": 30.0}, "totales": {"materiales_total": 657.7963, "procesos_total": 1448.3832, "coste_total_compra_estimado": 2106.1794}, "opcionales_a_parte": {"rellenado_total": 11.0, "armado_total": 33.0, "rellenado_unit": 0.11, "armado_unit": 0.33, "rellenado_total_coste": 5.0, "armado_total_coste": 15.0, "rellenado_unit_coste": 0.05, "armado_unit_coste": 0.15, "margen_aplicado": 2.2}, "embalajes_venta_por_opcion": [{"nombre": "Caja individual", "unit": 2.90164, "total": 290.164}]}, "250": {"Cantidad": 250, "materiales": {"cartoncillo": 140.6974, "ondulado": 333.7106, "rigidos": 295.926, "extras": 210.0, "embalajes_compra": 280.25}, "procesos": {"contracolado": 53.6777, "impresion": 984.0, "peliculado": 371.8429, "corte": 762.6792, "stamping": 238.5055, "manipulacion": 56.25, "dificultad": 12.5, "externos": 62.5}, "totales": {"materiales_total": 1260.584, "procesos_total": 2541.9553, "coste_total_compra_estimado": 3802.5393}, "opcionales_a_parte": {"rellenado_total": 27.5, "armado_total": 82.5, "rellenado_unit": 0.11, "armado_unit": 0.33, "rellenado_total_coste": 12.5, "armado_total_coste": 37.5, "rellenado_unit_coste": 0.05, "armado_unit_coste": 0.15, "margen_aplicado": 2.2}, "embalajes_venta_por_opcion": [{"nombre": "Caja individual", "unit": 1.5694, "total": 392.35}]}, "500": {"Cantidad": 500, "materiales": {"cartoncillo": 230.888, "ondulado": 621.3921, "rigidos": 545.8635, "extras": 420.0, "embalajes_compra": 401.9}, "procesos": {"contracolado": 99.9515, "impresion": 1640.25, "peliculado": 724.0782, "corte": 1308.0092, "stamping": 292.0448, "manipulacion": 112.5, "dificultad": 25.0, "externos": 100.0}, "totales": {"materiales_total": 2220.0436, "procesos_total": 4301.8337, "coste_total_compra_estimado": 6521.8773}, "opcionales_a_parte": {"rellenado_total": 55.0, "armado_total": 165.0, "rellenado_unit": 0.11, "armado_unit": 0.33, "rellenado_total_coste": 25.0, "armado_total_coste": 75.0, "rellenado_unit_coste": 0.05, "armado_unit_coste": 0.15, "margen_aplicado": 2.2}, "embalajes_venta_por_opcion": [{"nombre": "Caja individual", "unit": 1.12532, "total": 562.66}]}}}')


if __name__ == "__main__":
    main()
