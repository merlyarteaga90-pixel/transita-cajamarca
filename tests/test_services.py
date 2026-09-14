import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from backend.services.query_parser import interpretar_consulta_clara
from backend.services.route_code_service import normalizar_codigo_ruta
from backend.services.schedule_service import calcular_proxima_unidad


class QueryParserTests(unittest.TestCase):
    def test_route_family_query(self):
        resultado = interpretar_consulta_clara("Horario de la ruta 03")
        self.assertEqual(resultado["intencion"], "HORARIO")
        self.assertEqual(resultado["ruta_codigo"], "03")

    def test_informal_origin_and_destination(self):
        resultado = interpretar_consulta_clara(
            "estoy x manco capa y voy pa la chimba"
        )
        self.assertEqual(resultado["intencion"], "BUSCAR_RUTA")
        self.assertEqual(resultado["origen"], "manco capa")
        self.assertEqual(resultado["destino"], "la chimba")

    def test_routes_by_place_with_accent(self):
        resultado = interpretar_consulta_clara(
            "¿Qué rutas pasan por Av. Manco Cápac?"
        )
        self.assertEqual(resultado["intencion"], "RUTAS_POR_LUGAR")
        self.assertEqual(resultado["destino"], "Av. Manco Cápac")


class RouteCodeTests(unittest.TestCase):
    def test_supported_formats(self):
        casos = {
            "5": "R-05",
            "R05": "R-05",
            "ruta 05": "R-05",
            "03-1": "R-03-1",
            "3.1": "R-03-1",
            "Ruta 03 (1)": "R-03-1",
        }
        for entrada, esperado in casos.items():
            with self.subTest(entrada=entrada):
                self.assertEqual(normalizar_codigo_ruta(entrada), esperado)


class ScheduleTests(unittest.TestCase):
    def test_exact_service_start(self):
        ahora = datetime(2026, 9, 13, 6, 0, tzinfo=ZoneInfo("America/Lima"))
        resultado = calcular_proxima_unidad("06:00", "20:00", 7, ahora)
        self.assertEqual(resultado["estado"], "SERVICIO_ACTIVO")
        self.assertEqual(resultado["proxima_salida"], "06:00")
        self.assertEqual(resultado["minutos_restantes"], 0)

    def test_after_service(self):
        ahora = datetime(2026, 9, 13, 21, 0, tzinfo=ZoneInfo("America/Lima"))
        resultado = calcular_proxima_unidad("06:00", "20:00", 7, ahora)
        self.assertEqual(resultado["estado"], "SERVICIO_FINALIZADO")
        self.assertIsNone(resultado["minutos_restantes"])

    def test_missing_frequency_is_not_invented(self):
        resultado = calcular_proxima_unidad("06:00", "20:00", None)
        self.assertEqual(resultado["estado"], "DATOS_INSUFICIENTES")
        self.assertIsNone(resultado["frecuencia_min"])


if __name__ == "__main__":
    unittest.main()
