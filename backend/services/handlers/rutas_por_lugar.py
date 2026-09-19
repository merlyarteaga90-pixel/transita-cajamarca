"""Handler: RUTAS_POR_LUGAR y QUE_RUTA_PASA_CERCA.

Ambas intenciones terminan resolviendo qué rutas pasan por un lugar,
pero la fuente del lugar es diferente:
- RUTAS_POR_LUGAR → lugar explícito del usuario
- QUE_RUTA_PASA_CERCA → lugar inferido por coordenadas del usuario
"""

from __future__ import annotations

import os
from typing import Any
from sqlalchemy import text

from backend.services.handlers._helpers import respuesta
from backend.services.reference_service import resolver_referencia
from backend.services.route_engine import buscar_rutas_por_lugar


# Radio máximo en km para considerar un punto "cercano"
_MAX_DISTANCIA_KM = float(os.getenv("GEO_MAX_DISTANCIA_KM", "2.0"))


def _candidatos_ambiguos(resolucion: dict) -> list[str]:
    candidatos = []
    for sugerencia in resolucion.get("sugerencias", []):
        nombre = sugerencia.get("ubicacion") or sugerencia.get("nombre")
        if nombre and nombre not in candidatos:
            candidatos.append(nombre)
    return candidatos[:5]


def _respuesta_ambigua(referencia: str, rol: str, resolucion: dict) -> dict:
    candidatos = _candidatos_ambiguos(resolucion)
    return respuesta(
        f"{rol.capitalize()} ambiguo",
        "aclaracion",
        f"'{referencia}' puede referirse a varios lugares. Elegí una opción o escribí el nombre completo.",
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
    """Si el usuario envió coordenadas, busca puntos cercanos dentro de un radio."""
    user_location = params.get("user_location")

    if user_location:
        lat = user_location.get("lat")
        lon = user_location.get("lon")
        accuracy = user_location.get("accuracy_m")

        # Ajustar radio según precisión del GPS (máximo 5km)
        radio = min(_MAX_DISTANCIA_KM + (accuracy / 1000 if accuracy else 0), 5.0)

        filas = db.execute(
            text(
                """
                SELECT
                    r.codigo AS codigo_ruta,
                    s.tipo AS sentido,
                    p.nombre_original AS nombre,
                    (6371 * acos(
                        cos(radians(:lat)) * cos(radians(p.latitud))
                        * cos(radians(p.longitud) - radians(:lon))
                        + sin(radians(:lat)) * sin(radians(p.latitud))
                    )) AS distancia_km
                FROM puntos_recorrido p
                JOIN sentidos s ON s.id = p.sentido_id
                JOIN rutas r ON r.id = s.ruta_id
                WHERE p.latitud IS NOT NULL
                  AND p.longitud IS NOT NULL
                  AND (p.coord_confianza IS NULL OR p.coord_confianza != 'BAJA')
                HAVING distancia_km <= :radio
                ORDER BY distancia_km ASC
                LIMIT 20
                """
            ),
            {"lat": lat, "lon": lon, "radio": radio},
        ).mappings().all()

        if filas:
            # Agrupar por ruta+sentido, tomar la distancia mínima
            agrupado = {}
            for f in filas:
                clave = (f["codigo_ruta"], f["sentido"])
                if clave not in agrupado or f["distancia_km"] < agrupado[clave]["distancia_km"]:
                    agrupado[clave] = dict(f)

            resultados = [
                {
                    "codigo_ruta": v["codigo_ruta"],
                    "sentido": v["sentido"],
                    "distancia_aprox_m": round(v["distancia_km"] * 1000),
                }
                for v in list(agrupado.values())[:10]
            ]

            opciones = ", ".join(
                f"{r['codigo_ruta']} ({r['sentido']})"
                for r in resultados
            )
            return respuesta(
                f"Rutas cercanas: {len(resultados)}",
                "rutas_por_lugar",
                f"Encontré {len(resultados)} rutas con referencias cercanas: {opciones}.",
                resultados=resultados,
            )

        return respuesta(
            "Sin ubicación cercana",
            "sin_resultados",
            "No encontré puntos de ruta verificados cerca de tu ubicación actual.",
        )

    destino = params.get("destino") or params.get("lugar")
    return _buscar_y_armar(db, destino, "ver rutas")
