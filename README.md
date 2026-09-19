# Asistente de Rutas de Cajamarca

Aplicación local con FastAPI, SQLite, frontend React y Gemini API. Las consultas frecuentes se interpretan con reglas deterministas y Gemini se usa para clasificar frases no reconocidas y generar respuestas naturales.

El frontend está construido con React 18 + Vite y se sirve desde FastAPI usando el build generado en `frontend/dist`.

## Funciones actuales

- Búsqueda de rutas directas entre dos referencias.
- Tolerancia a alias, tildes, abreviaturas y errores comunes.
- Listado de todas las rutas y sentidos que pasan por un lugar.
- Información descriptiva de lugares turísticos, educativos, religiosos, de salud y comerciales.
- Establecimientos cercanos (bancos, restaurantes, farmacias) por lugar de referencia.
- Horarios, frecuencias, tarifas y salida teórica por ruta.
- Familias de ruta: `ruta 03` devuelve `R-03-1` y `R-03-2`.
- Clasificación de intención vía Gemini (con parser determinista de fallback).
- Respuestas naturales verificadas generadas por Gemini a partir de datos SQL.
- Sugerencias ante consultas vagas (deterministas).
- Manejo de "fuera de alcance" para consultas no relacionadas.
- Contexto conversacional (4-5 turnos).
- Lista de candidatos cuando un lugar es ambiguo.
- Funcionamiento principal aunque Gemini no esté configurado.

SQLite es la única fuente de rutas y datos operativos. IDA y VUELTA se procesan como recorridos independientes. Solo se buscan rutas directas; no hay transbordos todavía.

## Requisitos

- Python 3.12 recomendado.
- SQLite (archivo local `transita_cajamarca.db`).
- Gemini API key (gratuita para desarrollo en Google AI Studio).

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

Copia `.env.example` como `.env` y añade tu clave:

```dotenv
DB_PATH=transita_cajamarca.db
GEMINI_API_KEY=tu_clave_aqui
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_TIMEOUT_SECONDS=8
```

## Base de datos

Inicializar y cargar datos (crea la base si no existe):

```powershell
python -m backend.init_db
python -m backend.init_db --reset
```

Carga en orden: `database/00_schema.sql`, `01_seed.sql`, `02_info_lugares.sql`, `03_establecimientos_cercanos.sql`.
El flag `--reset` elimina el archivo de DB antes de cargar.

## Iniciar la aplicación

Si modificaste el frontend o no existe `frontend/dist`, genera el build:

```powershell
cd frontend
npm install
npm run build
cd ..
```

Luego inicia FastAPI:

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

Las pruebas no requieren Gemini activo.

## Interpretación de datos

- `tiempo_total_ruta_min` y `distancia_total_ruta_km` corresponden al recorrido completo del sentido, no al segmento solicitado.
- La próxima salida es teórica y se calcula desde el inicio de la ruta según horario y frecuencia.
- Los puntos del itinerario no se presentan como paraderos confirmados.
- Si hay varias rutas o variantes válidas, se muestran todas.
