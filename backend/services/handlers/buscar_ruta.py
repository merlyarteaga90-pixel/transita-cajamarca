"""Handler: BUSCAR_RUTA.

Lógica principal: resolver origen y destino, encontrar rutas directas,
fallback a alternativas si no hay ruta directa.
"""

from __future__ import annotations

from backend.services.handlers._helpers import respuesta
from backend.services.reference_service import resolver_referencia
from backend.services.respuesta_service import generar_respuesta
from backend.services.route_engine import buscar_ruta, buscar_rutas_por_lugar
from backend.services.schedule_service import calcular_proxima_unidad


def _rutas_por_ubicaciones(db, ubicaciones: list[dict]) -> list[dict]:
    encontrados = []
    for ubicacion in ubicaciones:
        encontrados.extend(buscar_rutas_por_lugar(db, ubicacion["oficial"]))
    unicos = {}
    for ruta in encontrados:
        clave = (ruta["ruta"], ruta["sentido"])
        unicos.setdefault(clave, ruta)
    return [
        {"codigo_ruta": ruta["ruta"], **{k: v for k, v in ruta.items() if k != "ruta"}}
        for ruta in unicos.values()
    ]


def _nombre_resuelto(referencia: str, resolucion: dict) -> str:
    ubicaciones = resolucion.get("ubicaciones", [])
    return ubicaciones[0]["oficial"] if len(ubicaciones) == 1 else referencia


def _ubicaciones_desde_resolucion(resolucion: dict) -> list[dict]:
    """Extrae ubicaciones oficiales tanto de resoluciones directas como ambiguas."""
    ubicaciones = resolucion.get("ubicaciones", [])
    if ubicaciones:
        return ubicaciones

    sugerencias = resolucion.get("sugerencias", [])
    oficiales = []
    vistas = set()
    for sug in sugerencias:
        oficial = sug.get("ubicacion") or sug.get("nombre")
        if oficial and oficial not in vistas:
            vistas.add(oficial)
            oficiales.append({"oficial": oficial, "normalizada": oficial.lower()})
    return oficiales


def _candidatos_ambiguos(resolucion: dict) -> list[str]:
    candidatos = []
    for sugerencia in resolucion.get("sugerencias", []):
        nombre = sugerencia.get("ubicacion") or sugerencia.get("nombre")
        if nombre and nombre not in candidatos:
            candidatos.append(nombre)
    return candidatos[:5]


def _respuesta_ambigua(referencia: str, rol: str, resolucion: dict) -> dict:
    candidatos = _candidatos_ambiguos(resolucion)
    return respuesta(
        f"{rol.capitalize()} ambiguo",
        "aclaracion",
        f"'{referencia}' puede referirse a varios lugares. Elegí una opción o escribí el nombre completo.",
        candidatos=candidatos,
    )


def _contexto_busqueda(origen=None, destino=None, pendiente=None) -> dict:
    contexto = {"intencion": "BUSCAR_RUTA"}
    if origen:
        contexto["origen"] = origen
    if destino:
        contexto["destino"] = destino
    if pendiente:
        contexto["pendiente"] = pendiente
    return contexto


