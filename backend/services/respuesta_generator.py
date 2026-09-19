"""Genera prosa natural a partir de resultados ya verificados por SQL."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from backend.services.ollama_client import get_client, get_model
from backend.services.text_helpers import limpiar_prosa


logger = logging.getLogger(__name__)

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "respuesta_generator.txt"


def _cargar_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def generar_respuesta_natural(
    consulta: str,
    resultados: list[dict],
    contexto: dict | None = None,
) -> str | None:
    """Genera un resumen natural; devuelve None si Ollama no está disponible."""
    if not resultados:
        return None

    payload = json.dumps(
        {
            "consulta": consulta,
            "resultados": resultados[:5],
            "contexto": contexto or {},
        },
        ensure_ascii=False,
        default=str,
    )

    try:
        response = get_client().chat(
            model=get_model(),
            messages=[
                {"role": "system", "content": _cargar_prompt()},
                {"role": "user", "content": payload},
            ],
            options={"temperature": 0.2},
        )
        texto = limpiar_prosa(response["message"]["content"])
        return texto or None
    except Exception as exc:
        logger.warning("Ollama no pudo generar la respuesta natural: %s", exc)
        return None
