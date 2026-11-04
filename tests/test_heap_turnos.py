import tempfile
import unittest
from pathlib import Path

from src.banco import Banco
from src.heap_turnos import HeapTurnos


class TestHeapTurnos(unittest.TestCase):
    def test_prioriza_urgente_y_respeta_fifo_en_empates(self):
        turnos = HeapTurnos()
        turnos.encolar("normal-1")
        turnos.encolar("urgente-1", HeapTurnos.PRIORIDAD_URGENTE)
        turnos.encolar("urgente-2", HeapTurnos.PRIORIDAD_URGENTE)

        self.assertEqual(turnos.desencolar(), "urgente-1")
        self.assertEqual(turnos.desencolar(), "urgente-2")
        self.assertEqual(turnos.desencolar(), "normal-1")

    def test_prioridad_intermedia_va_antes_de_normal(self):
        turnos = HeapTurnos()
        turnos.encolar("normal")
        turnos.encolar("preferente", HeapTurnos.PRIORIDAD_PREFERENTE)

        self.assertEqual(turnos.frente(), "preferente")
        self.assertEqual(turnos.desencolar(), "preferente")
        self.assertEqual(turnos.desencolar(), "normal")

    def test_turno_normal_no_se_pospone_indefinidamente(self):
        turnos = HeapTurnos()
        turnos.encolar("normal")
        for numero in range(5):
            turnos.encolar(
                f"urgente-{numero}", HeapTurnos.PRIORIDAD_URGENTE
            )

        self.assertEqual(turnos.desencolar(), "urgente-0")
        self.assertEqual(turnos.desencolar(), "urgente-1")
        self.assertEqual(turnos.desencolar(), "urgente-2")
        self.assertEqual(turnos.desencolar(), "normal")

    def test_frente_coincide_con_el_siguiente_turno_por_equidad(self):
        turnos = HeapTurnos()
        turnos.encolar("normal")
        for numero in range(4):
            turnos.encolar(
                f"urgente-{numero}", HeapTurnos.PRIORIDAD_URGENTE
            )

        for numero in range(3):
            self.assertEqual(turnos.desencolar(), f"urgente-{numero}")
        self.assertEqual(turnos.frente(), "normal")
        self.assertEqual(turnos.desencolar(), "normal")

    def test_envejecimiento_promueve_turno_que_espera(self):
        ahora = [0]
        turnos = HeapTurnos(reloj=lambda: ahora[0])
        turnos.encolar("normal")
        turnos.encolar("urgente", HeapTurnos.PRIORIDAD_URGENTE)

        self.assertEqual(turnos.frente(), "urgente")
        ahora[0] = HeapTurnos.SEGUNDOS_POR_ENVEJECIMIENTO
        self.assertEqual(turnos.frente(), "urgente")
        ahora[0] = 2 * HeapTurnos.SEGUNDOS_POR_ENVEJECIMIENTO
        self.assertEqual(turnos.frente(), "normal")

    def test_envejecimiento_se_limita_a_prioridad_urgente(self):
        ahora = [0]
        turnos = HeapTurnos(reloj=lambda: ahora[0])
        turnos.encolar("urgente", HeapTurnos.PRIORIDAD_URGENTE)
        turnos.encolar("normal")
        ahora[0] = 3 * HeapTurnos.SEGUNDOS_POR_ENVEJECIMIENTO

        self.assertEqual(turnos.extraer_maximo(), "urgente")

    def test_api_publica_insertar_y_extraer_maximo(self):
        turnos = HeapTurnos()
        turnos.insertar("normal")
        turnos.insertar("urgente", HeapTurnos.PRIORIDAD_URGENTE)

        self.assertEqual(turnos.extraer_maximo(), "urgente")
        self.assertEqual(turnos.extraer_maximo(), "normal")
        with self.assertRaises(IndexError):
            turnos.extraer_maximo()

    def test_extraer_maximo_siempre_extrae_la_raiz(self):
        turnos = HeapTurnos()
        turnos.insertar("normal")
        for numero in range(4):
            turnos.insertar(f"urgente-{numero}", HeapTurnos.PRIORIDAD_URGENTE)
        for _ in range(3):
            turnos.desencolar()

        self.assertEqual(turnos.extraer_maximo(), "urgente-3")

    def test_estructura_vacia_y_prioridad_invalida(self):
        turnos = HeapTurnos()
        self.assertTrue(turnos.esta_vacia())
        with self.assertRaises(IndexError):
            turnos.frente()
        with self.assertRaises(IndexError):
            turnos.desencolar()
        with self.assertRaises(ValueError):
            turnos.encolar("invalido", 3)
        with self.assertRaises(ValueError):
            turnos.encolar("booleano", True)

    def test_eliminar_turnos_mantiene_el_heap(self):
        turnos = HeapTurnos()
        for prioridad in (1, 2, 0, 2, 1, 0, 2):
            turnos.encolar(str(prioridad), prioridad)

        resultado = [turnos.desencolar() for _ in range(len(turnos))]
        self.assertEqual(resultado, ["2", "2", "2", "0", "1", "1", "0"])
        self.assertTrue(turnos.esta_vacia())

    def test_banco_usa_prioridad_y_rechaza_ci_inexistente(self):
        with tempfile.TemporaryDirectory() as directorio:
            banco = Banco(Path(directorio) / "historial.jsonl")
            banco.registrar_cliente("111", "Carlos", "Silva", 100, "clave123")
            banco.registrar_cliente("222", "Ana", "Lopez", 100, "clave456")
            banco.solicitar_turno("111")
            banco.solicitar_turno("222", HeapTurnos.PRIORIDAD_URGENTE)

            self.assertFalse(banco.solicitar_turno("999"))
            self.assertFalse(banco.solicitar_turno("111", 9))
            self.assertEqual(banco.atender_turno().ci, "222")
            self.assertEqual(banco.atender_turno().ci, "111")

    def test_banco_sin_turnos_devuelve_none(self):
        with tempfile.TemporaryDirectory() as directorio:
            banco = Banco(Path(directorio) / "historial.jsonl")
            self.assertIsNone(banco.atender_turno())


if __name__ == "__main__":
    unittest.main()
