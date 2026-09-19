"""Handler: LUGARES_CERCANOS. Lista negocios/establecimientos cerca de un lugar.

Si no hay datos curados en la base de datos, consulta a Ollama para generar
una lista general de establecimientos típicos, marcada como no verificada.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from sqlalchemy import text

from backend.services.handlers._helpers import respuesta
from backend.services.ollama_client import get_client, get_model


logger = logging.getLogger(__name__)

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "lugares_cercanos_generator.txt"


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


def _cargar_prompt(lugar: str) -> str:
    template = _PROMPT_PATH.read_text(encoding="utf-8")
    return template.replace("{{LUGAR}}", lugar)


def _parsear_listado_json(contenido: str) -> list[dict]:
    """Extrae un array JSON del texto devuelto por Ollama."""
    contenido = contenido.strip()
    if contenido.startswith("```"):
        contenido = re.sub(r"^```(?:json)?\s*|\s*```$", "", contenido, flags=re.IGNORECASE)
    try:
        data = json.loads(contenido)
    except json.JSONDecodeError as exc:
        # A veces el modelo devuelve texto antes o después del JSON.
        match = re.search(r"\[.*\]", contenido, re.DOTALL)
        if not match:
            raise exc
        data = json.loads(match.group(0))

    if not isinstance(data, list):
        return []

    resultados = []
    for item in data:
        if not isinstance(item, dict):
            continue
        nombre = str(item.get("nombre") or "").strip()
        tipo = str(item.get("tipo") or "").strip()
        if not nombre or not tipo:
            continue
        resultados.append(
            {
                "nombre": nombre,
                "tipo": tipo,
                "direccion": str(item.get("direccion") or "").strip(),
                "fuente": "general",
            }
        )
    return resultados


def _generar_con_ollama(lugar: str) -> list[dict]:
    """Genera establecimientos cercanos usando Ollama."""
    try:
        client = get_client()
        response = client.chat(
            model=get_model(),
            messages=[
                {"role": "system", "content": _cargar_prompt(lugar)},
                {"role": "user", "content": f"¿Qué hay cerca de {lugar} en Cajamarca?"},
            ],
            format="json",
            options={"temperature": 0.2},
        )
        contenido = response["message"]["content"]
        return _parsear_listado_json(contenido)
    except Exception as exc:
        logger.warning("Ollama no pudo generar lugares cercanos: %s", exc)
        return []


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
            listado.append(f"{fila['nombre']} ({fila['tipo']}){direccion}")

        resumen = "\n".join(f"• {item}" for item in listado)

        return respuesta(
            f"Establecimientos cerca de {destino}",
            "lugares_cercanos",
            f"Encontré {len(listado)} establecimientos cerca de '{destino}':\n\n{resumen}",
            resultados=[dict(fila) for fila in filas],
        )

    # Fallback con Ollama cuando no hay datos curados.
    generados = _generar_con_ollama(destino)
    if generados:
        listado = []
        for item in generados:
            direccion = f" ({item['direccion']})" if item.get("direccion") else ""
            listado.append(f"• {item['nombre']} ({item['tipo']}){direccion}")

        return respuesta(
            f"Lugares cercanos a {destino}",
            "lugares_cercanos",
            (
                f"No tengo un listado verificado cerca de '{destino}', "
                f"pero estos son lugares comunes en esa zona de Cajamarca:\n\n"
                + "\n".join(listado)
                + "\n\nℹ️ Información general — puede variar."
            ),
            resultados=generados,
        )

    return respuesta(
        "Sin establecimientos cercanos",
        "sin_resultados",
        f"No tengo registrados establecimientos cerca de '{destino}'.",
    )
