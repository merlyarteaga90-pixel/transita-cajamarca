from pathlib import Path
import os
import sys
from urllib.request import urlopen

RAIZ_PROYECTO = str(Path(__file__).resolve().parent.parent)
if RAIZ_PROYECTO not in sys.path:
    sys.path.insert(0, RAIZ_PROYECTO)

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
import uvicorn

from backend.database import SessionLocal
from backend.schemas import (
    ConsultaRequest,
    ProximaUnidadRequest,
    ProximaUnidadResponse,
    RespuestaAPI,
)
from backend.services.ai_service import analizar_consulta
from backend.services.query_parser import interpretar_consulta_clara
from backend.services.reference_service import resolver_referencia
from backend.services.respuesta_service import generar_respuesta
from backend.services.route_code_service import (
    normalizar_codigo_ruta,
    resolver_codigos_ruta,
)
from backend.services.route_engine import (
    buscar_ruta,
    buscar_rutas_por_lugar,
    fmt_hora,
    normalizar_referencia,
    obtener_todas_rutas,
)
from backend.services.schedule_service import calcular_proxima_unidad


app = FastAPI(title="Asistente de Rutas de Cajamarca")
RUTA_FRONTEND = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(RUTA_FRONTEND):
    app.mount("/static", StaticFiles(directory=RUTA_FRONTEND), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _respuesta(estado, tipo, respuesta, resultados=None, icono="🚌", **extra):
    return {
        "estado": estado,
        "icono": icono,
        "tipo": tipo,
        "resultados": resultados or [],
        "respuesta": respuesta,
        **extra,
    }


def _referencia_presente(referencia: str | None, consulta: str) -> bool:
    if not referencia:
        return True
    ref_n = normalizar_referencia(referencia)
    return bool(ref_n and ref_n in normalizar_referencia(consulta))


def _candidatos(resolucion: dict) -> list[str]:
    candidatos = []
    for sugerencia in resolucion.get("sugerencias", []):
        nombre = sugerencia.get("nombre") or sugerencia.get("ubicacion")
        if nombre and nombre not in candidatos:
            candidatos.append(nombre)
    return candidatos[:5]


def _respuesta_ambigua(referencia: str, rol: str, resolucion: dict):
    candidatos = _candidatos(resolucion)
    return _respuesta(
        f"{rol.capitalize()} ambiguo",
        "aclaracion",
        f"'{referencia}' puede referirse a varios lugares. Escribe el nombre completo.",
        candidatos=candidatos,
    )


def _rutas_selector(db):
    rutas = []
    vistos = set()
    for ruta in obtener_todas_rutas(db):
        if ruta["codigo"] in vistos:
            continue
        vistos.add(ruta["codigo"])
        rutas.append({**ruta, "codigo_ruta": ruta["codigo"]})
    return rutas


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


def _datos_info_rutas(db, codigos: list[str], intencion: str):
    resultados = []
    for codigo in codigos:
        fila = _fila_ruta(db, codigo)
        if not fila:
            continue
        hi = fmt_hora(fila["horario_inicio"]) or None
        hf = fmt_hora(fila["horario_fin"]) or None
        frecuencia = int(fila["frecuencia_general_min"]) if fila["frecuencia_general_min"] is not None else None
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
            "tarifa_general": float(fila["tarifa_general"]) if fila["tarifa_general"] is not None else None,
            "tarifa_medio_pasaje": float(fila["tarifa_medio_pasaje"]) if fila["tarifa_medio_pasaje"] is not None else None,
            "consulta_tipo": intencion,
        }
        if intencion == "PROXIMA_UNIDAD":
            calculo = calcular_proxima_unidad(
                fila["horario_inicio"], fila["horario_fin"], frecuencia
            )
            item.update({
                "estado_servicio": calculo["estado"],
                "proxima_salida": calculo["proxima_salida"],
                "proximo_paso_min": calculo["minutos_restantes"],
                "hora_actual": calculo["hora_actual"],
                "mensaje_servicio": calculo["mensaje"],
            })
        resultados.append(item)
    return resultados


