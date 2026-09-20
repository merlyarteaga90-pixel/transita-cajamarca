"""Handler: LUGARES_CERCANOS. Lista negocios/establecimientos cerca de un lugar."""

from __future__ import annotations

from sqlalchemy import text

from backend.services.handlers._helpers import respuesta


def _buscar_en_db(db, destino_lower: str):
    filas = db.execute(
        text(
            """
            SELECT nombre, tipo, direccion
            FROM establecimientos_cercanos
            WHERE activo = TRUE AND LOWER(lugar_referencia) LIKE :like
            ORDER BY tipo, nombre
            """
        ),
        {"like": f"%{destino_lower}%"},
    ).mappings().all()

    if not filas:
        filas = db.execute(
            text(
                """
                SELECT nombre, tipo, direccion
                FROM establecimientos_cercanos
                WHERE activo = TRUE
                AND LOWER(lugar_referencia) IN (
                    SELECT LOWER(ubicacion_oficial) FROM lugares_alias WHERE activo = TRUE
                )
                AND (
                    :destino_lower IN (LOWER(nombre), LOWER(lugar_referencia))
                    OR LOWER(lugar_referencia) LIKE '%' || :destino_lower || '%'
                )
                ORDER BY tipo, nombre
                """
            ),
            {"destino_lower": destino_lower},
        ).mappings().all()

    return filas


def handle_lugares_cercanos(db, params: dict) -> dict:
    destino = params.get("destino") or params.get("lugar")
    if not destino:
        return respuesta(
            "Lugar no especificado",
            "aclaracion",
            "Indica cerca de qué lugar quieres saber. Por ejemplo: 'qué hay cerca del mercado central'.",
        )

    destino_lower = destino.lower()
    filas = _buscar_en_db(db, destino_lower)

    if filas:
        listado = []
        for fila in filas:
            direccion = f" ({fila['direccion']})" if fila.get("direccion") else ""
            listado.append(f"• {fila['nombre']} ({fila['tipo']}){direccion}")

        return respuesta(
            f"Establecimientos cerca de {destino}",
            "lugares_cercanos",
            f"Encontré {len(listado)} establecimientos cerca de '{destino}':\n\n" + "\n".join(listado),
            resultados=[dict(fila) for fila in filas],
        )

    return respuesta(
        "Sin establecimientos cercanos",
        "sin_resultados",
        f"No tengo registrados establecimientos cerca de '{destino}'.",
    )
