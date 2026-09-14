import re
import unicodedata
from datetime import time as dt_time
from difflib import SequenceMatcher

from sqlalchemy import text


def fmt_hora(val) -> str:
    if val is None:
        return ""
    if isinstance(val, dt_time):
        return val.strftime("%H:%M")
    s = str(val)
    if ":" in s:
        parts = s.split(":")
        return f"{int(parts[0]):02d}:{int(parts[1]):02d}"
    return s[:5]


def quitar_tildes(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto)
    return "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )


def normalizar(texto: str) -> str:
    if not texto:
        return ""

    texto = str(texto).lower().strip()
    texto = quitar_tildes(texto)

    for ch in [".", ",", "-"]:
        texto = texto.replace(ch, " ")

    reemplazos = {
        "jiron": "jr", "jr": "jr",
        "avenida": "av", "avda": "av", "av": "av",
        "prolongacion": "prol", "prol": "prol",
        "pasaje": "psje", "psj": "psje", "psje": "psje",
        "calle": "cl", "cl": "cl",
    }

    palabras = texto.split()
    palabras = [reemplazos.get(p, p) for p in palabras]
    texto = " ".join(palabras)

    texto = re.sub(r"\bcuadra\b.*$", "", texto)
    texto = re.sub(r"\bcdra\b.*$", "", texto)
    texto = re.sub(r"\bc p\b", "cp", texto)
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def normalizar_referencia(texto: str) -> str:
    """
    Normaliza una referencia de lugar conservando las cuadras.

    A diferencia de normalizar(), NO elimina 'cuadra' ni 'cdra',
    para que 'av peru' y 'av peru cuadra 10' sigan siendo distintos.
    """
    if not texto:
        return ""

    texto = str(texto).lower().strip()
    texto = quitar_tildes(texto)

    for ch in [".", ",", "-"]:
        texto = texto.replace(ch, " ")

    reemplazos = {
        "jiron": "jr", "jr": "jr",
        "avenida": "av", "avda": "av", "av": "av",
        "prolongacion": "prol", "prol": "prol",
        "pasaje": "psje", "psj": "psje", "psje": "psje",
        "calle": "cl", "cl": "cl",
        "cuadra": "cdra", "cdra": "cdra",
    }

    palabras = texto.split()
    palabras = [reemplazos.get(p, p) for p in palabras]
    texto = " ".join(palabras)

    texto = re.sub(r"\bc p\b", "cp", texto)
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def calcular_coincidencia(nombre_bd: str, nombre_usuario: str) -> float:
    """
    Calcula un puntaje de coincidencia entre 0 y 1.

    Prioridad:
    1. Coincidencia exacta conservando cuadras (1.0)
       'av peru cdra 10' solo coincide 1.0 con 'Av. Perú Cdra 10'.
    2. Coincidencia por contenido o palabras conservando cuadras (0.92 / 0.88)
    3. Coincidencia sin cuadras, para referencias genéricas (0.95 hacia abajo)
    """
    bd_ref = normalizar_referencia(nombre_bd)
    usuario_ref = normalizar_referencia(nombre_usuario)

    if not bd_ref or not usuario_ref:
        return 0.0

    if bd_ref == usuario_ref:
        return 1.0

    if usuario_ref in bd_ref or bd_ref in usuario_ref:
        return 0.92

    palabras_bd = set(bd_ref.split())
    palabras_usuario = set(usuario_ref.split())

    if palabras_usuario and palabras_usuario.issubset(palabras_bd):
        return 0.88
    if palabras_bd and palabras_bd.issubset(palabras_usuario):
        return 0.88

    # Respaldo sin cuadras: 'av peru' debe seguir coincidiendo
    # con 'Av. Perú Cdra 04' cuando el usuario no especifica cuadra.
    bd = normalizar(nombre_bd)
    usuario = normalizar(nombre_usuario)

    if not bd or not usuario:
        return 0.0

    if bd == usuario:
        return 0.86
    if usuario in bd or bd in usuario:
        return 0.84

    palabras_bd = set(bd.split())
    palabras_usuario = set(usuario.split())

    if palabras_usuario and palabras_usuario.issubset(palabras_bd):
        return 0.80
    if palabras_bd and palabras_bd.issubset(palabras_usuario):
        return 0.75

    similitud = SequenceMatcher(None, bd, usuario).ratio()

    if similitud >= 0.90:
        return 0.90
    return similitud


