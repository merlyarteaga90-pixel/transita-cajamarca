"""Helpers para limpiar texto generado por Ollama."""

from __future__ import annotations

import re


_PREFIJOS_PROSA = (
    "claro,",
    "claro:",
    "¡claro!",
    "por supuesto,",
    "por supuesto:",
    "aquí tienes:",
    "aquí va:",
    "con gusto,",
)


def limpiar_prosa(texto: str, max_oraciones: int = 5) -> str:
    """Quita formato accidental y limita respuestas excesivamente largas."""
    limpio = (texto or "").strip()
    if not limpio:
        return ""

    if limpio.startswith("```") and limpio.endswith("```"):
        limpio = re.sub(r"^```(?:text|markdown)?\s*|\s*```$", "", limpio, flags=re.IGNORECASE)
        limpio = limpio.strip()

    if len(limpio) >= 2 and limpio[0] == limpio[-1] and limpio[0] in "\"'":
        limpio = limpio[1:-1].strip()

    minusculas = limpio.lower()
    for prefijo in _PREFIJOS_PROSA:
        if minusculas.startswith(prefijo):
            limpio = limpio[len(prefijo):].lstrip()
            break

    oraciones = re.split(r"(?<=[.!?])\s+", limpio)
    if len(oraciones) > max_oraciones:
        limpio = " ".join(oraciones[:max_oraciones]).strip()
    return limpio
