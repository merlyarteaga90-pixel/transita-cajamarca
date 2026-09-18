from typing import Any, Literal

from pydantic import BaseModel, Field


Intencion = Literal[
    "SALUDO",
    "DESPEDIDA",
    "BUSCAR_RUTA",
    "RUTAS_POR_LUGAR",
    "QUE_RUTA_PASA_CERCA",
    "INFO_LUGAR",
    "LUGARES_CERCANOS",
    "INTENCION_VAGA",
    "PROXIMA_UNIDAD",
    "HORARIO",
    "FRECUENCIA",
    "TARIFA",
    "FUERA_DE_ALCANCE",
]


class UserLocation(BaseModel):
    lat: float
    lon: float


class ConsultaRequest(BaseModel):
    consulta: str = Field(min_length=1, max_length=500)
    origen: str | None = None
    destino: str | None = None
    intencion: Intencion | None = None
    ruta_codigo: str | int | None = None
    contexto: dict[str, Any] | None = None
    user_location: UserLocation | None = None
    session_id: str | None = None


class ProximaUnidadRequest(BaseModel):
    ruta_codigo: str | int


class RespuestaAPI(BaseModel):
    estado: str
    icono: str = "🚌"
    tipo: Literal[
        "ruta",
        "alternativas",
        "rutas_por_lugar",
        "info",
        "info_lugar",
        "lugares_cercanos",
        "selector_ruta",
        "aclaracion",
        "sin_resultados",
        "saludo",
        "despedida",
        "error",
    ]
    resultados: list[dict[str, Any]] = Field(default_factory=list)
    respuesta: str
    candidatos: list[str] = Field(default_factory=list)
    rutas: list[dict[str, Any]] = Field(default_factory=list)
    intencion_solicitada: str | None = None
    contexto: dict[str, Any] = Field(default_factory=dict)
    session_id: str | None = None


class ProximaUnidadResponse(BaseModel):
    codigo_ruta: str
    ruta_nombre: str | None = None
    nombre_comercial: str | None = None
    razon_social: str | None = None
    ruc: str | None = None
    frecuencia_min: int | None = None
    horario_inicio: str | None = None
    horario_fin: str | None = None
    estado_servicio: str
    proxima_salida: str | None = None
    proximo_paso_min: int | None = None
    hora_actual: str | None = None
    mensaje_servicio: str | None = None