def nombres_coinciden(nombre_bd: str, nombre_usuario: str) -> bool:
    return calcular_coincidencia(nombre_bd, nombre_usuario) >= 0.90


def _mejor_segmento(puntos: list, origen: str, destino: str):
    """Elige el mejor par origen-destino válido, incluso con puntos repetidos."""
    candidatos = []
    for i, punto_origen in enumerate(puntos):
        puntaje_origen = calcular_coincidencia(punto_origen["nombre"], origen)
        if puntaje_origen < 0.90:
            continue
        for j in range(i + 1, len(puntos)):
            puntaje_destino = calcular_coincidencia(puntos[j]["nombre"], destino)
            if puntaje_destino >= 0.90:
                candidatos.append(
                    (puntaje_origen + puntaje_destino, -(j - i), i, j)
                )

    if not candidatos:
        return None, None
    _, _, indice_origen, indice_destino = max(candidatos)
    return indice_origen, indice_destino


def buscar_ruta(db, origen: str, destino: str):
    origen_n = normalizar(origen)
    destino_n = normalizar(destino)

    if not origen_n or not destino_n:
        return []

    consulta = text(
        """
        SELECT
            r.id AS ruta_id,
            r.codigo,
            r.nombre AS ruta_nombre,
            r.tarifa_general,
            r.tarifa_medio_pasaje,
            r.frecuencia_general_min,
            r.horario_inicio,
            r.horario_fin,

            s.id AS sentido_id,
            s.tipo,
            s.origen,
            s.destino,
            s.distancia_km,
            s.tiempo_total_min,

            e.nombre_comercial,
            e.razon_social,
            e.ruc,

            p.id AS punto_id,
            p.orden,
            p.nombre_original AS nombre,
            p.cuadra,
            p.distrito

        FROM rutas r

        INNER JOIN sentidos s
            ON s.ruta_id = r.id

        INNER JOIN puntos_recorrido p
            ON p.sentido_id = s.id

        LEFT JOIN empresas e
            ON e.id = r.empresa_id

        WHERE r.activo = TRUE

        ORDER BY
            r.id,
            s.id,
            p.orden
        """
    )

    filas = db.execute(consulta).mappings().all()

    recorridos = {}

    for fila in filas:
        clave = (fila["ruta_id"], fila["sentido_id"])

        if clave not in recorridos:
            recorridos[clave] = {
                "ruta_id": fila["ruta_id"],
                "codigo": fila["codigo"],
                "ruta_nombre": fila["ruta_nombre"],
                "tarifa_general": fila["tarifa_general"],
                "tarifa_medio_pasaje": fila["tarifa_medio_pasaje"],
                "frecuencia_min": fila["frecuencia_general_min"],
                "horario_inicio": fmt_hora(fila["horario_inicio"]),
                "horario_fin": fmt_hora(fila["horario_fin"]),
                "sentido_id": fila["sentido_id"],
                "tipo": fila["tipo"],
                "origen": fila["origen"],
                "destino": fila["destino"],
                "distancia_km": fila["distancia_km"],
                "tiempo_total_min": fila["tiempo_total_min"],
                "nombre_comercial": fila["nombre_comercial"],
                "razon_social": fila["razon_social"],
                "ruc": fila["ruc"],
                "puntos": []
            }

        recorridos[clave]["puntos"].append(
            {
                "id": fila["punto_id"],
                "orden": fila["orden"],
                "nombre": fila["nombre"],
                "cuadra": fila["cuadra"],
                "distrito": fila["distrito"]
            }
        )

    resultados = []

    for recorrido in recorridos.values():
        puntos = recorrido["puntos"]

        indice_origen, indice_destino = _mejor_segmento(puntos, origen, destino)

        if indice_origen is None:
            continue

        if indice_destino is None:
            continue

        if indice_destino <= indice_origen:
            continue

        puntos_segmento = puntos[indice_origen:indice_destino + 1]

        # El segmento ya está ordenado: el camino es la secuencia completa.
        camino = puntos_segmento

        resultados.append(
            {
                "ruta_id": recorrido["ruta_id"],
                "codigo": recorrido["codigo"],
                "ruta_nombre": recorrido["ruta_nombre"],
                "sentido": recorrido["tipo"],
                "distancia_km": recorrido["distancia_km"],
                "tiempo_total_min": recorrido["tiempo_total_min"],
                "frecuencia_min": recorrido["frecuencia_min"],
                "horario_inicio": recorrido["horario_inicio"],
                "horario_fin": recorrido["horario_fin"],
                "tarifa_general": recorrido["tarifa_general"],
                "tarifa_medio_pasaje": recorrido["tarifa_medio_pasaje"],
                "nombre_comercial": recorrido["nombre_comercial"],
                "razon_social": recorrido["razon_social"],
                "ruc": recorrido["ruc"],
                "origen": camino[0],
                "destino": camino[-1],
                "puntos_intermedios": camino[1:-1],
                "camino": camino
            }
        )

    return resultados


