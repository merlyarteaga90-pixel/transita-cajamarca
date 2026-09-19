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
from backend.services import assistant_service
from backend.services.route_code_service import resolver_codigos_ruta
from backend.services.route_engine import fmt_hora, obtener_todas_rutas
from backend.services.schedule_service import calcular_proxima_unidad


app = FastAPI(title="Asistente de Rutas de Cajamarca")
RUTA_FRONTEND = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
RUTA_FRONTEND_DIST = os.path.join(RUTA_FRONTEND, "dist")
RUTA_FRONTEND_DIST_ASSETS = os.path.join(RUTA_FRONTEND_DIST, "assets")
if os.path.exists(RUTA_FRONTEND):
    app.mount("/static", StaticFiles(directory=RUTA_FRONTEND), name="static")
if os.path.exists(RUTA_FRONTEND_DIST_ASSETS):
    app.mount("/assets", StaticFiles(directory=RUTA_FRONTEND_DIST_ASSETS), name="assets")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def inicio():
    svelte_index = os.path.join(RUTA_FRONTEND_DIST, "index.html")
    legacy_index = os.path.join(RUTA_FRONTEND, "index.html")
    return FileResponse(svelte_index if os.path.exists(svelte_index) else legacy_index)


@app.get("/api/health/db")
@app.get("/api/health")
def health(db=Depends(get_db)):
    try:
        empresas = db.execute(text("SELECT COUNT(*) FROM empresas")).scalar()
        rutas = db.execute(text("SELECT COUNT(*) FROM rutas")).scalar()
        sentidos = db.execute(text("SELECT COUNT(*) FROM sentidos")).scalar()
        puntos = db.execute(text("SELECT COUNT(*) FROM puntos_recorrido")).scalar()
        alias = db.execute(
            text("SELECT COUNT(*) FROM lugares_alias WHERE activo = TRUE")
        ).scalar()
        lugares_info = db.execute(
            text("SELECT COUNT(*) FROM lugares_info WHERE activo = TRUE")
        ).scalar()
        establecimientos = db.execute(
            text("SELECT COUNT(*) FROM establecimientos_cercanos WHERE activo = TRUE")
        ).scalar()
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail="Base de datos no disponible"
        ) from exc

    from backend.services.gemini_client import is_configured as gemini_configured

    gemini = "configurado" if gemini_configured() else "no_configurado"

    return {
        "status": "ok" if rutas and puntos else "sin_datos",
        "modo": "completo" if gemini == "configurado" else "degradado",
        "gemini": gemini,
        "empresas": empresas,
        "rutas": rutas,
        "sentidos": sentidos,
        "puntos": puntos,
        "alias": alias,
        "lugares_info": lugares_info,
        "establecimientos": establecimientos,
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

    codigo = codigos[0]
    fila = db.execute(
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

    if not fila:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    hi = fmt_hora(fila["horario_inicio"]) or None
    hf = fmt_hora(fila["horario_fin"]) or None
    frecuencia = (
        int(fila["frecuencia_general_min"])
        if fila["frecuencia_general_min"] is not None
        else None
    )
    calculo = calcular_proxima_unidad(fila["horario_inicio"], fila["horario_fin"], frecuencia)

    return {
        "codigo_ruta": fila["codigo"],
        "ruta_nombre": fila["ruta_nombre"],
        "nombre_comercial": fila["nombre_comercial"],
        "razon_social": fila["razon_social"],
        "ruc": fila["ruc"],
        "frecuencia_min": frecuencia,
        "horario_inicio": hi,
        "horario_fin": hf,
        "estado_servicio": calculo["estado"],
        "proxima_salida": calculo["proxima_salida"],
        "proximo_paso_min": calculo["minutos_restantes"],
        "hora_actual": calculo["hora_actual"],
        "mensaje_servicio": calculo["mensaje"],
    }


@app.post("/api/consultar", response_model=RespuestaAPI)
def consultar(datos: ConsultaRequest, db=Depends(get_db)):
    consulta = datos.consulta.strip()
    if not consulta:
        raise HTTPException(status_code=422, detail="La consulta no puede estar vacía")
    return assistant_service.consultar(db, datos)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print("Servidor en http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
