# Asistente de Rutas de Cajamarca

Aplicación local con FastAPI, MySQL y frontend web. Ollama es opcional: las consultas frecuentes se interpretan con reglas deterministas y el modelo se usa solo como respaldo para frases no reconocidas.

## Funciones actuales

- Búsqueda de rutas directas entre dos referencias.
- Tolerancia a alias, tildes, abreviaturas y errores comunes.
- Listado de todas las rutas y sentidos que pasan por un lugar.
- Horarios, frecuencias, tarifas y salida teórica por ruta.
- Familias de ruta: `ruta 03` devuelve `R-03-1` y `R-03-2`.
- Cards para recorridos, rutas por lugar e información de rutas.
- Lista de candidatos cuando un lugar es ambiguo.
- Funcionamiento principal aunque Ollama no esté disponible.

MySQL es la única fuente de rutas y datos operativos. IDA y VUELTA se procesan como recorridos independientes. Solo se buscan rutas directas; no hay transbordos todavía.

## Requisitos

- Python 3.12 recomendado.
- MySQL en `localhost:3306` con la base `asistente_rutas`.
- Ollama opcional con el modelo `llama3.2:3b`.

## Configuración

Desde PowerShell, en la raíz del proyecto:

```powershell
cd "<carpeta-del-proyecto>"
```

Si el entorno virtual aún no existe:

```powershell
py -3.12 -m venv .venv
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
```

Copia `.env.example` como `.env` y configura los datos de MySQL. La configuración actual esperada es:

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_NAME=asistente_rutas
DB_USER=root
DB_PASSWORD=
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TIMEOUT=4
```

## Base de datos

Aplicar los esquemas en orden:

1. `database/01_schema.sql`
2. `database/03_lugares_alias.sql`

Importadores disponibles:

```powershell
& ".venv\Scripts\python.exe" resources\importar_excel_v4.py
& ".venv\Scripts\python.exe" resources\importar_diccionario_alias.py
```

Los importadores usan por defecto los archivos versionados en `resources/` (`listado_rutas_cajamarca_2024.xlsx` y `lugares_alias.csv`). Limpian sus tablas antes de insertar: úsalos contra una base de respaldo si tienes datos propios.

## Ollama opcional

```powershell
ollama pull llama3.2:3b
ollama serve
```

Si Ollama está apagado, horarios, tarifas, frecuencias, rutas por lugar y búsquedas con estructuras claras continúan funcionando.

## Iniciar la aplicación

```powershell
& ".venv\Scripts\python.exe" -m backend.main
```

Abrir `http://127.0.0.1:8000`.

Para detenerla, presiona `Ctrl+C` en la misma terminal. Después de modificar Python, reinicia el servidor si no lo ejecutaste con recarga automática.

Modo de desarrollo:

```powershell
& ".venv\Scripts\python.exe" -m uvicorn backend.main:app --reload --port 8000
```

## Verificación

Estado general:

```text
http://127.0.0.1:8000/api/health
```

Pruebas automatizadas:

```powershell
& ".venv\Scripts\python.exe" -m unittest discover -s tests -v
```

Las pruebas de integración requieren MySQL, pero no requieren un servidor HTTP ni Ollama activos.

## Interpretación de datos

- `tiempo_total_ruta_min` y `distancia_total_ruta_km` corresponden al recorrido completo del sentido, no al segmento solicitado.
- La próxima salida es teórica y se calcula desde el inicio de la ruta según horario y frecuencia.
- Los puntos del itinerario no se presentan como paraderos confirmados.
- Si hay varias rutas o variantes válidas, se muestran todas.
