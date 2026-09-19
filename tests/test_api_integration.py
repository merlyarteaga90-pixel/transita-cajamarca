import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.database import SessionLocal
from backend.main import app


class ApiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
        except Exception as exc:
            raise unittest.SkipTest(f"SQLite no disponible: {exc}")
        finally:
            db.close()
        cls.client = TestClient(app)

    def setUp(self):
        self.gemini_gen_patch = patch(
            "backend.services.respuesta_generator.generate_natural_response",
            return_value=None,
        )
        self.gemini_gen_patch.start()
        self.addCleanup(self.gemini_gen_patch.stop)

    def consultar_sin_gemini(self, consulta):
        with patch(
            "backend.services.intent_classifier._clasificar_con_gemini",
            side_effect=AssertionError("Una consulta clara no debe usar Gemini"),
        ):
            return self.client.post("/api/consultar", json={"consulta": consulta})

    def test_route_family_returns_all_variants(self):
        respuesta = self.consultar_sin_gemini("Horario de la ruta 03")
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(datos["tipo"], "info")
        self.assertEqual(
            [ruta["codigo_ruta"] for ruta in datos["resultados"]],
            ["R-03-1", "R-03-2"],
        )

    def test_exact_variant_returns_one_card(self):
        datos = self.consultar_sin_gemini("Horario de la ruta 03-1").json()
        self.assertEqual(len(datos["resultados"]), 1)
        self.assertEqual(datos["resultados"][0]["codigo_ruta"], "R-03-1")

    def test_routes_by_place_preserves_directions(self):
        datos = self.consultar_sin_gemini("¿Qué rutas pasan por Shudal?").json()
        self.assertEqual(datos["tipo"], "rutas_por_lugar")
        sentidos = {
            ruta["sentido"]
            for ruta in datos["resultados"]
            if ruta["codigo_ruta"] == "R-05"
        }
        self.assertEqual(sentidos, {"IDA", "VUELTA"})
        self.assertTrue(all("nombre_comercial" in r for r in datos["resultados"]))

    def test_direct_route(self):
        datos = self.consultar_sin_gemini(
            "Estoy en Shudal y quiero ir a Hoyos Rubio"
        ).json()
        self.assertEqual(datos["tipo"], "ruta")
        self.assertGreaterEqual(len(datos["resultados"]), 1)

    def test_informal_references_are_understood(self):
        datos = self.consultar_sin_gemini(
            "como voy de el milagro a los baños del inca"
        ).json()
        self.assertIn(datos["tipo"], {"ruta", "sin_resultados", "aclaracion"})

    def test_more_informal_references_are_understood(self):
        consultas = [
            "shuda shudal a hoyos rubio",
            "estoy x manco capa y voy pa la chimba",
        ]
        for consulta in consultas:
            with self.subTest(consulta=consulta):
                datos = self.consultar_sin_gemini(consulta).json()
                self.assertIn(datos["tipo"], {"ruta", "alternativas", "sin_resultados"})

    def test_informal_routes_by_place(self):
        datos = self.consultar_sin_gemini(
            "q rutas pasan x hoyos rubios"
        ).json()
        self.assertEqual(datos["tipo"], "rutas_por_lugar")
        self.assertGreaterEqual(len(datos["resultados"]), 1)

    def test_destination_only_requests_origin(self):
        datos = self.consultar_sin_gemini(
            "Quiero ir a las pozas termales"
        ).json()
        self.assertIn(datos["tipo"], {"aclaracion", "alternativas"})
        self.assertEqual(datos["estado"], "Falta el origen")
        self.assertEqual(datos["contexto"]["pendiente"], "origen")

    def test_destination_only_can_show_alternatives(self):
        datos = self.consultar_sin_gemini("como voy a shudal").json()
        self.assertEqual(datos["tipo"], "alternativas")
        self.assertEqual(datos["estado"], "Falta el origen")
        self.assertGreaterEqual(len(datos["resultados"]), 1)
        self.assertEqual(datos["contexto"]["destino"], "C.P. SHUDAL")
        self.assertEqual(datos["contexto"]["pendiente"], "origen")

    def test_natural_destination_query_does_not_use_rutas_as_origin(self):
        datos = self.consultar_sin_gemini("rutas para ir a shudal").json()
        self.assertEqual(datos["tipo"], "alternativas")
        self.assertNotIn("origen 'rutas'", datos["respuesta"].lower())

    def test_no_direct_route_returns_destination_alternatives(self):
        datos = self.consultar_sin_gemini("de shudal al hospital").json()
        self.assertIn(datos["tipo"], {"alternativas", "aclaracion"})
        if datos["tipo"] == "aclaracion":
            self.assertGreaterEqual(len(datos.get("candidatos", [])), 1)
        else:
            self.assertEqual(datos["estado"], "Sin ruta directa")
            self.assertGreaterEqual(len(datos["resultados"]), 1)

    def test_context_completes_missing_origin(self):
        primera = self.consultar_sin_gemini("quiero ir al hospital").json()
        segunda = self.client.post(
            "/api/consultar",
            json={"consulta": "desde shudal", "contexto": primera["contexto"]},
        ).json()
        self.assertNotEqual(segunda["estado"], "Falta el origen")
        self.assertIn(segunda["tipo"], {"ruta", "alternativas", "sin_resultados"})

    def test_vague_trip_requests_both_places(self):
        datos = self.consultar_sin_gemini("Quiero ir").json()
        self.assertEqual(datos["tipo"], "aclaracion")
        self.assertEqual(datos["estado"], "Datos incompletos")

    def test_tariff_and_frequency_are_deterministic(self):
        casos = [
            ("cuanto cuesta la ruta 04", "TARIFA", "R-04"),
            ("frecuencia de la ruta 05", "FRECUENCIA", "R-05"),
        ]
        for consulta, intencion, codigo in casos:
            with self.subTest(consulta=consulta):
                datos = self.consultar_sin_gemini(consulta).json()
                self.assertEqual(datos["tipo"], "info")
                self.assertEqual(datos["intencion_solicitada"], intencion)
                self.assertEqual(datos["resultados"][0]["codigo_ruta"], codigo)

    def test_general_route_code_returns_next_unit_info(self):
        casos = [
            "cual es la ruta 05",
            "dime la ruta 05",
            "ruta 05",
            "informacion de la ruta 05",
        ]
        for consulta in casos:
            with self.subTest(consulta=consulta):
                datos = self.consultar_sin_gemini(consulta).json()
                self.assertEqual(datos["tipo"], "info")
                self.assertEqual(datos["intencion_solicitada"], "PROXIMA_UNIDAD")
                self.assertEqual(datos["resultados"][0]["codigo_ruta"], "R-05")

    def test_incomplete_route_info_does_not_list_all_routes(self):
        casos = [
            ("cual es la tarifa", "TARIFA"),
            ("dime la tarifa", "TARIFA"),
            ("horario", "HORARIO"),
            ("frecuencia", "FRECUENCIA"),
        ]
        for consulta, intencion in casos:
            with self.subTest(consulta=consulta):
                datos = self.consultar_sin_gemini(consulta).json()
                self.assertEqual(datos["tipo"], "aclaracion")
                self.assertEqual(datos["estado"], "Indica una ruta")
                self.assertEqual(datos["intencion_solicitada"], intencion)
                self.assertEqual(datos["resultados"], [])
                self.assertEqual(datos["rutas"], [])

    def test_numeric_explicit_route_code_is_accepted(self):
        respuesta = self.client.post(
            "/api/consultar",
            json={
                "consulta": "horario",
                "intencion": "HORARIO",
                "ruta_codigo": 5,
            },
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["resultados"][0]["codigo_ruta"], "R-05")

    def test_next_unit_endpoint_uses_service_state(self):
        respuesta = self.client.post(
            "/api/proxima-unidad", json={"ruta_codigo": "R05"}
        )
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(datos["codigo_ruta"], "R-05")
        self.assertIn(
            datos["estado_servicio"],
            {
                "ANTES_DE_INICIO",
                "SERVICIO_ACTIVO",
                "SERVICIO_FINALIZADO",
                "SIN_MAS_SALIDAS",
                "DATOS_INSUFICIENTES",
            },
        )

    def test_unknown_free_text_degrades_without_ollama(self):
        with patch(
            "backend.services.intent_classifier._clasificar_con_gemini",
            side_effect=ConnectionError,
        ):
            datos = self.client.post(
                "/api/consultar", json={"consulta": "ando perdido compadre"}
            ).json()
        self.assertEqual(datos["tipo"], "aclaracion")

    def test_ambiguous_place_lists_candidates(self):
        datos = self.consultar_sin_gemini(
            "¿Qué rutas pasan por Plaza de Armas?"
        ).json()
        self.assertEqual(datos["tipo"], "aclaracion")
        self.assertGreaterEqual(len(datos["candidatos"]), 2)

    def test_null_query_returns_validation_error(self):
        respuesta = self.client.post("/api/consultar", json={"consulta": None})
        self.assertEqual(respuesta.status_code, 422)

    def test_non_object_body_returns_validation_error(self):
        respuesta = self.client.post("/api/consultar", json=[])
        self.assertEqual(respuesta.status_code, 422)

    def test_health_reports_loaded_data(self):
        datos = self.client.get("/api/health").json()
        self.assertEqual(datos["status"], "ok")
        self.assertGreater(datos["rutas"], 0)
        self.assertIn(datos["gemini"], {"configurado", "no_configurado"})
        self.assertGreater(datos["lugares_info"], 0)
        self.assertGreater(datos["establecimientos"], 0)

    def test_info_lugar_returns_description(self):
        datos = self.client.post(
            "/api/consultar",
            json={"consulta": "qué es la catedral", "intencion": "INFO_LUGAR"},
        ).json()
        self.assertEqual(datos["tipo"], "info_lugar")
        self.assertIn("Catedral", datos["resultados"][0]["nombre_oficial"])
        self.assertGreater(len(datos["resultados"][0]["descripcion"]), 20)

    def test_lugares_cercanos_returns_list(self):
        datos = self.client.post(
            "/api/consultar",
            json={"consulta": "qué hay cerca del mercado central",
                  "intencion": "LUGARES_CERCANOS"},
        ).json()
        self.assertEqual(datos["tipo"], "lugares_cercanos")
        self.assertGreater(len(datos["resultados"]), 0)

    def test_intencion_vaga_returns_suggestion(self):
        datos = self.client.post(
            "/api/consultar",
            json={"consulta": "quiero ir al médico", "intencion": "INTENCION_VAGA"},
        ).json()
        self.assertEqual(datos["tipo"], "aclaracion")
        self.assertGreater(len(datos["respuesta"]), 20)

    def test_fuera_de_alcance_polite_response(self):
        datos = self.client.post(
            "/api/consultar",
            json={"consulta": "qué hora es en tokio", "intencion": "FUERA_DE_ALCANCE"},
        ).json()
        self.assertEqual(datos["tipo"], "aclaracion")
        self.assertIn("Cajamarca", datos["respuesta"])

    def test_session_id_returned_in_response(self):
        datos = self.client.post(
            "/api/consultar",
            json={"consulta": "hola", "intencion": "SALUDO"},
        ).json()
        self.assertIn("session_id", datos)
        self.assertGreater(len(datos["session_id"]), 8)

    def test_explicit_intencion_is_used(self):
        datos = self.client.post(
            "/api/consultar",
            json={"consulta": "ignorar este texto",
                  "intencion": "INFO_LUGAR",
                  "destino": "mercado central"},
        ).json()
        self.assertEqual(datos["tipo"], "info_lugar")
        self.assertEqual(datos["intencion_solicitada"], "INFO_LUGAR")

    def test_despedida_chau(self):
        datos = self.consultar_sin_gemini("chau").json()
        self.assertEqual(datos["tipo"], "despedida")

    def test_despedida_adios(self):
        datos = self.consultar_sin_gemini("adiós").json()
        self.assertEqual(datos["tipo"], "despedida")

    def test_despedida_gracias(self):
        datos = self.consultar_sin_gemini("gracias").json()
        self.assertEqual(datos["tipo"], "despedida")

    def test_despedida_hasta_luego(self):
        datos = self.consultar_sin_gemini("hasta luego").json()
        self.assertEqual(datos["tipo"], "despedida")

    def test_saludo_hola(self):
        datos = self.consultar_sin_gemini("hola").json()
        self.assertEqual(datos["tipo"], "saludo")

    def test_saludo_buenas(self):
        datos = self.consultar_sin_gemini("buenas").json()
        self.assertEqual(datos["tipo"], "saludo")


if __name__ == "__main__":
    unittest.main()
