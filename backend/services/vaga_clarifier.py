"""Genera preguntas de aclaración para consultas que no se pudieron entender."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from backend.services.ollama_client import get_client, get_model
from backend.services.text_helpers import limpiar_prosa


logger = logging.getLogger(__name__)

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "vaga_clarification.txt"


def _cargar_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def generar_aclaracion_vaga(
    consulta: str,
    slots: dict | None = None,
    contexto: dict | None = None,
) -> str | None:
    """Genera una pregunta específica; devuelve None si Ollama falla."""
    payload = json.dumps(
        {
            "consulta": consulta,
            "slots": slots or {},
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
            options={"temperature": 0.3},
        )
        texto = limpiar_prosa(response["message"]["content"], max_oraciones=2)
        return texto or None
    except Exception as exc:
        logger.warning("Ollama no pudo generar la aclaración: %s", exc)
        return None
