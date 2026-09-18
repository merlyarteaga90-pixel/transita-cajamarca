"""Handler: INFO_LUGAR. Devuelve descripción de un lugar desde lugares_info."""

from __future__ import annotations

from sqlalchemy import text

from backend.services.handlers._helpers import respuesta
from backend.services.route_engine import normalizar
from backend.services.reference_service import resolver_referencia


def handle_info_lugar(db, params: dict) -> dict:
    destino = params.get("destino") or params.get("lugar")
    if not destino:
        return respuesta(
            "Lugar no especificado",
            "aclaracion",
            "Indica sobre qué lugar quieres saber. Por ejemplo: 'qué es la catedral'.",
        )

    destino_n = normalizar(destino)

    fila = db.execute(
        text(
            """
            SELECT nombre_oficial, descripcion, tipo, categoria
            FROM lugares_info
            WHERE activo = TRUE AND (
                LOWER(nombre_oficial) LIKE :like
                OR :destino_n IN (SELECT LOWER(ubicacion_oficial) FROM lugares_alias WHERE activo = TRUE)
            )
            LIMIT 5
            """
        ),
        {"like": f"%{destino.lower()}%", "destino_n": destino_n},
    ).mappings().all()

    if not fila:
        resolucion = resolver_referencia(db, destino)
        if resolucion["estado"] in ("ALIAS_EXACTO", "PUNTO_EXACTO"):
            oficial = resolucion["ubicaciones"][0]["oficial"]
            fila = db.execute(
                text(
                    "SELECT nombre_oficial, descripcion, tipo, categoria "
                    "FROM lugares_info WHERE activo = TRUE AND LOWER(nombre_oficial) = LOWER(:oficial)"
                ),
                {"oficial": oficial},
            ).mappings().all()

    if not fila:
        return respuesta(
            "Sin información",
            "sin_resultados",
            f"No tengo información descriptiva sobre '{destino}'.",
        )

    principal = fila[0]
    descripcion = principal["descripcion"]
    tipo = principal.get("tipo") or ""
    categoria = principal.get("categoria") or ""

    texto = descripcion
    if tipo and categoria:
        texto = f"{descripcion} (Tipo: {tipo}, categoría: {categoria})"

    return respuesta(
        f"Información de {principal['nombre_oficial']}",
        "info_lugar",
        texto,
        resultados=[
            {
                "nombre_oficial": principal["nombre_oficial"],
                "descripcion": descripcion,
                "tipo": tipo,
                "categoria": categoria,
            }
        ],
    )
