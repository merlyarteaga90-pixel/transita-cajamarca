"""Helpers compartidos por todos los handlers."""

from __future__ import annotations

from datetime import time as dt_time
from typing import Any


def fmt_hora(val: Any) -> str | None:
    if val is None:
        return None
    if isinstance(val, dt_time):
        return val.strftime("%H:%M")
    s = str(val)
    if ":" in s:
        parts = s.split(":")
        return f"{int(parts[0]):02d}:{int(parts[1]):02d}"
    return s[:5]


def respuesta(estado: str, tipo: str, texto: str, **extra) -> dict:
    """Wrapper uniforme para todas las respuestas de los handlers."""
    base = {
        "estado": estado,
        "icono": extra.pop("icono", "🚌"),
        "tipo": tipo,
        "resultados": extra.pop("resultados", []),
        "respuesta": texto,
    }
    base.update(extra)
    return base
