"""Orquestador principal del asistente.

Flujo:
1. Recibe request del frontend.
2. Si tiene intención explícita, la usa.
3. Si no, clasifica la consulta (parser determinista → Ollama).
4. Aplica contexto conversacional (4-5 turnos).
5. Despacha al handler correspondiente.
6. Devuelve respuesta.
"""

from __future__ import annotations

import logging
import re
import uuid

from backend.services import intent_classifier
from backend.services.respuesta_generator import generar_respuesta_natural
from backend.services.handlers import (
    buscar_ruta,
    info_lugar,
    info_ruta,
    lugares_cercanos,
    rutas_por_lugar,
    saludo,
    vaga,
)


logger = logging.getLogger(__name__)


_PATRONES_LUGAR = [
    r"^(?:qu[eé]\s+es\s+|qu[eé]\s+hay\s+en\s+|d[oó]nde\s+(?:queda|es)\s+|informaci[oó]n\s+de\s+|sobre\s+)(.+?)[?.!]*$",
    r"^(?:qu[eé]\s+hay\s+cerca\s+(?:d[ea]l?|de)\s+|cerca\s+de\s+|negocios\s+cerca\s+de\s+|bancos\s+cerca\s+de\s+|restaurantes\s+cerca\s+de\s+)(.+?)[?.!]*$",
]


def _extraer_lugar_del_texto(consulta: str, intencion: str) -> str | None:
    """Fallback determinista: extrae un lugar del texto cuando no hay destino explícito."""
    texto = consulta.strip().rstrip("?.!")
    for patron in _PATRONES_LUGAR:
        match = re.match(patron, texto, re.IGNORECASE)
        if match:
            lugar = match.group(1).strip()
            lugar = re.sub(r"^(?:el|la|los|las|un|una|unos|unas)\s+", "", lugar, flags=re.IGNORECASE)
            return lugar.strip() or None
    return None


def _aplicar_contexto(params: dict, contexto: dict | None) -> dict:
    """Si hay un slot pendiente en el contexto y la consulta no trae ese dato, complétalo."""
    if not contexto:
        return params
    if contexto.get("intencion") != "BUSCAR_RUTA":
        return params

    pendiente = contexto.get("pendiente")
    if pendiente == "origen" and not params.get("origen") and contexto.get("destino"):
        params["origen"] = contexto["destino"]
        params["_pendiente_completado"] = "origen"
    elif pendiente == "destino" and not params.get("destino") and contexto.get("origen"):
        params["destino"] = contexto["origen"]
        params["_pendiente_completado"] = "destino"
    return params


def _dispatch(db, intencion: str, params: dict) -> dict:
    """Despacha al handler correcto."""
    if intencion == "SALUDO":
        return saludo.handle_saludo(params)
    if intencion == "DESPEDIDA":
        return saludo.handle_despedida(params)
    if intencion == "BUSCAR_RUTA":
        return buscar_ruta.handle_buscar_ruta(db, params)
    if intencion == "RUTAS_POR_LUGAR":
        return rutas_por_lugar.handle_rutas_por_lugar(db, params)
    if intencion == "QUE_RUTA_PASA_CERCA":
        return rutas_por_lugar.handle_que_ruta_pasa_cerca(db, params)
    if intencion == "INFO_LUGAR":
        return info_lugar.handle_info_lugar(db, params)
    if intencion == "LUGARES_CERCANOS":
        return lugares_cercanos.handle_lugares_cercanos(db, params)
    if intencion == "INTENCION_VAGA":
        return vaga.handle_vaga(db, params)
    if intencion in ("HORARIO", "FRECUENCIA", "TARIFA", "PROXIMA_UNIDAD"):
        params["_intencion"] = intencion
        return info_ruta.handle_info_ruta(db, params)
    if intencion == "FUERA_DE_ALCANCE":
        return {
            "estado": "Fuera de alcance",
            "icono": "ℹ️",
            "tipo": "aclaracion",
            "resultados": [],
            "respuesta": "Soy un asistente de transporte público de Cajamarca. "
                          "Puedo ayudarte con rutas de bus, lugares y horarios. "
                          "No tengo información sobre otros temas.",
        }

    return {
        "estado": "Consulta no procesada",
        "icono": "⚠️",
        "tipo": "aclaracion",
        "resultados": [],
        "respuesta": "No pude identificar qué información necesitas.",
    }


def _resultado_vacio() -> dict:
    return {
        "estado": "Consulta vacía",
        "icono": "⚠️",
        "tipo": "error",
        "resultados": [],
        "respuesta": "La consulta no puede estar vacía.",
    }


def consultar(db, request) -> dict:
    """Punto de entrada único del asistente.

    `request` es un objeto con: consulta, origen, destino, intencion,
    ruta_codigo, contexto, user_location, session_id.
    """
    consulta = (getattr(request, "consulta", "") or "").strip()
    if not consulta:
        return _resultado_vacio()

    session_id = getattr(request, "session_id", None) or str(uuid.uuid4())
    contexto = getattr(request, "contexto", None)
    user_location = getattr(request, "user_location", None)

    intencion_explicita = getattr(request, "intencion", None)

    entidades_clasificadas = intent_classifier.clasificar_consulta(consulta)

    if intencion_explicita:
        destino = (
            getattr(request, "destino", None)
            or entidades_clasificadas.get("destino")
            or _extraer_lugar_del_texto(consulta, intencion_explicita)
        )
        clasificacion = {
            "intencion": intencion_explicita,
            "origen": getattr(request, "origen", None) or entidades_clasificadas.get("origen"),
            "destino": destino,
            "ruta_codigo": (
                str(getattr(request, "ruta_codigo", None))
                if getattr(request, "ruta_codigo", None) is not None
                else entidades_clasificadas.get("ruta_codigo")
            ),
            "confianza": 1.0,
        }
    else:
        clasificacion = entidades_clasificadas

    params = {
        "_consulta": consulta,
        "_intencion": clasificacion["intencion"],
        "origen": clasificacion.get("origen"),
        "destino": clasificacion.get("destino"),
        "ruta_codigo": clasificacion.get("ruta_codigo"),
        "user_location": user_location,
        "_contexto": contexto or {},
    }

    params = _aplicar_contexto(params, contexto)

    logger.info(
        "Asistente: intencion=%s origen=%s destino=%s ruta=%s",
        params["_intencion"], params.get("origen"), params.get("destino"), params.get("ruta_codigo"),
    )

    respuesta = _dispatch(db, params["_intencion"], params)

    if respuesta.get("tipo") in ("ruta", "alternativas", "rutas_por_lugar") and respuesta.get("resultados"):
        prosa = generar_respuesta_natural(
            consulta=consulta,
            resultados=respuesta["resultados"],
            contexto=respuesta.get("contexto") or contexto,
        )
        if prosa:
            respuesta["respuesta"] = prosa

    respuesta["session_id"] = session_id
    respuesta["intencion_solicitada"] = params["_intencion"]
    return respuesta
