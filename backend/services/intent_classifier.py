"""Clasificador de intenciones: Ollama primary con parser determinista como fallback.

Flujo:
1. Parser determinista (rápido, ~ms) — cubre frases frecuentes.
2. Si no se reconoce, Ollama con prompt corto (clasificación JSON).
3. Si Ollama falla o devuelve algo inválido, fallback a INTENCION_VAGA.

Este módulo NO decide qué hacer con la intención — solo clasifica.
El dispatch ocurre en `assistant_service.py`.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from backend.services.ollama_client import get_client, get_model
from backend.services.query_parser import interpretar_consulta_clara


logger = logging.getLogger(__name__)

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "intent_classifier.txt"
_INTENCIONES_VALIDAS = {
    "SALUDO",
    "DESPEDIDA",
    "BUSCAR_RUTA",
    "RUTAS_POR_LUGAR",
    "QUE_RUTA_PASA_CERCA",
    "INFO_LUGAR",
    "LUGARES_CERCANOS",
    "INTENCION_VAGA",
    "PROXIMA_UNIDAD",
    "HORARIO",
    "FRECUENCIA",
    "TARIFA",
    "FUERA_DE_ALCANCE",
}

_intencion_vaga = {
    "intencion": "INTENCION_VAGA",
    "origen": None,
    "destino": None,
    "ruta_codigo": None,
    "confianza": 0.0,
}


def _cargar_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _normalizar_codigo(codigo: str | None) -> str | None:
    """Normaliza '5', 'R05', 'ruta 05' a 'R-5' o 'R-05-1'."""
    if not codigo:
        return None
    codigo = codigo.strip()
    match = re.match(r"^R?[- ]?(\d{1,2})(?:[-./](\d{1,2}))?$", codigo, re.IGNORECASE)
    if not match:
        return codigo
    base, variante = match.groups()
    if variante:
        return f"R-{int(base)}-{int(variante)}"
    return f"R-{int(base)}"


def _normalizar_resultado(resultado: dict) -> dict | None:
    """Valida y normaliza el resultado de Ollama o del parser determinista."""
    intencion = (resultado.get("intencion") or "").upper()
    if intencion not in _INTENCIONES_VALIDAS:
        logger.warning("Intención inválida devuelta: %s", intencion)
        return None

    return {
        "intencion": intencion,
        "origen": (resultado.get("origen") or None),
        "destino": (resultado.get("destino") or None),
        "ruta_codigo": _normalizar_codigo(resultado.get("ruta_codigo")),
        "confianza": float(resultado.get("confianza", 0.0) or 0.0),
    }


def _clasificar_con_ollama(consulta: str) -> dict | None:
    """Llama a Ollama con el prompt corto de clasificación."""
    try:
        client = get_client()
        prompt_sistema = _cargar_prompt()

        response = client.chat(
            model=get_model(),
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": consulta},
            ],
            format="json",
            options={"temperature": 0},
        )

        contenido = response["message"]["content"]
        data = json.loads(contenido)
        return _normalizar_resultado(data)
    except Exception as exc:
        logger.warning("Ollama falló al clasificar: %s", exc)
        return None


def clasificar_consulta(consulta: str) -> dict:
    """Clasifica la consulta del usuario.

    Returns: dict con {intencion, origen, destino, ruta_codigo, confianza}.
    """
    consulta = (consulta or "").strip()
    if not consulta:
        return dict(_intencion_vaga)

    parser_result = interpretar_consulta_clara(consulta)
    if parser_result is not None:
        normalizado = _normalizar_resultado(parser_result)
        if normalizado is not None:
            logger.info("Clasificador determinista: %s", normalizado["intencion"])
            return normalizado

    try:
        ollama_result = _clasificar_con_ollama(consulta)
    except Exception as exc:
        logger.warning("Ollama falló al clasificar (top-level): %s", exc)
        ollama_result = None

    if ollama_result is not None:
        logger.info("Clasificador Ollama: %s (confianza %.2f)", ollama_result["intencion"], ollama_result["confianza"])
        return ollama_result

    logger.info("Clasificador: fallback a INTENCION_VAGA")
    return dict(_intencion_vaga)
