"""Cliente singleton para Gemini API.

Maneja configuración, timeouts, estadísticas y fallback silencioso
 cuando no hay API key configurada.
"""

from __future__ import annotations

import json
import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_TIMEOUT = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "8"))

# Estadísticas agregadas (no thread-safe, suficiente para MVP)
_stats = {"calls": 0, "tokens_input": 0, "tokens_output": 0, "errors": 0}

_client = None


def _get_client():
    """Lazily importa y construye el cliente de Gemini."""
    global _client
    if _client is not None:
        return _client
    if not GEMINI_API_KEY:
        return None
    try:
        from google import genai
        _client = genai.Client(api_key=GEMINI_API_KEY)
        return _client
    except Exception as exc:
        logger.warning("No se pudo inicializar cliente Gemini: %s", exc)
        return None


def is_configured() -> bool:
    return GEMINI_API_KEY is not None and GEMINI_API_KEY.strip() != ""


def get_stats() -> dict:
    return dict(_stats)


def classify_intent(consulta: str, prompt_sistema: str) -> dict | None:
    """Clasifica intención devolviendo JSON estructurado."""
    client = _get_client()
    if client is None:
        return None

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                {"role": "user", "parts": [{"text": prompt_sistema}]},
                {"role": "user", "parts": [{"text": consulta}]},
            ],
            config={
                "response_mime_type": "application/json",
                "temperature": 0.0,
            },
        )
        _stats["calls"] += 1
        _stats["tokens_input"] += response.usage_metadata.prompt_token_count or 0
        _stats["tokens_output"] += response.usage_metadata.candidates_token_count or 0

        text = response.text
        if not text:
            return None
        data = json.loads(text)
        return data
    except Exception as exc:
        _stats["errors"] += 1
        logger.warning("Gemini falló al clasificar: %s", exc)
        return None


def generate_natural_response(evidencia: dict, temperatura: float = 0.2) -> str | None:
    """Genera prosa natural basada únicamente en evidencia estructurada."""
    client = _get_client()
    if client is None:
        return None

    prompt = (
        "Eres un asistente de transporte público de Cajamarca, Perú. "
        "Responde ÚNICAMENTE con la información proporcionada en la evidencia. "
        "No inventes rutas, paraderos, tiempos ni tarifas. "
        "Usa lenguaje natural y claro. Menciona 'Ruta X' en lugar de 'R-X'.\n\n"
        "Evidencia:\n" + json.dumps(evidencia, ensure_ascii=False, indent=2) + "\n\n"
        "Responde en español de forma concisa y útil."
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            config={"temperature": temperatura},
        )
        _stats["calls"] += 1
        _stats["tokens_input"] += response.usage_metadata.prompt_token_count or 0
        _stats["tokens_output"] += response.usage_metadata.candidates_token_count or 0
        return response.text.strip()
    except Exception as exc:
        _stats["errors"] += 1
        logger.warning("Gemini falló al generar respuesta: %s", exc)
        return None
