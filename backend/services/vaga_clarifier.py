"""Genera preguntas de aclaración deterministas para consultas vagas."""

from __future__ import annotations


def generar_aclaracion_vaga(
    consulta: str,
    slots: dict | None = None,
    contexto: dict | None = None,
) -> str | None:
    """Genera una pregunta corta de aclaración sin llamar a ningún modelo externo."""
    if slots is None:
        slots = {}
    if contexto is None:
        contexto = {}

    origen = slots.get("origen") or contexto.get("origen")
    destino = slots.get("destino") or contexto.get("destino")
    ruta_codigo = slots.get("ruta_codigo")

    if origen and not destino:
        return f"¿A dónde quieres ir desde {origen}?"

    if destino and not origen:
        return f"¿Desde dónde partes para ir a {destino}?"

    if ruta_codigo and not origen and not destino:
        return f"¿Desde dónde y hacia dónde necesitas la {ruta_codigo}?"

    if not origen and not destino:
        return (
            "Indícame desde dónde partes y a dónde quieres ir. "
            "Por ejemplo: 'de Shudal al aeropuerto'."
        )

    return (
        "Cuéntame más detalles sobre tu consulta. "
        "Puedes indicarme origen y destino, o el código de una ruta."
    )
