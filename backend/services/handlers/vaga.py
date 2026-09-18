"""Handler: INTENCION_VAGA. Consulta ambigua sin suficiente información."""

from __future__ import annotations

from backend.services.handlers._helpers import respuesta


_RESPUESTAS_POR_PISTA = [
    (
        ["medico", "doctor", "hospital", "clinica", "salud"],
        "Si necesitas atención médica, las opciones más conocidas en Cajamarca son el Hospital Regional "
        "(vía de Evitamiento), EsSalud y la Clínica Limatambo. ¿A cuál quieres ir?",
    ),
    (
        ["aeropuerto", "vuelo"],
        "El Aeropuerto de Cajamarca está en la Av. Hoyos Rubio. Las rutas que llegan cerca son R-05, R-06 y R-12. "
        "¿Quieres que te busque una ruta específica?",
    ),
    (
        ["universidad", "estudiar", "unc", "upn", "upagu"],
        "Hay varias universidades en Cajamarca: UNC, UPAGU, UPN. ¿A cuál quieres ir?",
    ),
    (
        ["centro", "plaza", "plazuela"],
        "El centro de Cajamarca tiene varias referencias: Plaza de Armas, Plazuela Bolognesi, Plazuela Miguel Grau. "
        "¿A cuál vas?",
    ),
    (
        ["banco", "plata", "cajeros"],
        "Los bancos principales están cerca de la Plaza de Armas (BCP, BBVA, Interbank). "
        "¿Vas a alguno en particular?",
    ),
]


def handle_vaga(db, params: dict) -> dict:
    consulta = (params.get("_consulta") or "").lower()
    pista_destino = (params.get("destino") or "").lower()

    texto_busqueda = f"{consulta} {pista_destino}"

    for pistas, mensaje in _RESPUESTAS_POR_PISTA:
        if any(p in texto_busqueda for p in pistas):
            return respuesta(
                "Sugerencia",
                "aclaracion",
                mensaje,
            )

    return respuesta(
        "Necesito más detalles",
        "aclaracion",
        "No estoy seguro de qué necesitas. ¿Puedes indicarme origen y destino? "
        "Por ejemplo: 'cómo voy del mercado central al aeropuerto'.",
    )
