"""Inicializa la base de datos SQLite desde los archivos SQL del directorio database/.

Uso:
    python -m backend.init_db

Carga en orden:
    database/00_schema.sql
    database/01_seed.sql
    database/02_info_lugares.sql
    database/03_establecimientos_cercanos.sql
    database/04_puntos_coords.sql

Si la base ya existe con tablas pobladas, solo carga los datos nuevos (no duplica).
"""

from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

DB_PATH = os.getenv("DB_PATH", "transita_cajamarca.db")
RAIZ = Path(__file__).resolve().parent.parent
DB_DIR = RAIZ / "database"

ARCHIVOS_SQL = [
    "00_schema.sql",
    "01_seed.sql",
    "02_info_lugares.sql",
    "03_establecimientos_cercanos.sql",
    "04_puntos_coords.sql",
]


def _tablas_pobladas(conn: sqlite3.Connection) -> set[str]:
    """Devuelve los nombres de tablas que ya tienen al menos una fila."""
    pobladas = set()
    filas = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    for (nombre,) in filas:
        if nombre.startswith("sqlite_"):
            continue
        cursor = conn.execute(f"SELECT COUNT(*) FROM \"{nombre}\"")
        (cantidad,) = cursor.fetchone()
        if cantidad > 0:
            pobladas.add(nombre)
    return pobladas


def inicializar(reset: bool = False) -> None:
    if reset and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"[init_db] Archivo eliminado: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    tablas_existentes = set(
        nombre
        for (nombre,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    )

    alias_count = 0
    if "lugares_alias" in tablas_existentes:
        (alias_count,) = conn.execute(
            "SELECT COUNT(*) FROM lugares_alias"
        ).fetchone()

    info_count = 0
    if "lugares_info" in tablas_existentes:
        (info_count,) = conn.execute(
            "SELECT COUNT(*) FROM lugares_info"
        ).fetchone()

    est_count = 0
    if "establecimientos_cercanos" in tablas_existentes:
        (est_count,) = conn.execute(
            "SELECT COUNT(*) FROM establecimientos_cercanos"
        ).fetchone()

    for archivo in ARCHIVOS_SQL:
        ruta = DB_DIR / archivo
        if not ruta.exists():
            print(f"[init_db] AVISO: {ruta} no existe, saltando")
            continue

        if archivo == "00_schema.sql":
            print(f"[init_db] Cargando schema: {archivo}")
            conn.executescript(ruta.read_text(encoding="utf-8"))
            continue

        if archivo == "04_puntos_coords.sql":
            print(f"[init_db] Aplicando coordenadas: {archivo}")
            try:
                conn.executescript(ruta.read_text(encoding="utf-8"))
            except sqlite3.IntegrityError as exc:
                print(f"[init_db] AVISO: {archivo} ya estaba cargado ({exc})")
            continue

        if archivo == "01_seed.sql" and alias_count > 0:
            print(f"[init_db] Saltando {archivo} (lugares_alias ya tiene {alias_count} filas)")
            continue

        if archivo == "02_info_lugares.sql" and info_count > 0:
            print(f"[init_db] Saltando {archivo} (lugares_info ya tiene {info_count} filas)")
            continue

        if archivo == "03_establecimientos_cercanos.sql" and est_count > 0:
            print(f"[init_db] Saltando {archivo} (establecimientos_cercanos ya tiene {est_count} filas)")
            continue

        print(f"[init_db] Cargando datos: {archivo}")
        try:
            conn.executescript(ruta.read_text(encoding="utf-8"))
        except sqlite3.IntegrityError as exc:
            print(f"[init_db] AVISO: {archivo} ya estaba cargado ({exc})")

    conn.commit()
    conn.close()
    print(f"[init_db] Base de datos lista en: {DB_PATH}")


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    inicializar(reset=reset)