def _interpretar(consulta: str):
    interpretacion = interpretar_consulta_clara(consulta)
    if interpretacion:
        return interpretacion

    try:
        interpretacion = analizar_consulta(consulta)
    except Exception:
        return None

    if not _referencia_presente(interpretacion.get("origen"), consulta):
        interpretacion["origen"] = None
    if not _referencia_presente(interpretacion.get("destino"), consulta):
        interpretacion["destino"] = None
    return interpretacion


@app.get("/")
def inicio():
    return FileResponse(os.path.join(RUTA_FRONTEND, "index.html"))


@app.get("/api/health/db")
@app.get("/api/health")
def health(db=Depends(get_db)):
    try:
        empresas = db.execute(text("SELECT COUNT(*) FROM empresas")).scalar()
        rutas = db.execute(text("SELECT COUNT(*) FROM rutas")).scalar()
        sentidos = db.execute(text("SELECT COUNT(*) FROM sentidos")).scalar()
        puntos = db.execute(text("SELECT COUNT(*) FROM puntos_recorrido")).scalar()
        alias = db.execute(text("SELECT COUNT(*) FROM lugares_alias WHERE activo = TRUE")).scalar()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="MySQL no está disponible") from exc

    ollama = "no_disponible"
    try:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        with urlopen(f"{base_url}/api/tags", timeout=0.5) as respuesta:
            if respuesta.status == 200:
                ollama = "disponible"
    except Exception:
        pass

    return {
        "status": "ok" if rutas and puntos else "sin_datos",
        "modo": "completo" if ollama == "disponible" else "degradado",
        "ollama": ollama,
        "empresas": empresas,
        "rutas": rutas,
        "sentidos": sentidos,
        "puntos": puntos,
        "alias": alias,
    }


@app.get("/api/rutas")
def listar_rutas(db=Depends(get_db)):
    return {"rutas": obtener_todas_rutas(db)}


@app.post("/api/proxima-unidad", response_model=ProximaUnidadResponse)
def proxima_unidad(datos: ProximaUnidadRequest, db=Depends(get_db)):
    codigos = resolver_codigos_ruta(db, datos.ruta_codigo)
    if not codigos:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    if len(codigos) > 1:
        raise HTTPException(
            status_code=409,
            detail=f"Especifica una variante: {', '.join(codigos)}",
        )

    item = _datos_info_rutas(db, codigos, "PROXIMA_UNIDAD")[0]
    return {
        **item,
        "proximo_paso_min": item["proximo_paso_min"],
    }


