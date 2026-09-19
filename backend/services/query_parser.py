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


_STOP_LUGAR = (
    r"(?:pero|y)\s+no\s+s[eé]\s+(?:desde|de|a|ad[oó]nde)\s+d[oó]nde",
    r"no\s+s[eé]\s+(?:desde|de|a|ad[oó]nde)\s+d[oó]nde",
    r"no\s+s[eé]\s+(?:desde|de)\s+d[oó]nde",
    r"no\s+s[eé]\s+a\s+d[oó]nde",
    r"no\s+s[eé]\s+ad[oó]nde",
    r"por\s+favor",
    r"ayuda",
)


def _recortar_lugar(texto: str | None) -> str | None:
    """Elimina frases colgantes como 'pero no sé desde dónde'."""
    if not texto:
        return None
    for patron in _STOP_LUGAR:
        texto = re.split(patron, texto, flags=re.IGNORECASE)[0]
    return _limpiar_lugar(texto)


def _prep_destino() -> str:
    return r"(?:a|al|a\s+la|a\s+los|a\s+las|hacia|hasta|pa(?:ra)?)"


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

    if re.fullmatch(r"(?:chau|adios|hasta luego|nos vemos|bye)[!. ]*", simple):
        return {"intencion": "DESPEDIDA", "origen": None, "destino": None, "ruta_codigo": None}

    info_lugar = re.match(
        r"^(?:qu[eé]\s+es|qu[eé]\s+hay\s+en|d[oó]nde\s+(?:queda|es)|sobre)\s+(?!la\s+ruta|r\s*-?\s*\d)(.+?)[?.!]*$",
        original,
        re.IGNORECASE,
    )
    if info_lugar:
        return {
            "intencion": "INFO_LUGAR",
            "origen": None,
            "destino": _limpiar_lugar(info_lugar.group(1)),
            "ruta_codigo": None,
        }

    lugares_cercanos = re.match(
        r"^(?:qu[eé]\s+hay\s+cerca\s+(?:d[ea]l?)?|cerca\s+de|negocios\s+cerca\s+de|bancos\s+cerca\s+de|restaurantes\s+cerca\s+de|farmacias?\s+cerca\s+de)\s+(.+?)[?.!]*$",
        original,
        re.IGNORECASE,
    )
    if lugares_cercanos:
        return {
            "intencion": "LUGARES_CERCANOS",
            "origen": None,
            "destino": _limpiar_lugar(lugares_cercanos.group(1)),
            "ruta_codigo": None,
        }

    fuera = re.match(
        r"^(?:qu[eé]\s+hora\s+es\s+en|clima\s+en|cu[aá]ntos?\s+habitantes|qu[eé]\s+idiomas?\s+se\s+habla|cu[aá]nto\s+falta\s+para\s+navidad)",
        simple,
    )
    if fuera:
        return {
            "intencion": "FUERA_DE_ALCANCE",
            "origen": None,
            "destino": None,
            "ruta_codigo": None,
        }

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

    if re.search(r"\bruta\s*\d{1,2}\b|\br\s*\d{1,2}\b", simple):
        return {
            "intencion": "PROXIMA_UNIDAD",
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
        rf"\b(?:de|desde)\s+(.+?)\s+{_prep_destino()}\s+(.+)$",
        rf"\bestoy\s+(?:en|por|x)\s+(.+?)\s+y\s+(?:quiero\s+ir|voy|necesito\s+(?:ir|llegar))\s+{_prep_destino()}\s+(.+)$",
    ]
    for patron in patrones_viaje:
        viaje = re.search(patron, original, re.IGNORECASE)
        if viaje:
            return {
                "intencion": "BUSCAR_RUTA",
                "origen": _recortar_lugar(viaje.group(1)),
                "destino": _recortar_lugar(viaje.group(2)),
                "ruta_codigo": None,
            }

    destino_sin_origen = [
        rf"\brutas?\s+(?:para\s+)?(?:ir|llegar)\s+{_prep_destino()}\s+(.+)$",
        rf"\b(?:qu[eé]|q|cu[aá]l)\s+(?:ruta|combi|micro|bus)\s+(?:me\s+)?(?:lleva|llevar[ií]a|va)\s+{_prep_destino()}\s+(.+)$",
        rf"\b(?:quiero\s+ir|c[oó]mo\s+(?:voy|llego|puedo\s+llegar)|necesito\s+(?:ir|llegar)|voy)\s+{_prep_destino()}\s+(.+)$",
    ]
    for patron in destino_sin_origen:
        destino = re.search(patron, original, re.IGNORECASE)
        if destino:
            return {
                "intencion": "BUSCAR_RUTA",
                "origen": None,
                "destino": _recortar_lugar(destino.group(1)),
                "ruta_codigo": None,
            }

    if re.fullmatch(r"(?:quiero ir|como llego|necesito ir|necesito llegar)[?.! ]*", simple):
        return {"intencion": "BUSCAR_RUTA", "origen": None, "destino": None, "ruta_codigo": None}

    solo_origen = re.search(
        r"\b(?:desde|de|salgo\s+de|parto\s+de|estoy\s+(?:en|por|x))\s+(.+)$",
        original,
        re.IGNORECASE,
    )
    if solo_origen:
        return {
            "intencion": "BUSCAR_RUTA",
            "origen": _recortar_lugar(solo_origen.group(1)),
            "destino": None,
            "ruta_codigo": None,
        }

    # Forma corta frecuente: "shudal a hoyos rubio".
    corto = re.fullmatch(r"(.+?)\s+(?:a|hasta|hacia|pa(?:ra)?)\s+(.+)", original, re.IGNORECASE)
    if corto:
        origen_corto = _sin_tildes(corto.group(1).lower())
        if re.search(r"\b(?:ruta|rutas|combi|micro|bus|quiero|como|necesito|voy)\b", origen_corto):
            return None
        return {
            "intencion": "BUSCAR_RUTA",
            "origen": _recortar_lugar(corto.group(1)),
            "destino": _recortar_lugar(corto.group(2)),
            "ruta_codigo": None,
        }

    return None
