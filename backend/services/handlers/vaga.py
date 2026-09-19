"""Handler: INTENCION_VAGA. Consulta ambigua sin suficiente información.

Antes devolvía un mensaje de texto; ahora intenta inferir un tema concreto
(médico, aeropuerto, universidad, centro, bancos) y devuelve rutas reales
que pasan por puntos de recorrido relacionados.
"""

from __future__ import annotations

from sqlalchemy import text

from backend.services.handlers._helpers import respuesta
from backend.services.vaga_clarifier import generar_aclaracion_vaga


_PISTAS = [
    {
        "keywords": ["medico", "doctor", "hospital", "clinica", "salud", "seguro"],
        "terminos_sql": ["HOSPITAL", "CLINICA", "SALUD", "CENEPA"],
        "mensaje": "Si necesitas atención médica, encontré rutas que pasan cerca de hospitales/clínicas.",
    },
    {
        "keywords": ["aeropuerto", "vuelo", "avion"],
        "terminos_sql": ["AEROPUERTO", "HOYOS RUBIO", "REVOREDO"],
        "mensaje": "Estas rutas pasan cerca del Aeropuerto de Cajamarca.",
    },
    {
        "keywords": ["universidad", "estudiar", "unc", "upn", "upagu", "la u"],
        "terminos_sql": ["UNIVERSIDAD", "ATAHUALPA", "UNC"],
        "mensaje": "Estas rutas pasan cerca de la UNC y otras universidades.",
    },
    {
        "keywords": ["centro", "plaza", "plazuela", "plaza de armas"],
        "terminos_sql": ["PLAZA", "PLAZUELA", "BOLOGNESI", "AMALIA PUGA"],
        "mensaje": "Estas rutas pasan por el centro de Cajamarca.",
    },
    {
        "keywords": ["banco", "plata", "cajeros", "atm"],
        "terminos_sql": ["PLAZA", "BOLOGNESI", "AMALIA PUGA", "COMERCIO"],
        "mensaje": "Los bancos principales están cerca del centro. Estas rutas pasan por ahí.",
    },
]


def _detectar_pista(consulta: str) -> dict | None:
    texto = consulta.lower()
    for pista in _PISTAS:
        if any(kw in texto for kw in pista["keywords"]):
            return pista
    return None


def _buscar_rutas_por_terminos(db, terminos: list[str]) -> list[dict]:
    """Busca rutas cuyos puntos de recorrido contengan alguno de los términos."""
    filtros = " OR ".join("p.nombre_original LIKE :t{}".format(i) for i in range(len(terminos)))
    params = {f"t{i}": f"%{term}%" for i, term in enumerate(terminos)}

    consulta = text(
        f"""
        SELECT DISTINCT
            r.codigo,
            r.nombre AS ruta_nombre,
            r.tarifa_general,
            r.tarifa_medio_pasaje,
            r.frecuencia_general_min,
            r.horario_inicio,
            r.horario_fin,
            e.nombre_comercial,
            e.razon_social,
            e.ruc,
            s.tipo,
            s.origen,
            s.destino,
            p.nombre_original AS punto
        FROM rutas r
        INNER JOIN sentidos s ON s.ruta_id = r.id
        INNER JOIN puntos_recorrido p ON p.sentido_id = s.id
        LEFT JOIN empresas e ON e.id = r.empresa_id
        WHERE r.activo = TRUE AND ({filtros})
        ORDER BY r.codigo, s.tipo
        """
    )

    filas = db.execute(consulta, params).mappings().all()

    resultados = []
    for fila in filas:
        resultados.append(
            {
                "codigo_ruta": fila["codigo"],
                "nombre": fila["ruta_nombre"],
                "sentido": fila["tipo"],
                "punto": fila["punto"],
                "nombre_comercial": fila["nombre_comercial"] or "",
                "razon_social": fila["razon_social"] or "",
                "ruc": fila["ruc"] or "",
                "origen": fila["origen"] or "",
                "destino": fila["destino"] or "",
                "frecuencia_min": fila["frecuencia_general_min"],
                "horario_inicio": fila["horario_inicio"],
                "horario_fin": fila["horario_fin"],
                "tarifa_general": fila["tarifa_general"],
                "tarifa_medio_pasaje": fila["tarifa_medio_pasaje"],
            }
        )
    return resultados


def handle_vaga(db, params: dict) -> dict:
    consulta = params.get("_consulta") or ""
    pista = _detectar_pista(consulta)

    if pista:
        resultados = _buscar_rutas_por_terminos(db, pista["terminos_sql"])
        if resultados:
            return respuesta(
                "Sugerencia",
                "alternativas",
                pista["mensaje"],
                resultados=resultados,
            )

    slots = {
        nombre: valor
        for nombre in ("origen", "destino", "ruta_codigo")
        if (valor := params.get(nombre))
    }
    pregunta = generar_aclaracion_vaga(
        consulta=consulta,
        slots=slots,
        contexto=params.get("_contexto"),
    )

    return respuesta(
        "Necesito más detalles",
        "aclaracion",
        pregunta
        or "No estoy seguro de qué necesitas. ¿Puedes indicarme origen y destino? "
        "Por ejemplo: 'cómo voy del mercado central al aeropuerto'.",
    )
