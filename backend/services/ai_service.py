import json
from backend.services.ollama_client import get_client, get_model


INTENCIONES_PERMITIDAS = [
    "SALUDO",
    "BUSCAR_RUTA",
    "RUTAS_POR_LUGAR",
    "PROXIMA_UNIDAD",
    "HORARIO",
    "FRECUENCIA",
    "TARIFA",
]


def analizar_consulta(mensaje: str):
    """
    Analiza la consulta del usuario usando Ollama.

    Ollama interpreta:
    - intención
    - origen
    - destino
    - ruta_codigo

    Ollama NO decide qué ruta existe. MySQL es la fuente de verdad.
    """

    prompt = f"""
Analiza esta consulta de transporte público de Cajamarca.

Devuelve únicamente un objeto JSON válido.

La estructura EXACTA es:

{{
    "intencion": "BUSCAR_RUTA",
    "origen": null,
    "destino": null,
    "ruta_codigo": null
}}

Las únicas intenciones permitidas son:

SALUDO
BUSCAR_RUTA
RUTAS_POR_LUGAR
PROXIMA_UNIDAD
HORARIO
FRECUENCIA
TARIFA

REGLAS POR INTENCIÓN:

SALUDO:
Solo cuando el usuario saluda, se despide o hace una cortesía
y NO expresa intención de viajar ni pide información:
"hola", "buenos días", "gracias", "hasta luego".

"Quiero ir" NO es saludo: expresa intención de viajar.

BUSCAR_RUTA:
Cuando la persona quiere ir de un lugar a otro.
Requiere origen y destino cuando ambos estén mencionados.

Si quiere viajar pero NO menciona ningún lugar,
igual usa BUSCAR_RUTA con origen y destino en null:

"Quiero ir" →
{{
    "intencion": "BUSCAR_RUTA",
    "origen": null,
    "destino": null,
    "ruta_codigo": null
}}

Ejemplos:
"Estoy en Shudal y quiero ir a Hoyos Rubio" →
{{
    "intencion": "BUSCAR_RUTA",
    "origen": "shudal",
    "destino": "hoyos rubio",
    "ruta_codigo": null
}}

"Quiero ir a la Plaza de Armas de Baños del Inca" →
{{
    "intencion": "BUSCAR_RUTA",
    "origen": null,
    "destino": "plaza de armas de baños del inca",
    "ruta_codigo": null
}}

"Quiero ir al hospital" →
{{
    "intencion": "BUSCAR_RUTA",
    "origen": null,
    "destino": "hospital",
    "ruta_codigo": null
}}

"Rutas para ir a Shudal" →
{{
    "intencion": "BUSCAR_RUTA",
    "origen": null,
    "destino": "shudal",
    "ruta_codigo": null
}}

"Qué combi me lleva al hospital" →
{{
    "intencion": "BUSCAR_RUTA",
    "origen": null,
    "destino": "hospital",
    "ruta_codigo": null
}}

RUTAS_POR_LUGAR:
Cuando pregunta qué rutas pasan por un lugar.
El lugar puede ser un nombre coloquial: cópialo tal cual
aparece en la consulta y colócalo en "destino".

"¿Qué rutas pasan por Hoyos Rubio?" →
{{
    "intencion": "RUTAS_POR_LUGAR",
    "origen": null,
    "destino": "hoyos rubio",
    "ruta_codigo": null
}}

"¿Qué rutas pasan por Shudal?" →
{{
    "intencion": "RUTAS_POR_LUGAR",
    "origen": null,
    "destino": "shudal",
    "ruta_codigo": null
}}

PROXIMA_UNIDAD:
Cuando pregunta por la próxima unidad o combi.
Si menciona un número de ruta, colócalo en ruta_codigo.
También usa PROXIMA_UNIDAD cuando el usuario pide información general
de una ruta por código sin pedir horario, frecuencia o tarifa específica.

Ejemplos:
"Cuál es la ruta 05" →
{{
    "intencion": "PROXIMA_UNIDAD",
    "origen": null,
    "destino": null,
    "ruta_codigo": "05"
}}

"Información de la ruta 05" →
{{
    "intencion": "PROXIMA_UNIDAD",
    "origen": null,
    "destino": null,
    "ruta_codigo": "05"
}}

HORARIO:
Cuando pregunta a qué hora opera una ruta.

FRECUENCIA:
Cuando pregunta cada cuánto pasa una unidad.

TARIFA:
Cuando pregunta cuánto cuesta el pasaje.

REGLAS PARA EXTRAER LUGARES (MUY IMPORTANTES):

Copia el texto del lugar EXACTAMENTE como aparece escrito
en la consulta del usuario.

NO traduzcas, NO completes, NO abrevies, NO corrige nombres.

Si el lugar tiene varias palabras, copia la frase completa:

"la Plaza de Armas de Baños del Inca"
→ "plaza de armas de baños del inca"

NO lo cortes a "plaza" ni a "baños del inca".

Puedes eliminar únicamente las palabras de conexión que
rodean al lugar, como:
"estoy en", "quiero ir a", "ir a", "hasta", "hacia",
"desde", "de", "a", "al", "a la", "a los", "a las", "por"

Ejemplos:
"Estoy en Shudal y quiero ir a Baños del Inca"
→ origen: "shudal", destino: "baños del inca"

"Necesito ir desde C.P. Shudal hasta Av. Manco Cápac"
→ origen: "cp shudal", destino: "av manco capac"

"Cómo llego a la plaza de armas de baños del inca"
→ destino: "plaza de armas de baños del inca"

"Estoy en el sector La Esperanza Baños y quiero ir a Hoyos Rubio"
→ origen: "sector la esperanza baños", destino: "hoyos rubio"

PROHIBIDO:
- Inventar lugares que no aparecen en la consulta.
- Completar con lugares conocidos si el usuario no los mencionó.
- Si la consulta no menciona origen, origen debe ser null.
- Si la consulta no menciona destino, destino debe ser null.
- Si la consulta es vaga ("quiero ir", "cómo llego" sin lugar),
  origen y destino deben ser null.

Convierte origen y destino a minúsculas.

Si se menciona un número de ruta, colócalo en ruta_codigo
(sin el prefijo "R-", solo el número o como aparezca).

CONSULTA DEL USUARIO:

{mensaje}
"""

    ultimo_error = None

    for intento in range(1):
        try:
            client = get_client()
            model = get_model()

            respuesta = client.chat(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un analizador de consultas. "
                            "Devuelve únicamente JSON válido. "
                            "No inventes información."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                format="json",
                options={
                    "temperature": 0
                }
            )

            contenido = respuesta["message"]["content"].strip()
            datos = json.loads(contenido)

            intencion = datos.get("intencion")

            if intencion not in INTENCIONES_PERMITIDAS:
                raise ValueError(f"Intención no válida: {intencion}")

            origen = datos.get("origen")
            destino = datos.get("destino")
            ruta_codigo = datos.get("ruta_codigo")

            if isinstance(origen, str):
                origen = origen.strip().lower()
                if not origen:
                    origen = None

            if isinstance(destino, str):
                destino = destino.strip().lower()
                if not destino:
                    destino = None

            if ruta_codigo is not None:
                ruta_codigo = str(ruta_codigo).strip()
                if not ruta_codigo:
                    ruta_codigo = None

            return {
                "intencion": intencion,
                "origen": origen,
                "destino": destino,
                "ruta_codigo": ruta_codigo
            }

        except Exception as e:
            ultimo_error = e

    raise ValueError(
        "No se pudo interpretar la consulta. "
        f"Último error: {ultimo_error}"
    )