@app.post("/api/consultar", response_model=RespuestaAPI)
def consultar(datos: ConsultaRequest, db=Depends(get_db)):
    consulta = datos.consulta.strip()
    if not consulta:
        raise HTTPException(status_code=422, detail="La consulta no puede estar vacía")

    interpretacion = {
        "intencion": datos.intencion,
        "origen": datos.origen,
        "destino": datos.destino,
        "ruta_codigo": str(datos.ruta_codigo) if datos.ruta_codigo is not None else None,
    }
    if not interpretacion["intencion"]:
        interpretacion = _interpretar(consulta)
    if not interpretacion:
        return _respuesta(
            "Consulta no comprendida",
            "aclaracion",
            "No pude identificar la consulta. Prueba indicando 'de [origen] a [destino]' o el código de la ruta.",
        )

    intencion = interpretacion.get("intencion")
    origen = interpretacion.get("origen")
    destino = interpretacion.get("destino")
    ruta_codigo = interpretacion.get("ruta_codigo")

    if intencion == "SALUDO":
        return _respuesta(
            "Saludo",
            "saludo",
            "¡Hola! Puedo buscar rutas directas, rutas por lugar, horarios, frecuencias y tarifas.",
            icono="👋",
        )

    if intencion == "RUTAS_POR_LUGAR":
        if not destino:
            return _respuesta(
                "Lugar no especificado",
                "aclaracion",
                "Indica el lugar por donde quieres saber qué rutas pasan.",
            )

        resolucion = resolver_referencia(db, destino)
        if resolucion["estado"] == "AMBIGUO":
            return _respuesta_ambigua(destino, "lugar", resolucion)
        if resolucion["estado"] == "NO_ENCONTRADO":
            return _respuesta(
                "Lugar no reconocido",
                "aclaracion",
                f"No reconocí el lugar '{destino}'. Prueba con otro nombre o una referencia cercana.",
            )

        encontrados = []
        for ubicacion in resolucion["ubicaciones"]:
            encontrados.extend(buscar_rutas_por_lugar(db, ubicacion["oficial"]))

        unicos = {}
        for ruta in encontrados:
            clave = (ruta["ruta"], ruta["sentido"])
            unicos.setdefault(clave, ruta)
        rutas = list(unicos.values())
        if not rutas:
            return _respuesta(
                "Sin rutas",
                "sin_resultados",
                f"No encontré rutas que pasen por '{destino}'.",
            )

        resultados = [{"codigo_ruta": r["ruta"], **{k: v for k, v in r.items() if k != "ruta"}} for r in rutas]
        opciones = ", ".join(f"{r['codigo_ruta']} ({r['sentido']})" for r in resultados)
        return _respuesta(
            f"Rutas por lugar: {len(resultados)}",
            "rutas_por_lugar",
            f"Encontré {len(resultados)} opciones que pasan por '{destino}': {opciones}.",
            resultados,
        )

    if intencion in ("HORARIO", "FRECUENCIA", "TARIFA", "PROXIMA_UNIDAD"):
        if not ruta_codigo:
            return _respuesta(
                "Indica una ruta",
                "selector_ruta",
                f"Indica el código de la ruta para consultar {intencion.lower()}.",
                rutas=_rutas_selector(db),
                intencion_solicitada=intencion,
            )

        codigos = resolver_codigos_ruta(db, ruta_codigo)
        if not codigos:
            canonico = normalizar_codigo_ruta(ruta_codigo) or str(ruta_codigo)
            return _respuesta(
                "Ruta no encontrada",
                "error",
                f"No encontré la ruta o familia {canonico}.",
                icono="⚠️",
            )

        resultados = _datos_info_rutas(db, codigos, intencion)
        nombres = ", ".join(codigos)
        etiqueta = {
            "HORARIO": "horario",
            "FRECUENCIA": "frecuencia",
            "TARIFA": "tarifa",
            "PROXIMA_UNIDAD": "próxima salida teórica",
        }[intencion]
        return _respuesta(
            f"{etiqueta.capitalize()}: {len(resultados)} ruta(s)",
            "info",
            f"Encontré información de {etiqueta} para: {nombres}.",
            resultados,
            intencion_solicitada=intencion,
        )

    if intencion != "BUSCAR_RUTA":
        return _respuesta(
            "Consulta no procesada",
            "aclaracion",
            "No pude identificar qué información necesitas.",
        )

    if not origen and not destino:
        return _respuesta(
            "Datos incompletos",
            "aclaracion",
            "Indica desde dónde partes y a dónde quieres ir. Por ejemplo: 'de Shudal a Hoyos Rubio'.",
        )

    if not origen:
        resolucion = resolver_referencia(db, destino)
        if resolucion["estado"] == "AMBIGUO":
            return _respuesta_ambigua(destino, "destino", resolucion)
        if resolucion["estado"] == "NO_ENCONTRADO":
            return _respuesta(
                "Destino no reconocido",
                "aclaracion",
                f"No reconocí el destino '{destino}'.",
            )
        nombre = resolucion["ubicaciones"][0]["oficial"] if len(resolucion["ubicaciones"]) == 1 else destino
        return _respuesta(
            "Falta el origen",
            "aclaracion",
            f"Entiendo que quieres ir a {nombre}. ¿Desde dónde partes?",
        )

    if not destino:
        resolucion = resolver_referencia(db, origen)
        if resolucion["estado"] == "AMBIGUO":
            return _respuesta_ambigua(origen, "origen", resolucion)
        if resolucion["estado"] == "NO_ENCONTRADO":
            return _respuesta("Origen no reconocido", "aclaracion", f"No reconocí el origen '{origen}'.")
        nombre = resolucion["ubicaciones"][0]["oficial"] if len(resolucion["ubicaciones"]) == 1 else origen
        return _respuesta("Falta el destino", "aclaracion", f"Entiendo que partes de {nombre}. ¿A dónde quieres ir?")

    resolucion_origen = resolver_referencia(db, origen)
    resolucion_destino = resolver_referencia(db, destino)
    if resolucion_origen["estado"] == "AMBIGUO":
        return _respuesta_ambigua(origen, "origen", resolucion_origen)
    if resolucion_destino["estado"] == "AMBIGUO":
        return _respuesta_ambigua(destino, "destino", resolucion_destino)
    if resolucion_origen["estado"] == "NO_ENCONTRADO":
        return _respuesta("Origen no reconocido", "aclaracion", f"No reconocí el origen '{origen}'.")
    if resolucion_destino["estado"] == "NO_ENCONTRADO":
        return _respuesta("Destino no reconocido", "aclaracion", f"No reconocí el destino '{destino}'.")

    encontrados = []
    vistos = set()
    for ubicacion_origen in resolucion_origen["ubicaciones"]:
        for ubicacion_destino in resolucion_destino["ubicaciones"]:
            for ruta in buscar_ruta(db, ubicacion_origen["oficial"], ubicacion_destino["oficial"]):
                clave = (ruta["codigo"], ruta["sentido"])
                if clave not in vistos:
                    vistos.add(clave)
                    encontrados.append(ruta)

    if not encontrados:
        return _respuesta(
            "Sin rutas directas",
            "sin_resultados",
            f"No encontré una ruta directa para ir desde {origen} hasta {destino}.",
        )

    resultados = []
    for ruta in encontrados:
        frecuencia = int(ruta["frecuencia_min"]) if ruta.get("frecuencia_min") is not None else None
        calculo = calcular_proxima_unidad(
            ruta.get("horario_inicio"), ruta.get("horario_fin"), frecuencia
        )
        puntos = [
            {"nombre": punto.get("nombre", ""), "orden": punto.get("orden", indice)}
            for indice, punto in enumerate(ruta.get("camino", []))
        ]
        resultados.append({
            "codigo_ruta": ruta["codigo"],
            "sentido": ruta["sentido"],
            "nombre_comercial": ruta.get("nombre_comercial") or ruta.get("razon_social") or "",
            "razon_social": ruta.get("razon_social") or "",
            "ruc": ruta.get("ruc") or "",
            "origen": ruta["origen"].get("nombre", ""),
            "destino": ruta["destino"].get("nombre", ""),
            "distancia_total_ruta_km": round(float(ruta["distancia_km"]), 2) if ruta.get("distancia_km") is not None else None,
            "tiempo_total_ruta_min": ruta.get("tiempo_total_min"),
            "frecuencia_min": frecuencia,
            "horario": f"{ruta.get('horario_inicio')} - {ruta.get('horario_fin')}" if ruta.get("horario_inicio") and ruta.get("horario_fin") else None,
            "horario_inicio": ruta.get("horario_inicio") or None,
            "horario_fin": ruta.get("horario_fin") or None,
            "tarifa_general": float(ruta["tarifa_general"]) if ruta.get("tarifa_general") is not None else None,
            "tarifa_medio_pasaje": float(ruta["tarifa_medio_pasaje"]) if ruta.get("tarifa_medio_pasaje") is not None else None,
            "estado_servicio": calculo["estado"],
            "proxima_salida": calculo["proxima_salida"],
            "proximo_paso_min": calculo["minutos_restantes"],
            "mensaje_servicio": calculo["mensaje"],
            "puntos": puntos,
        })

    return _respuesta(
        f"Rutas directas encontradas: {len(resultados)}",
        "ruta",
        generar_respuesta(consulta, resultados),
        resultados,
    )


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print("Servidor en http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