def obtener_todas_rutas(db):
    consulta = text(
        """
        SELECT DISTINCT
            r.codigo,
            r.nombre AS ruta_nombre,
            r.tarifa_general,
            r.tarifa_medio_pasaje,
            r.frecuencia_general_min,
            r.horario_inicio,
            r.horario_fin,
            e.nombre_comercial,
            e.razon_social,
            e.ruc,
            s.tipo,
            s.origen,
            s.destino,
            s.distancia_km,
            s.tiempo_total_min
        FROM rutas r
        INNER JOIN sentidos s ON s.ruta_id = r.id
        LEFT JOIN empresas e ON e.id = r.empresa_id
        WHERE r.activo = TRUE
        ORDER BY r.codigo, s.tipo
        """
    )
    filas = db.execute(consulta).mappings().all()
    rutas = []
    for fila in filas:
        hi = fmt_hora(fila["horario_inicio"])
        hf = fmt_hora(fila["horario_fin"])
        rutas.append({
            "codigo": fila["codigo"],
            "ruta_nombre": fila["ruta_nombre"],
            "nombre_comercial": fila["nombre_comercial"] or "",
            "razon_social": fila["razon_social"] or "",
            "ruc": fila["ruc"] or "",
            "tipo": fila["tipo"],
            "origen": fila["origen"],
            "destino": fila["destino"],
            "distancia_km": float(fila["distancia_km"]) if fila["distancia_km"] else 0,
            "tiempo_total_min": fila["tiempo_total_min"],
            "frecuencia_min": fila["frecuencia_general_min"],
            "horario_inicio": hi,
            "horario_fin": hf,
            "tarifa_general": float(fila["tarifa_general"]) if fila["tarifa_general"] else 0,
            "tarifa_medio_pasaje": float(fila["tarifa_medio_pasaje"]) if fila["tarifa_medio_pasaje"] else 0,
        })
    return rutas


def buscar_rutas_por_lugar(db, lugar: str):
    lugar_n = normalizar(lugar)

    if not lugar_n:
        return []

    consulta = text(
        """
        SELECT
            r.codigo,
            r.nombre AS ruta_nombre,
            r.tarifa_general,
            r.tarifa_medio_pasaje,
            r.frecuencia_general_min,
            r.horario_inicio,
            r.horario_fin,
            e.nombre_comercial,
            e.razon_social,
            e.ruc,
            s.tipo,
            s.origen,
            s.destino,
            p.orden,
            p.nombre_original AS punto

        FROM rutas r

        INNER JOIN sentidos s
            ON s.ruta_id = r.id

        INNER JOIN puntos_recorrido p
            ON p.sentido_id = s.id

        LEFT JOIN empresas e
            ON e.id = r.empresa_id

        WHERE r.activo = TRUE

        ORDER BY
            r.codigo,
            s.tipo,
            p.orden
        """
    )

    filas = db.execute(consulta).mappings().all()

    resultados = []

    for fila in filas:
        if nombres_coinciden(fila["punto"], lugar):
            resultados.append(
                {
                    "ruta": fila["codigo"],
                    "nombre": fila["ruta_nombre"],
                    "sentido": fila["tipo"],
                    "punto": fila["punto"],
                    "orden": fila["orden"],
                    "nombre_comercial": fila["nombre_comercial"] or "",
                    "razon_social": fila["razon_social"] or "",
                    "ruc": fila["ruc"] or "",
                    "origen": fila["origen"] or "",
                    "destino": fila["destino"] or "",
                    "frecuencia_min": fila["frecuencia_general_min"],
                    "horario_inicio": fmt_hora(fila["horario_inicio"]),
                    "horario_fin": fmt_hora(fila["horario_fin"]),
                    "tarifa_general": float(fila["tarifa_general"]) if fila["tarifa_general"] is not None else None,
                    "tarifa_medio_pasaje": float(fila["tarifa_medio_pasaje"]) if fila["tarifa_medio_pasaje"] is not None else None,
                }
            )

    return resultados
