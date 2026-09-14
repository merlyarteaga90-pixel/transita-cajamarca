"""
Servicio de resolución de referencias coloquiales.

Convierte lo que la gente escribe ('shudal', 'baños del inca',
'plaza de armas de baños del inca') en ubicaciones oficiales
registradas en puntos_recorrido.

Orden de resolución:
1. Alias exacto en lugares_alias.
2. Punto exacto en puntos_recorrido.
3. Coincidencia aproximada (alias y puntos) como último recurso.
4. Aclaración cuando hay ambigüedad.
"""

from difflib import SequenceMatcher
import re

from sqlalchemy import text

from backend.services.route_engine import (
    calcular_coincidencia,
    normalizar_referencia,
)


UMBRAL_RESUELTO = 0.90
UMBRAL_CANDIDATO = 0.70
UMBRAL_MISMA_ZONA = 0.85


def _cargar_alias(db):
    consulta = text(
        """
        SELECT referencia_original, referencia_normalizada,
               ubicacion_oficial, ubicacion_normalizada
        FROM lugares_alias
        WHERE activo = TRUE
        """
    )
    return db.execute(consulta).mappings().all()


def _cargar_puntos(db):
    consulta = text(
        """
        SELECT DISTINCT p.nombre_original AS nombre
        FROM puntos_recorrido p
        INNER JOIN sentidos s ON s.id = p.sentido_id
        INNER JOIN rutas r ON r.id = s.ruta_id
        WHERE r.activo = TRUE
        """
    )
    return [fila["nombre"] for fila in db.execute(consulta).mappings().all()]


def resolver_referencia(db, referencia: str):
    """
    Resuelve una referencia y devuelve las ubicaciones oficiales.

    Estados:
    - ALIAS_EXACTO:  la referencia está en el diccionario.
    - PUNTO_EXACTO:  la referencia es un nombre oficial de punto.
    - APROXIMADO:    coincidencia fuerte (errores de escritura).
    - AMBIGUO:       varias opciones posibles, pedir aclaración.
    - NO_ENCONTRADO: sin coincidencias razonables.
    """

    ref_n = normalizar_referencia(referencia)

    if not ref_n:
        return {
            "estado": "NO_ENCONTRADO",
            "referencia": referencia,
            "ubicaciones": [],
            "sugerencias": [],
        }

    alias = _cargar_alias(db)
    ref_sin_articulo = re.sub(r"^(?:el|la|los|las)\s+", "", ref_n)
    referencias_exactas = {ref_n, ref_sin_articulo}

    # ----------------------------------------------------------
    # 1. Alias exacto (puede tener varios destinos, ej: baños del inca)
    # ----------------------------------------------------------

    ubicaciones = []
    for fila in alias:
        if fila["referencia_normalizada"] in referencias_exactas:
            ubicaciones.append({
                "oficial": fila["ubicacion_oficial"],
                "normalizada": fila["ubicacion_normalizada"],
            })

    if ubicaciones:
        return {
            "estado": "ALIAS_EXACTO",
            "referencia": referencia,
            "ubicaciones": ubicaciones,
            "sugerencias": [],
        }

    # ----------------------------------------------------------
    # 2. Punto exacto en la base
    # ----------------------------------------------------------

    puntos = _cargar_puntos(db)

    exactos = []
    for punto in puntos:
        if normalizar_referencia(punto) in referencias_exactas:
            exactos.append({
                "oficial": punto,
                "normalizada": ref_n,
            })

    if exactos:
        return {
            "estado": "PUNTO_EXACTO",
            "referencia": referencia,
            "ubicaciones": exactos,
            "sugerencias": [],
        }

    # ----------------------------------------------------------
    # 3. Coincidencia aproximada contra alias y puntos
    # ----------------------------------------------------------

    candidatos = []

    for fila in alias:
        puntaje = calcular_coincidencia(fila["referencia_original"], ref_sin_articulo)
        if puntaje >= UMBRAL_CANDIDATO:
            candidatos.append({
                "puntaje": puntaje,
                "mostrar": fila["referencia_original"],
                "ubicacion": fila["ubicacion_oficial"],
            })

    for punto in puntos:
        puntaje = calcular_coincidencia(punto, ref_sin_articulo)
        if puntaje >= UMBRAL_CANDIDATO:
            candidatos.append({
                "puntaje": puntaje,
                "mostrar": punto,
                "ubicacion": punto,
            })

    candidatos.sort(key=lambda c: c["puntaje"], reverse=True)

    if not candidatos:
        return {
            "estado": "NO_ENCONTRADO",
            "referencia": referencia,
            "ubicaciones": [],
            "sugerencias": [],
        }

    mejor = candidatos[0]["puntaje"]

    if mejor >= UMBRAL_RESUELTO:
        fuertes = [c for c in candidatos if c["puntaje"] >= UMBRAL_RESUELTO]

        ubicaciones = []
        vistos = set()
        for c in fuertes:
            clave = normalizar_referencia(c["ubicacion"])
            if clave not in vistos:
                vistos.add(clave)
                ubicaciones.append({
                    "oficial": c["ubicacion"],
                    "normalizada": clave,
                })

        if len(ubicaciones) == 1:
            return {
                "estado": "APROXIMADO",
                "referencia": referencia,
                "ubicaciones": ubicaciones,
                "sugerencias": [],
            }

        # Varias ubicaciones con coincidencia fuerte:
        # si son casi el mismo lugar (misma vía con variantes de nombre)
        # se resuelven todas y la búsqueda combina resultados.
        todas_similares = True
        for i in range(len(ubicaciones)):
            for j in range(i + 1, len(ubicaciones)):
                sim = SequenceMatcher(
                    None,
                    ubicaciones[i]["normalizada"],
                    ubicaciones[j]["normalizada"],
                ).ratio()
                if sim < UMBRAL_MISMA_ZONA:
                    todas_similares = False
                    break
            if not todas_similares:
                break

        if todas_similares:
            return {
                "estado": "APROXIMADO",
                "referencia": referencia,
                "ubicaciones": ubicaciones,
                "sugerencias": [],
            }

        # Lugares realmente distintos: pedir aclaración.
        return {
            "estado": "AMBIGUO",
            "referencia": referencia,
            "ubicaciones": [],
            "sugerencias": [{
                "nombre": c["mostrar"],
                "ubicacion": c["ubicacion"],
            } for c in fuertes[:5]],
        }

    # ----------------------------------------------------------
    # 4. Coincidencias débiles: pedir aclaración
    # ----------------------------------------------------------

    return {
        "estado": "AMBIGUO",
        "referencia": referencia,
        "ubicaciones": [],
        "sugerencias": [{
            "nombre": c["mostrar"],
            "ubicacion": c["ubicacion"],
        } for c in candidatos[:5]],
    }
