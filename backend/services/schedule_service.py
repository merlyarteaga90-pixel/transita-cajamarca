from datetime import datetime, time, timedelta
from math import ceil
from zoneinfo import ZoneInfo


ZONA_HORARIA = ZoneInfo("America/Lima")


def convertir_a_time(valor):
    if valor is None:
        return None
    if isinstance(valor, time):
        return valor
    if isinstance(valor, timedelta):
        segundos = int(valor.total_seconds()) % (24 * 60 * 60)
        return time(segundos // 3600, (segundos % 3600) // 60, segundos % 60)
    if isinstance(valor, str):
        for formato in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(valor, formato).time()
            except ValueError:
                pass
    raise TypeError(f"No se puede convertir {type(valor)} a datetime.time")


def calcular_proxima_unidad(horario_inicio, horario_fin, frecuencia_min, ahora=None):
    """Calcula salidas teóricas desde el inicio de la ruta."""
    hora_actual = ahora or datetime.now(ZONA_HORARIA)
    if hora_actual.tzinfo is None:
        hora_actual = hora_actual.replace(tzinfo=ZONA_HORARIA)
    else:
        hora_actual = hora_actual.astimezone(ZONA_HORARIA)

    try:
        inicio_hora = convertir_a_time(horario_inicio)
        fin_hora = convertir_a_time(horario_fin)
        frecuencia = int(frecuencia_min) if frecuencia_min is not None else None
    except (TypeError, ValueError):
        inicio_hora = fin_hora = None
        frecuencia = None

    base = {
        "disponible": False,
        "hora_actual": hora_actual.strftime("%H:%M"),
        "horario_inicio": inicio_hora.strftime("%H:%M") if inicio_hora else None,
        "horario_fin": fin_hora.strftime("%H:%M") if fin_hora else None,
        "frecuencia_min": frecuencia if frecuencia and frecuencia > 0 else None,
        "proxima_salida": None,
        "minutos_restantes": None,
    }

    if not inicio_hora or not fin_hora or not frecuencia or frecuencia <= 0:
        return {
            **base,
            "estado": "DATOS_INSUFICIENTES",
            "mensaje": "No hay datos suficientes para calcular la próxima salida.",
        }

    inicio = datetime.combine(hora_actual.date(), inicio_hora, tzinfo=ZONA_HORARIA)
    fin = datetime.combine(hora_actual.date(), fin_hora, tzinfo=ZONA_HORARIA)
    if fin < inicio:
        fin += timedelta(days=1)
        if hora_actual < inicio:
            hora_actual += timedelta(days=1)

    if hora_actual < inicio:
        minutos = ceil((inicio - hora_actual).total_seconds() / 60)
        return {
            **base,
            "disponible": True,
            "estado": "ANTES_DE_INICIO",
            "proxima_salida": inicio.strftime("%H:%M"),
            "minutos_restantes": minutos,
            "mensaje": "El servicio aún no inicia; esta es la primera salida teórica.",
        }

    if hora_actual > fin:
        return {
            **base,
            "estado": "SERVICIO_FINALIZADO",
            "mensaje": "El servicio ya terminó por hoy.",
        }

    intervalo_segundos = frecuencia * 60
    transcurridos = max(0, (hora_actual - inicio).total_seconds())
    intervalos = ceil(transcurridos / intervalo_segundos)
    proxima = inicio + timedelta(minutes=intervalos * frecuencia)

    if proxima > fin:
        return {
            **base,
            "estado": "SIN_MAS_SALIDAS",
            "mensaje": "No quedan salidas teóricas programadas para hoy.",
        }

    minutos = ceil(max(0, (proxima - hora_actual).total_seconds()) / 60)
    return {
        **base,
        "disponible": True,
        "estado": "SERVICIO_ACTIVO",
        "proxima_salida": proxima.strftime("%H:%M"),
        "minutos_restantes": minutos,
        "mensaje": "Salida teórica desde el inicio de la ruta.",
    }
