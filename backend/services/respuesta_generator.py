"""Genera prosa natural a partir de resultados ya verificados por SQL.

Usa Gemini cuando está configurado; si no, retorna None y se conserva
la respuesta determinista del handler.
"""

from __future__ import annotations

import logging

from backend.services.gemini_client import generate_natural_response, is_configured


logger = logging.getLogger(__name__)


def generar_respuesta_natural(
    consulta: str,
    resultados: list[dict],
    contexto: dict | None = None,
    tipo_respuesta: str | None = None,
    estado: str | None = None,
) -> str | None:
    """Genera un resumen natural; devuelve None si Gemini no está disponible."""
    if not resultados or not is_configured():
        return None

    evidencia = {
        "consulta": consulta,
        "resultados": resultados[:5],
        "contexto": contexto or {},
        "tipo_respuesta": tipo_respuesta,
        "estado": estado,
    }

    try:
        return generate_natural_response(evidencia, temperatura=0.2)
    except Exception as exc:
        logger.warning("Gemini no pudo generar la respuesta natural: %s", exc)
        return None
