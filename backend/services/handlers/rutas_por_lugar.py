"""Handler: RUTAS_POR_LUGAR y QUE_RUTA_PASA_CERCA.

Ambas intenciones terminan resolviendo qué rutas pasan por un lugar,
pero la fuente del lugar es diferente:
- RUTAS_POR_LUGAR → lugar explícito del usuario
- QUE_RUTA_PASA_CERCA → lugar inferido por coordenadas del usuario
"""

from __future__ import annotations

from typing import Any
from sqlalchemy import text

from backend.services.handlers._helpers import respuesta
from backend.services.reference_service import resolver_referencia
from backend.services.route_engine import buscar_rutas_por_lugar


def _candidatos_ambiguos(resolucion: dict) -> list[str]:
    candidatos = []
    for sugerencia in resolucion.get("sugerencias", []):
        nombre = sugerencia.get("nombre") or sugerencia.get("ubicacion")
        if nombre and nombre not in candidatos:
            candidatos.append(nombre)
    return candidatos[:5]


def _respuesta_ambigua(referencia: str, rol: str, resolucion: dict) -> dict:
    candidatos = _candidatos_ambiguos(resolucion)
    return respuesta(
        f"{rol.capitalize()} ambiguo",
        "aclaracion",
        f"'{referencia}' puede referirse a varios lugares. Escribe el nombre completo.",
        candidatos=candidatos,
    )


def _resolver_lugar_a_lista(db, lugar: str) -> list[str]:
    """Resuelve una referencia y devuelve lista de nombres oficiales."""
    resolucion = resolver_referencia(db, lugar)
    if resolucion["estado"] in ("ALIAS_EXACTO", "PUNTO_EXACTO", "APROXIMADO"):
        return [u["oficial"] for u in resolucion.get("ubicaciones", []) if u.get("oficial")]
    return []


def _buscar_y_armar(db, lugar: str, etiqueta_origen: str) -> dict:
    if not lugar:
        return respuesta(
            "Lugar no especificado",
            "aclaracion",
            f"Indica el lugar desde donde quieres {etiqueta_origen}.",
        )

    resolucion = resolver_referencia(db, lugar)
    if resolucion["estado"] == "AMBIGUO":
        return _respuesta_ambigua(lugar, "lugar", resolucion)
    if resolucion["estado"] == "NO_ENCONTRADO":
        return respuesta(
            "Lugar no reconocido",
            "aclaracion",
            f"No reconocí el lugar '{lugar}'. Prueba con otro nombre o una referencia cercana.",
        )

    encontrados = []
    for ubicacion in resolucion["ubicaciones"]:
        encontrados.extend(buscar_rutas_por_lugar(db, ubicacion["oficial"]))

    unicos = {}
    for ruta in encontrados:
        clave = (ruta["ruta"], ruta["sentido"])
        unicos.setdefault(clave, ruta)
    resultados = [
        {"codigo_ruta": ruta["ruta"], **{k: v for k, v in ruta.items() if k != "ruta"}}
        for ruta in unicos.values()
    ]

    if not resultados:
        return respuesta(
            "Sin rutas",
            "sin_resultados",
            f"No encontré rutas que pasen por '{lugar}'.",
        )

    opciones = ", ".join(f"{r['codigo_ruta']} ({r['sentido']})" for r in resultados)
    return respuesta(
        f"Rutas por lugar: {len(resultados)}",
        "rutas_por_lugar",
        f"Encontré {len(resultados)} opciones que pasan por '{lugar}': {opciones}.",
        resultados=resultados,
    )


def handle_rutas_por_lugar(db, params: dict) -> dict:
    destino = params.get("destino") or params.get("lugar")
    return _buscar_y_armar(db, destino, "ver rutas")


def handle_que_ruta_pasa_cerca(db, params: dict) -> dict:
    """Si el usuario envió coordenadas, las usamos para buscar puntos cercanos."""
    user_location = params.get("user_location")

    if user_location:
        lat = user_location.get("lat")
        lon = user_location.get("lon")

        fila = db.execute(
            text(
                """
                SELECT nombre_original AS nombre,
                       (6371 * acos(
                           cos(radians(:lat)) * cos(radians(latitud))
                           * cos(radians(longitud) - radians(:lon))
                           + sin(radians(:lat)) * sin(radians(latitud))
                       )) AS distancia_km
                FROM puntos_recorrido
                WHERE latitud IS NOT NULL AND longitud IS NOT NULL
                ORDER BY distancia_km ASC
                LIMIT 1
                """
            ),
            {"lat": lat, "lon": lon},
        ).mappings().first()

        if fila:
            lugar = fila["nombre"]
            return _buscar_y_armar(db, lugar, "ver rutas cercanas")

        return respuesta(
            "Sin ubicación cercana",
            "sin_resultados",
            "No encontré puntos de ruta cerca de tu ubicación actual.",
        )

    destino = params.get("destino") or params.get("lugar")
    return _buscar_y_armar(db, destino, "ver rutas")
