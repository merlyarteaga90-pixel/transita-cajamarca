"""
Importador del diccionario de referencias de Cajamarca al MySQL.

Lee por defecto el CSV versionado:
resources/lugares_alias.csv
(se puede sobreescribir con ALIAS_CSV_PATH o pasando la ruta como argumento;
con --excel <ruta> se puede leer la hoja diccionario_referencias del Excel original).

Columnas esperadas:
    referencia        -> como la gente llama al lugar
    ubicacion_oficial -> nombre oficial del punto en puntos_recorrido

Ejecutar desde la raiz del proyecto:
    python resources/importar_diccionario_alias.py [ruta_csv_opcional]
    python resources/importar_diccionario_alias.py --excel <ruta_excel>

Requiere:
    pip install sqlalchemy pymysql
    (openpyxl solo si se usa --excel)
"""

import csv
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

PROYECTO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROYECTO))

from backend.services.route_engine import normalizar_referencia  # noqa: E402

CSV_PATH = os.getenv(
    "ALIAS_CSV_PATH",
    str(PROYECTO / "resources" / "lugares_alias.csv"),
)
EXCEL_PATH = os.getenv("ALIAS_EXCEL_PATH", "")

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3307")
DB_NAME = os.getenv("DB_NAME", "asistente_rutas")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

# ============================================================
# CORRECCIONES CONFIRMADAS
# ============================================================

# Referencias con doble destino en el Excel: se conserva solo el correcto.
# (referencia_normalizada, ubicacion_oficial a conservar)
REGLAS_CONFLICTOS = {
    "angamos cdra 14": "Jr. Angamos Cdra 14",
    "cp la chimba": "C.P. La Chimba",
}

# Alias genericos confirmados: un alias con varios destinos posibles.
ALIAS_MULTIPLES = [
    ("baños del inca", "AV. MANCO CAPAC"),
    ("baños del inca", "CARRETERA CAJAMARCA - BAÑOS DEL INCA"),
]


def limpiar(texto) -> str:
    if texto is None:
        return ""
    return str(texto).strip()


def leer_csv(ruta: str) -> list:
    filas = []
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        lector = csv.DictReader(f)
        for linea in lector:
            ref = limpiar(linea.get("referencia"))
            ubic = limpiar(linea.get("ubicacion_oficial"))
            if not ref or not ubic:
                continue
            filas.append((ref, ubic))
    return filas


def leer_excel(ruta: str) -> list:
    import openpyxl

    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    ws = wb["diccionario_referencias"]

    filas = []
    for ref, ubic in ws.iter_rows(min_row=2, values_only=True):
        ref = limpiar(ref)
        ubic = limpiar(ubic)
        if not ref or not ubic:
            continue
        filas.append((ref, ubic))

    return filas


def importar(engine, fuente: str):
    print("Importador Diccionario de Referencias -> MySQL")
    print(f"Base de datos: {DB_NAME}@{DB_HOST}:{DB_PORT}")
    print(f"Archivo: {fuente}")

    if fuente.lower().endswith((".xlsx", ".xlsm", ".xltx", ".xltm")):
        filas = leer_excel(fuente)
    else:
        filas = leer_csv(fuente)
    print(f"\nFilas leidas: {len(filas)}")

    # Cargar nombres oficiales de la base para validar destinos
    with engine.connect() as conn:
        puntos_db = {
            normalizar_referencia(r[0]): r[0]
            for r in conn.execute(text(
                "SELECT DISTINCT nombre_original FROM puntos_recorrido"
            )).fetchall()
        }

    # Aplicar reglas de conflicto y agregar alias genericos
    filas_finales = []
    descartadas = 0
    for ref, ubic in filas:
        ref_n = normalizar_referencia(ref)
        regla = REGLAS_CONFLICTOS.get(ref_n)
        if regla is not None and ubic != regla:
            descartadas += 1
            print(f"  [CONFLICTO] Descartado '{ref}' -> '{ubic}' (se conserva '{regla}')")
            continue
        filas_finales.append((ref, ubic))

    for ref, ubic in ALIAS_MULTIPLES:
        filas_finales.append((ref, ubic))
        print(f"  [ALIAS MULTIPLE] Agregado '{ref}' -> '{ubic}'")

    # Validar que cada destino exista en puntos_recorrido
    invalidas = []
    for ref, ubic in filas_finales:
        ubic_n = normalizar_referencia(ubic)
        if ubic_n not in puntos_db:
            invalidas.append((ref, ubic))

    if invalidas:
        print(f"\nERROR: {len(invalidas)} ubicaciones no existen en puntos_recorrido:")
        for ref, ubic in invalidas:
            print(f"  '{ref}' -> '{ubic}'")
        sys.exit(1)

    # Deduplicar pares (referencia_normalizada, ubicacion_normalizada)
    vistos = {}
    for ref, ubic in filas_finales:
        ref_n = normalizar_referencia(ref)
        ubic_n = normalizar_referencia(ubic)
        vistos[(ref_n, ubic_n)] = (ref, ubic)

    print(f"\nPares unicos a insertar: {len(vistos)} (descartados por conflicto: {descartadas})")

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM lugares_alias"))
        print("Tabla lugares_alias limpiada")

        insertados = 0
        for (ref_n, ubic_n), (ref, ubic) in vistos.items():
            conn.execute(
                text("""
                    INSERT INTO lugares_alias (
                        referencia_original, referencia_normalizada,
                        ubicacion_oficial, ubicacion_normalizada,
                        activo, fuente
                    )
                    VALUES (:ref, :refn, :ubi, :ubin, TRUE, 'EXCEL_DICCIONARIO')
                """),
                {
                    "ref": ref, "refn": ref_n,
                    "ubi": ubic, "ubin": ubic_n,
                }
            )
            insertados += 1

        print(f"Alias insertados: {insertados}")

        total = conn.execute(
            text("SELECT COUNT(*) FROM lugares_alias")
        ).scalar()
        referencias = conn.execute(
            text("SELECT COUNT(DISTINCT referencia_normalizada) FROM lugares_alias")
        ).scalar()
        ubicaciones = conn.execute(
            text("SELECT COUNT(DISTINCT ubicacion_normalizada) FROM lugares_alias")
        ).scalar()

    print("\n=== Resumen ===")
    print(f"  Alias totales: {total}")
    print(f"  Referencias unicas: {referencias}")
    print(f"  Ubicaciones oficiales unicas: {ubicaciones}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--excel"]:
        fuente = args[1] if len(args) > 1 else EXCEL_PATH
        if not fuente:
            print("ERROR: indica la ruta del Excel: --excel <ruta>")
            sys.exit(1)
    elif args:
        fuente = args[0]
    else:
        fuente = CSV_PATH
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    importar(engine, fuente)
