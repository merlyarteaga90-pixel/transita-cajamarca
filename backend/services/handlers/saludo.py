"""Handler: SALUDO y DESPEDIDA."""

from __future__ import annotations

from backend.services.handlers._helpers import respuesta


def handle_saludo(params: dict) -> dict:
    return respuesta(
        "Saludo",
        "saludo",
        "¡Hola! Soy tu asistente de rutas en Cajamarca. "
        "Puedo buscar rutas, decirte qué combi pasa por un lugar, "
        "darte horarios, frecuencias y tarifas, o contar qué hay cerca de algún sitio. "
        "¿A dónde quieres ir?",
        icono="👋",
    )


def handle_despedida(params: dict) -> dict:
    return respuesta(
        "Despedida",
        "despedida",
        "¡Hasta luego! Si necesitas otra ruta, aquí estaré.",
        icono="👋",
    )
