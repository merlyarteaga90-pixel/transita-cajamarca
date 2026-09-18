"""Handler: HORARIO, FRECUENCIA, TARIFA, PROXIMA_UNIDAD.

Todas estas intenciones consultan info de una ruta específica (con código).
"""

from __future__ import annotations

from sqlalchemy import text

from backend.services.handlers._helpers import respuesta, fmt_hora
from backend.services.route_code_service import normalizar_codigo_ruta, resolver_codigos_ruta
from backend.services.schedule_service import calcular_proxima_unidad


_ETIQUETAS = {
    "HORARIO": ("horario", "el horario"),
    "FRECUENCIA": ("frecuencia", "la frecuencia"),
    "TARIFA": ("tarifa", "la tarifa"),
    "PROXIMA_UNIDAD": ("próxima salida teórica", "la próxima salida teórica"),
}


def _fila_ruta(db, codigo: str):
    return db.execute(
        text(
            """
            SELECT r.codigo, r.nombre AS ruta_nombre,
                   r.tarifa_general, r.tarifa_medio_pasaje,
                   r.frecuencia_general_min,
                   r.horario_inicio, r.horario_fin,
                   e.nombre_comercial, e.razon_social, e.ruc
            FROM rutas r
            LEFT JOIN empresas e ON e.id = r.empresa_id
            WHERE r.codigo = :codigo AND r.activo = TRUE
            LIMIT 1
            """
        ),
        {"codigo": codigo},
    ).mappings().first()


def _datos_info_rutas(db, codigos: list[str], intencion: str) -> list[dict]:
    resultados = []
    for codigo in codigos:
        fila = _fila_ruta(db, codigo)
        if not fila:
            continue
        hi = fmt_hora(fila["horario_inicio"]) or None
        hf = fmt_hora(fila["horario_fin"]) or None
        frecuencia = (
            int(fila["frecuencia_general_min"])
            if fila["frecuencia_general_min"] is not None
            else None
        )
        item = {
            "codigo_ruta": fila["codigo"],
            "ruta_nombre": fila["ruta_nombre"],
            "nombre_comercial": fila["nombre_comercial"] or fila["razon_social"] or "",
            "razon_social": fila["razon_social"] or "",
            "ruc": fila["ruc"] or "",
            "horario": f"{hi} - {hf}" if hi and hf else None,
            "horario_inicio": hi,
            "horario_fin": hf,
            "frecuencia_min": frecuencia,
            "tarifa_general": float(fila["tarifa_general"])
            if fila["tarifa_general"] is not None
            else None,
            "tarifa_medio_pasaje": float(fila["tarifa_medio_pasaje"])
            if fila["tarifa_medio_pasaje"] is not None
            else None,
            "consulta_tipo": intencion,
        }
        if intencion == "PROXIMA_UNIDAD":
            calculo = calcular_proxima_unidad(
                fila["horario_inicio"], fila["horario_fin"], frecuencia
            )
            item.update(
                {
                    "estado_servicio": calculo["estado"],
                    "proxima_salida": calculo["proxima_salida"],
                    "proximo_paso_min": calculo["minutos_restantes"],
                    "hora_actual": calculo["hora_actual"],
                    "mensaje_servicio": calculo["mensaje"],
                }
            )
        resultados.append(item)
    return resultados


def handle_info_ruta(db, params: dict) -> dict:
    intencion = params.get("_intencion")
    ruta_codigo = params.get("ruta_codigo")

    if intencion not in _ETIQUETAS:
        return respuesta(
            "Intención no soportada",
            "error",
            "No puedo procesar esta consulta de información de ruta.",
            icono="⚠️",
        )

    etiqueta, descripcion = _ETIQUETAS[intencion]

    if not ruta_codigo:
        return respuesta(
            "Indica una ruta",
            "aclaracion",
            f"Indica el código de la ruta para consultar {descripcion}. "
            f"Por ejemplo: '{descripcion} de la ruta 05'.",
            intencion_solicitada=intencion,
        )

    codigos = resolver_codigos_ruta(db, ruta_codigo)
    if not codigos:
        canonico = normalizar_codigo_ruta(ruta_codigo) or str(ruta_codigo)
        return respuesta(
            "Ruta no encontrada",
            "error",
            f"No encontré la ruta o familia {canonico}.",
            icono="⚠️",
        )

    resultados = _datos_info_rutas(db, codigos, intencion)
    nombres = ", ".join(codigos)
    return respuesta(
        f"{etiqueta.capitalize()}: {len(resultados)} ruta(s)",
        "info",
        f"Encontré información de {etiqueta} para: {nombres}.",
        resultados=resultados,
        intencion_solicitada=intencion,
    )
