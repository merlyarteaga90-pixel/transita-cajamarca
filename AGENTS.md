# AGENTS.md

Contexto para AI agents y contribuidores humanos. Aquí vive lo que necesitás
saber para no romper el proyecto ni repetir decisiones ya tomadas.

## Proyecto

"Asistente de Rutas de Cajamarca" — backend FastAPI + frontend React + SQLite
+ Gemini API (opcional). Responde consultas en español sobre transporte público de
Cajamarca, Perú.

## Comandos clave

```bash
# Backend: inicializar / resetear la base de datos
python -m backend.init_db            # crea si no existe, salta lo ya cargado
python -m backend.init_db --reset    # borra el .db y recarga todo

# Backend: tests (35 pruebas, todas pasan sin Gemini)
python -m unittest tests.test_api_integration -v

# Backend: arrancar servidor de desarrollo
python -m backend.main               # http://127.0.0.1:8000

# Frontend: instalar dependencias y construir
cd frontend
npm install
npm run dev      # dev server con proxy a /api -> 127.0.0.1:8000
npm run build    # genera frontend/dist que sirve FastAPI
npm run type-check
```

## Arquitectura (resumen)

```
backend/
  main.py                    FastAPI app, endpoints
  schemas.py                 Pydantic, tipos Intencion, UserLocation
  database.py                SQLAlchemy engine sobre SQLite
  init_db.py                 Carga los SQL de database/
  prompts/
    intent_classifier.txt    Prompt corto (~120 líneas) para Gemini
    respuesta_generator.txt  Prompt para resumir rutas en lenguaje natural
  services/
    assistant_service.py      Orquestador: clasifica -> contexto -> handler -> prosa
    intent_classifier.py     Parser determinista -> Gemini -> INTENCION_VAGA
    gemini_client.py         Cliente singleton para Gemini
    respuesta_generator.py   Genera prosa natural desde resultados SQL
    vaga_clarifier.py       Aclaraciones deterministas para consultas vagas
    query_parser.py          Regex para frases frecuentes (sin IA)
    reference_service.py     Resuelve alias coloquiales -> ubicaciones oficiales
    route_engine.py          Búsquedas SQL: rutas, sentidos, puntos
    route_code_service.py    Normaliza "R05", "ruta 05", "03-1" -> "R-5", "R-3-1"
    schedule_service.py      Cálculo de próxima unidad (timezone America/Lima)
    respuesta_service.py     Generador de respuesta de texto para rutas
    handlers/                Un módulo por intención (ver más abajo)
database/
  00_schema.sql              Empresas, rutas, sentidos, puntos, alias, lugares_info, establecimientos_cercanos
  01_seed.sql                Datos de rutas y aliases
  02_info_lugares.sql        Descripciones de lugares para INFO_LUGAR
  03_establecimientos_cercanos.sql  Negocios/establecimientos por lugar
frontend/                    React 18 + Vite + TypeScript + CSS Modules
tests/
  test_api_integration.py    35 tests, todos pasan sin Gemini
```

## Flujo de una consulta

1. Frontend hace `POST /api/consultar`.
2. `assistant_service.consultar` clasifica la intención:
   - Parser determinista primero (rápido, cubre frases frecuentes).
   - Gemini como primary cuando el parser no reconoce.
   - Fallback a `INTENCION_VAGA` si Gemini no está disponible.
3. Se aplica contexto conversacional (slots `origen`/`destino`).
4. Se despacha al handler correspondiente.
5. Handler consulta SQLite y devuelve dict con `tipo`, `respuesta`, `resultados`.
6. Para rutas con resultados, Gemini reescribe `respuesta` en lenguaje
   natural usando únicamente esos datos. Si falla, se conserva la plantilla.
7. Para `INTENCION_VAGA`, se genera una pregunta determinista de aclaración.

**Importante:** Gemini NO es fallback — es el clasificador primary.
El parser determinista es el fast-path. Si Gemini no está configurado, las frases
frecuentes siguen funcionando porque el parser las cubre.

## Intenciones soportadas

| Intención | Handler | Descripción |
|-----------|---------|-------------|
| `SALUDO` | `handlers/saludo.py` | Hola/buenas |
| `DESPEDIDA` | `handlers/saludo.py` | Chau/gracias/hasta luego |
| `BUSCAR_RUTA` | `handlers/buscar_ruta.py` | De origen a destino |
| `RUTAS_POR_LUGAR` | `handlers/rutas_por_lugar.py` | Qué rutas pasan por X |
| `QUE_RUTA_PASA_CERCA` | `handlers/rutas_por_lugar.py` | Usa `user_location` (Haversine) |
| `INFO_LUGAR` | `handlers/info_lugar.py` | Descripción de lugar |
| `LUGARES_CERCANOS` | `handlers/lugares_cercanos.py` | Negocios cerca de X |
| `INTENCION_VAGA` | `handlers/vaga.py` | Consulta ambigua, pide detalles |
| `HORARIO` / `FRECUENCIA` / `TARIFA` / `PROXIMA_UNIDAD` | `handlers/info_ruta.py` | Info de ruta por código |
| `FUERA_DE_ALCANCE` | `assistant_service.py` | No relacionado a transporte |

## Convenciones

### Imports
- Estilo: `from backend.services.X import Y` (NO `from services.X`).
- En `backend/services/handlers/*.py` también va con prefijo `backend.services.handlers.X`.

