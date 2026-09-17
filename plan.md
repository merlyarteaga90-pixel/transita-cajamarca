# Estado Y Plan Del Asistente De Rutas

## Hito Actual

La aplicación alcanzó una línea base funcional y comprobable:

- FastAPI valida entradas con Pydantic.
- MySQL es la única fuente de rutas, sentidos, horarios, frecuencias y tarifas.
- El parser determinista resuelve primero las consultas frecuentes.
- Ollama es un respaldo opcional con timeout de 4 segundos, no un requisito para el flujo principal.
- El frontend Svelte tiene cards específicas para recorridos, rutas por lugar, información y familias de rutas.
- Los lugares ambiguos muestran únicamente una lista de candidatos.
- Hay 24 pruebas automatizadas de servicios e integración.

Comando de pruebas:

```powershell
& ".venv\Scripts\python.exe" -m unittest discover -s tests -v
```

## Flujo Vigente

```text
Consulta
  -> parser determinista
  -> Ollama solo si el parser no reconoce la frase
  -> resolución de alias y coincidencia aproximada
  -> búsqueda de todas las opciones directas en MySQL
  -> respuesta estructurada
  -> cards del frontend
```

La redacción de recorridos es determinista. Ya no se hace una segunda llamada a Ollama después de buscar rutas.

## Decisiones Confirmadas

- Mostrar todas las rutas válidas.
- Conservar IDA y VUELTA como opciones distintas.
- `ruta 03` representa una familia y muestra `R-03-1` y `R-03-2`.
- Un código exacto como `03-1` muestra solo `R-03-1`.
- Aceptar formatos `5`, `R05`, `R-05`, `3.1`, `R03-1` y `Ruta 03 (1)`.
- Tolerar entradas como `shuda shudal`, `manco capa` y artículos como `los baños del inca`.
- Si varias referencias significan la misma zona, combinar sus rutas y deduplicar por código y sentido.
- Si una referencia puede significar lugares distintos, listar candidatos y pedir el nombre completo.
- No usar botones ni memoria conversacional para candidatos ambiguos.
- Mantener solo rutas directas por ahora.
- No inventar frecuencias cuando faltan datos.
- Presentar próxima unidad como salida teórica desde el inicio de la ruta.

## Contrato De Respuesta

`POST /api/consultar` usa una envoltura común:

```json
{
  "estado": "...",
  "icono": "🚌",
  "tipo": "ruta",
  "respuesta": "...",
  "resultados": [],
  "candidatos": [],
  "rutas": []
}
```

Tipos vigentes:

- `ruta`: opciones directas con recorrido.
- `rutas_por_lugar`: una card por código y sentido.
- `info`: horario, frecuencia, tarifa o salida teórica; admite varias variantes.
- `selector_ruta`: listado informativo cuando falta código.
- `aclaracion`: datos faltantes, referencia desconocida o candidatos ambiguos.
- `sin_resultados`: lugares válidos sin una ruta directa.
- `saludo` y `error`.

## Archivos Principales

- `backend/main.py`: endpoints y orquestación.
- `backend/schemas.py`: validación de solicitudes y respuestas.
- `backend/services/query_parser.py`: interpretación determinista.
- `backend/services/route_code_service.py`: códigos y familias.
- `backend/services/reference_service.py`: alias y coincidencia aproximada.
- `backend/services/route_engine.py`: búsqueda de rutas y sentidos.
- `backend/services/schedule_service.py`: cálculo de salida teórica con zona `America/Lima`.
- `frontend/src/`: componentes Svelte, cliente API, estado de consulta y utilidades de voz/formato.
- `frontend/style.css`: estilos compartidos de la interfaz.
- `tests/`: pruebas permanentes.

## Datos Actuales

- 28 empresas.
- 52 rutas.
- 104 sentidos.
- 419 puntos.
- 504 alias activos.

Limitaciones confirmadas en los datos:

- Solo `R-05` pasa por C.P. SHUDAL.
- `R-05` no conecta directamente Shudal con los puntos registrados de Baños del Inca.
- Tiempo y distancia disponibles son totales del sentido, no estimaciones del tramo consultado.
- Los puntos del itinerario son referencias viales; no son paraderos certificados.

## Próximas Decisiones De Producto

Estas decisiones se posponen hasta validar la línea base en la interfaz:

1. Búsqueda con transbordos.
2. Alias oficial para `centro`.
3. Ubicación GPS del usuario.
4. Contexto conversacional entre mensajes.
5. Recomendación u ordenamiento de rutas por tiempo, cercanía o tarifa.
6. Tiempos y distancias reales por segmento.
7. Calendarios distintos por día o feriado.

## Criterio Para Continuar

Antes de ampliar funciones, verificar manualmente:

- Cards de `Horario de la ruta 03` para ambas variantes.
- Cards con todos los sentidos de `¿Qué rutas pasan por Shudal?`.
- Búsqueda directa `Shudal -> Hoyos Rubio`.
- Frases informales y con errores.
- Candidatos de `Plaza de Armas`.
- Ollama apagado sin bloquear consultas claras.
- Ausencia de `Ruta 41`, `undefined`, `null` y `NaN` en la interfaz.
