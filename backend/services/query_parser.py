import re
import unicodedata


def _sin_tildes(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _limpiar_lugar(texto: str | None) -> str | None:
    if not texto:
        return None
    texto = texto.strip(" \t\r\n,.;:!?¿¡\"'")
    texto = re.sub(r"\s+", " ", texto)
    return texto or None


def _extraer_codigo(texto: str) -> str | None:
    patron_ruta = re.search(
        r"\b(?:ruta|r)\s*[-:]?\s*(\d{1,2})"
        r"(?:\s*(?:[-./]|\(|var(?:iante)?\s*)\s*(\d{1,2})\)?)?",
        texto,
        re.IGNORECASE,
    )
    if patron_ruta:
        base, variante = patron_ruta.groups()
        return f"{base}-{variante}" if variante else base

    numero = re.search(r"\b(\d{1,2})(?:\s*[-.]\s*(\d{1,2}))?\b", texto)
    if numero:
        base, variante = numero.groups()
        return f"{base}-{variante}" if variante else base
    return None


def interpretar_consulta_clara(mensaje: str) -> dict | None:
    """Interpreta frases frecuentes sin depender de Ollama."""
    original = re.sub(r"\s+", " ", mensaje.strip())
    simple = _sin_tildes(original.lower())

    if re.fullmatch(r"(?:hola|buenas|buenos dias|buenas tardes|buenas noches|gracias|chau|adios)[!. ]*", simple):
        return {"intencion": "SALUDO", "origen": None, "destino": None, "ruta_codigo": None}

    intenciones_ruta = (
        ("HORARIO", r"\b(?:horario|hora|a que hora)\b"),
        ("FRECUENCIA", r"\b(?:frecuencia|cada cuanto|cada que tiempo)\b"),
        ("TARIFA", r"\b(?:tarifa|pasaje|cuanto cuesta|precio)\b"),
        ("PROXIMA_UNIDAD", r"\b(?:proxima (?:unidad|combi)|cuando pasa|cuanto falta)\b"),
    )
    for intencion, patron in intenciones_ruta:
        if re.search(patron, simple):
            return {
                "intencion": intencion,
                "origen": None,
                "destino": None,
                "ruta_codigo": _extraer_codigo(simple),
            }

    por_lugar = re.search(
        r"\b(?:qu[eé]|q|cu[aá]les?)\s+rutas?\s+(?:pasan?|van)\s+(?:por|x)\s+(.+)$",
        original,
        re.IGNORECASE,
    )
    if por_lugar:
        return {
            "intencion": "RUTAS_POR_LUGAR",
            "origen": None,
            "destino": _limpiar_lugar(por_lugar.group(1)),
            "ruta_codigo": None,
        }

    patrones_viaje = [
        r"\b(?:de|desde)\s+(.+?)\s+(?:a|hasta|hacia|pa(?:ra)?)\s+(.+)$",
        r"\bestoy\s+(?:en|por|x)\s+(.+?)\s+y\s+(?:quiero\s+ir|voy|necesito\s+(?:ir|llegar))\s+(?:a|hacia|pa(?:ra)?)\s+(.+)$",
    ]
    for patron in patrones_viaje:
        viaje = re.search(patron, original, re.IGNORECASE)
        if viaje:
            return {
                "intencion": "BUSCAR_RUTA",
                "origen": _limpiar_lugar(viaje.group(1)),
                "destino": _limpiar_lugar(viaje.group(2)),
                "ruta_codigo": None,
            }

    destino = re.search(
        r"\b(?:quiero\s+ir|c[oó]mo\s+llego|necesito\s+(?:ir|llegar)|voy)\s+"
        r"(?:a|hacia|pa(?:ra)?)\s+(.+)$",
        original,
        re.IGNORECASE,
    )
    if destino:
        return {
            "intencion": "BUSCAR_RUTA",
            "origen": None,
            "destino": _limpiar_lugar(destino.group(1)),
            "ruta_codigo": None,
        }

    if re.fullmatch(r"(?:quiero ir|como llego|necesito ir|necesito llegar)[?.! ]*", simple):
        return {"intencion": "BUSCAR_RUTA", "origen": None, "destino": None, "ruta_codigo": None}

    # Forma corta frecuente: "shudal a hoyos rubio".
    corto = re.fullmatch(r"(.+?)\s+(?:a|hasta|hacia|pa(?:ra)?)\s+(.+)", original, re.IGNORECASE)
    if corto:
        return {
            "intencion": "BUSCAR_RUTA",
            "origen": _limpiar_lugar(corto.group(1)),
            "destino": _limpiar_lugar(corto.group(2)),
            "ruta_codigo": None,
        }

    return None