### Tipos de respuesta
- `tipo` es uno de los `Literal` en `backend/schemas.py:RespuestaAPI`.
- Nuevos tipos requieren actualizar el Literal y posiblemente el frontend.

### Path del proyecto
- `RAIZ_PROYECTO` se agrega a `sys.path` desde `main.py` (ver línea 8).
- Los tests también lo requieren (ya está configurado).

### Base de datos
- SQLite, `transita_cajamarca.db` por defecto (configurable vía `DB_PATH`).
- Las tablas nuevas se agregan en `database/00_schema.sql` con `IF NOT EXISTS`.
- Datos en archivos separados: `01_seed.sql` (rutas+aliases), `02_info_lugares.sql`, `03_establecimientos_cercanos.sql`.
- `init_db` detecta si cada tabla ya tiene filas y salta el archivo si es así.
- Para cambios estructurales, usar `init_db --reset`.

### Aliases coloquiales
- Tabla `lugares_alias`: `(referencia_original, referencia_normalizada, ubicacion_oficial, ubicacion_normalizada, activo)`.
- Un mismo `referencia_normalizada` puede mapear a varias `ubicacion_oficial` (ej: "baños del inca" → 2 lugares). Eso causa `AMBIGUO`.
- Para agregar aliases, editar `database/01_seed.sql` y correr `init_db --reset`.

### Frontend
- React 18 + Vite + TypeScript + CSS Modules. NO Tailwind, NO UI libraries.
- Tipos canónicos en `frontend/src/api/types.ts`.
- Cliente API en `frontend/src/api/client.ts`.
- Hooks personalizados en `frontend/src/hooks/`.

## Lo que NO hacer

- **No usar Svelte** — el proyecto migró a React. No hay `frontend/src/*.svelte`.
- **No committear `frontend/dist/`** — está en `.gitignore` eventualmente, hoy se regenera con `npm run build`.
- **No usar MySQL** — SQLite es la única fuente.
- **No usar `pymysql` ni `openpyxl`** — dependencias eliminadas en requirements.txt.
- **No llamar Gemini desde el frontend** — siempre vía backend.
- **No agregar system prompt gigante en el código** — vive en `backend/prompts/*.txt`.
- **No inventar datos en respuestas** — si no hay ruta directa, decir "sin ruta directa"; no rellenar.

## Estado actual (resumen)

- 28 empresas, 52 rutas, 104 sentidos, 419 puntos, **620 aliases** activos.
- 38 lugares con descripción (`lugares_info`).
- 30 establecimientos cercanos (`establecimientos_cercanos`).
- 35 tests pasan en ~0.5s sin Gemini.
- Gemini API con `gemini-3.5-flash-lite` es el modelo por defecto.
- `GEMINI_MODEL` permite probar otros modelos; modelo debe soportar `generateContent`.

## Datos cargados

Para re-inicializar la base después de cambios:

```bash
python -m backend.init_db --reset
```

Esto borra `transita_cajamarca.db` y carga los 4 SQL en orden.

## Limitaciones conocidas (no son bugs)

- Solo rutas directas — no hay transbordos.
- Tiempo/distancia son totales del sentido, no del tramo consultado.
- Puntos del itinerario son referencias viales, no paraderos certificados.
- "Próxima combi" es salida teórica desde el inicio de la ruta, no desde el paradero del usuario.
- Memoria conversacional: 4-5 turnos, no persistente entre sesiones.
- Sin GPS real del usuario en producción (la API funciona, falta integración en frontend para usarla activa).

## Endpoint contract

`POST /api/consultar`:

```json
Request:
{
  "consulta": "string (1-500)",
  "origen?": "string",
  "destino?": "string",
  "intencion?": "string (Intencion Literal)",
  "ruta_codigo?": "string | int",
  "contexto?": { "origen?": "...", "destino?": "...", "pendiente?": "origen|destino" },
  "user_location?": { "lat": float, "lon": float },
  "session_id?": "string"
}

Response:
{
  "estado": "string",
  "icono": "🚌",
  "tipo": "ruta|alternativas|rutas_por_lugar|info|info_lugar|lugares_cercanos|selector_ruta|aclaracion|sin_resultados|saludo|despedida|error",
  "resultados": [ ... ],
  "respuesta": "string",
  "candidatos?": [ "string" ],
  "rutas?": [ ... ],
  "contexto": { ... },
  "session_id": "string",
  "intencion_solicitada": "string"
}
```

## Agregar una nueva intención

1. Agregar el literal en `backend/schemas.py` (en `Intencion` y `RespuestaAPI.tipo` si aplica).
2. Documentar el patrón en `backend/prompts/intent_classifier.txt`.
3. (Opcional) Agregar patrón regex en `backend/services/query_parser.py` para cobertura determinista.
4. Crear `backend/services/handlers/<nombre>.py` con función `handle_<intencion>(db, params)`.
5. Registrar dispatch en `backend/services/assistant_service.py:_dispatch`.
6. Agregar test en `tests/test_api_integration.py`.
7. Si el frontend necesita renderizarlo, agregar tipo en `frontend/src/api/types.ts` y el caso en `frontend/src/components/ResponsePanel.tsx`.

## Agregar un nuevo alias o lugar

- Alias coloquial → INSERT en `database/01_seed.sql` + `init_db --reset`.
- Descripción de lugar → INSERT en `database/02_info_lugares.sql` + `init_db --reset`.
- Negocio cercano → INSERT en `database/03_establecimientos_cercanos.sql` + `init_db --reset`.
