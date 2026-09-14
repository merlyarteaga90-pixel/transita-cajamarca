def generar_respuesta(_mensaje_usuario: str, resultados: list):
    """Genera un resumen determinista; las cards contienen el detalle."""
    if not resultados:
        return "No encontré rutas directas para ese recorrido."

    opciones = []
    for resultado in resultados:
        codigo = resultado.get("codigo_ruta")
        sentido = resultado.get("sentido")
        etiqueta = f"{codigo} ({sentido})" if sentido else str(codigo)
        if etiqueta not in opciones:
            opciones.append(etiqueta)

    if len(opciones) == 1:
        return (
            f"Encontré una opción directa: {opciones[0]}. "
            "Revisa en la tarjeta los puntos por donde pasa y los datos generales de la ruta."
        )

    return (
        f"Encontré {len(opciones)} opciones directas: {', '.join(opciones)}. "
        "Revisa cada tarjeta para comparar sus recorridos y datos generales."
    )