def handle_buscar_ruta(db, params: dict) -> dict:
    origen = params.get("origen")
    destino = params.get("destino")

    if not origen and not destino:
        return respuesta(
            "Datos incompletos",
            "aclaracion",
            "Indica desde dónde partes y a dónde quieres ir. Por ejemplo: 'de Shudal a Hoyos Rubio'.",
        )

    if not origen:
        resolucion = resolver_referencia(db, destino)
        if resolucion["estado"] == "NO_ENCONTRADO":
            return respuesta(
                "Destino no reconocido",
                "aclaracion",
                f"No reconocí el destino '{destino}'.",
            )
        nombre = _nombre_resuelto(destino, resolucion)
        ubicaciones = _ubicaciones_desde_resolucion(resolucion)
        alternativas = _rutas_por_ubicaciones(db, ubicaciones)
        candidatos = _candidatos_ambiguos(resolucion) if resolucion["estado"] == "AMBIGUO" else []
        if alternativas:
            return respuesta(
                "Falta el origen",
                "alternativas",
                f"Entiendo que quieres ir a {nombre}. Estas rutas pasan por ahí. "
                "Si me dices desde dónde partes, puedo buscar una ruta directa.",
                resultados=alternativas,
                candidatos=candidatos,
                contexto=_contexto_busqueda(destino=nombre, pendiente="origen"),
            )
        return respuesta(
            "Falta el origen",
            "aclaracion",
            f"Entiendo que quieres ir a {nombre}. ¿Desde dónde partes?",
            candidatos=candidatos,
            contexto=_contexto_busqueda(destino=nombre, pendiente="origen"),
        )

    if not destino:
        resolucion = resolver_referencia(db, origen)
        if resolucion["estado"] == "AMBIGUO":
            return _respuesta_ambigua(origen, "origen", resolucion)
        if resolucion["estado"] == "NO_ENCONTRADO":
            return respuesta(
                "Origen no reconocido",
                "aclaracion",
                f"No reconocí el origen '{origen}'.",
            )
        nombre = _nombre_resuelto(origen, resolucion)
        alternativas = _rutas_por_ubicaciones(db, resolucion["ubicaciones"])
        if alternativas:
            return respuesta(
                "Falta el destino",
                "alternativas",
                f"Entiendo que partes de {nombre}. Estas rutas pasan por ahí. "
                "¿A dónde quieres ir para buscar una ruta directa?",
                resultados=alternativas,
                contexto=_contexto_busqueda(origen=nombre, pendiente="destino"),
            )
        return respuesta(
            "Falta el destino",
            "aclaracion",
            f"Entiendo que partes de {nombre}. ¿A dónde quieres ir?",
            contexto=_contexto_busqueda(origen=nombre, pendiente="destino"),
        )

    resolucion_origen = resolver_referencia(db, origen)
    resolucion_destino = resolver_referencia(db, destino)
    if resolucion_origen["estado"] == "AMBIGUO":
        return _respuesta_ambigua(origen, "origen", resolucion_origen)
    if resolucion_destino["estado"] == "AMBIGUO":
        return _respuesta_ambigua(destino, "destino", resolucion_destino)
    if resolucion_origen["estado"] == "NO_ENCONTRADO":
        return respuesta(
            "Origen no reconocido",
            "aclaracion",
            f"No reconocí el origen '{origen}'.",
        )
    if resolucion_destino["estado"] == "NO_ENCONTRADO":
        return respuesta(
            "Destino no reconocido",
            "aclaracion",
            f"No reconocí el destino '{destino}'.",
        )

    encontrados = []
    vistos = set()
    for ubicacion_origen in resolucion_origen["ubicaciones"]:
        for ubicacion_destino in resolucion_destino["ubicaciones"]:
            for ruta in buscar_ruta(
                db, ubicacion_origen["oficial"], ubicacion_destino["oficial"]
            ):
                clave = (ruta["codigo"], ruta["sentido"])
                if clave not in vistos:
                    vistos.add(clave)
                    encontrados.append(ruta)

    if not encontrados:
        nombre_origen = _nombre_resuelto(origen, resolucion_origen)
        nombre_destino = _nombre_resuelto(destino, resolucion_destino)
        alternativas = _rutas_por_ubicaciones(db, resolucion_destino["ubicaciones"])
        if alternativas:
            return respuesta(
                "Sin ruta directa",
                "alternativas",
                f"No encontré una ruta directa desde {nombre_origen} hasta {nombre_destino}. "
                "Estas rutas sí pasan por el destino; con los datos actuales no puedo confirmar "
                "el tramo completo desde tu origen.",
                resultados=alternativas,
                contexto=_contexto_busqueda(origen=nombre_origen, destino=nombre_destino),
            )
        return respuesta(
            "Sin rutas directas",
            "sin_resultados",
            f"No encontré una ruta directa para ir desde {origen} hasta {destino}.",
            contexto=_contexto_busqueda(
                origen=_nombre_resuelto(origen, resolucion_origen),
                destino=_nombre_resuelto(destino, resolucion_destino),
            ),
        )

    resultados = []
    for ruta in encontrados:
        frecuencia = (
            int(ruta["frecuencia_min"]) if ruta.get("frecuencia_min") is not None else None
        )
        calculo = calcular_proxima_unidad(
            ruta.get("horario_inicio"), ruta.get("horario_fin"), frecuencia
        )
        puntos = [
            {
                "nombre": punto.get("nombre", ""),
                "orden": punto.get("orden", indice),
            }
            for indice, punto in enumerate(ruta.get("camino", []))
        ]
        resultados.append(
            {
                "codigo_ruta": ruta["codigo"],
                "sentido": ruta["sentido"],
                "nombre_comercial": ruta.get("nombre_comercial") or ruta.get("razon_social") or "",
                "razon_social": ruta.get("razon_social") or "",
                "ruc": ruta.get("ruc") or "",
                "origen": ruta["origen"].get("nombre", ""),
                "destino": ruta["destino"].get("nombre", ""),
                "distancia_total_ruta_km": round(float(ruta["distancia_km"]), 2)
                if ruta.get("distancia_km") is not None
                else None,
                "tiempo_total_ruta_min": ruta.get("tiempo_total_min"),
                "frecuencia_min": frecuencia,
                "horario": (
                    f"{ruta.get('horario_inicio')} - {ruta.get('horario_fin')}"
                    if ruta.get("horario_inicio") and ruta.get("horario_fin")
                    else None
                ),
                "horario_inicio": ruta.get("horario_inicio") or None,
                "horario_fin": ruta.get("horario_fin") or None,
                "tarifa_general": float(ruta["tarifa_general"])
                if ruta.get("tarifa_general") is not None
                else None,
                "tarifa_medio_pasaje": float(ruta["tarifa_medio_pasaje"])
                if ruta.get("tarifa_medio_pasaje") is not None
                else None,
                "estado_servicio": calculo["estado"],
                "proxima_salida": calculo["proxima_salida"],
                "proximo_paso_min": calculo["minutos_restantes"],
                "mensaje_servicio": calculo["mensaje"],
                "puntos": puntos,
            }
        )

    consulta = params.get("_consulta", "")
    return respuesta(
        f"Rutas directas encontradas: {len(resultados)}",
        "ruta",
        generar_respuesta(consulta, resultados),
        resultados=resultados,
        contexto={},
    )
