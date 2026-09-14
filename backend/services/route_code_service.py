import re

from sqlalchemy import text


def normalizar_codigo_ruta(valor) -> str | None:
    if valor is None:
        return None

    codigo = str(valor).strip().upper()
    codigo = re.sub(r"^RUTA\s*", "", codigo)
    codigo = re.sub(r"^R\s*-?\s*", "", codigo)
    codigo = codigo.replace("(", "-").replace(")", "")
    codigo = re.sub(r"\bVAR(?:IANTE)?\s*", "-", codigo)
    codigo = codigo.replace(".", "-").replace("/", "-")
    codigo = re.sub(r"\s+", "", codigo)
    codigo = re.sub(r"-+", "-", codigo).strip("-")

    coincidencia = re.fullmatch(r"(\d{1,2})(?:-(\d{1,2}))?", codigo)
    if not coincidencia:
        return None

    base, variante = coincidencia.groups()
    canonico = f"R-{int(base):02d}"
    if variante is not None:
        canonico += f"-{int(variante)}"
    return canonico


def resolver_codigos_ruta(db, valor) -> list[str]:
    """Devuelve el código exacto o todas las variantes de una familia."""
    canonico = normalizar_codigo_ruta(valor)
    if not canonico:
        return []

    exacto = db.execute(
        text("SELECT codigo FROM rutas WHERE codigo = :codigo AND activo = TRUE"),
        {"codigo": canonico},
    ).scalar()
    if exacto:
        return [exacto]

    if re.fullmatch(r"R-\d{2}", canonico):
        variantes = db.execute(
            text(
                "SELECT codigo FROM rutas "
                "WHERE codigo LIKE :familia AND activo = TRUE ORDER BY codigo"
            ),
            {"familia": f"{canonico}-%"},
        ).scalars().all()
        return list(variantes)

    return []
