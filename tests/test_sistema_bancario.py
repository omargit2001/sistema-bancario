import json
import tempfile
import unittest
from pathlib import Path

from src.banco import Banco
from src.cola import Cola
from src.pila import Pila

class TestSistemaBancario(unittest.TestCase):

    def setUp(self):
        self.directorio_temporal = tempfile.TemporaryDirectory()
        self.ruta_historial = Path(self.directorio_temporal.name) / "historial.jsonl"
        self.banco = Banco(self.ruta_historial)

    def tearDown(self):
        self.directorio_temporal.cleanup()

    # 1. Registrar un cliente
    def test_registrar_cliente_valido(self):
        resultado = self.banco.registrar_cliente(
            "111", "Carlos", "Silva", 100.0, "clave123"
        )
        self.assertTrue(resultado)
        self.assertEqual(len(self.banco.clientes), 1)

    # 2. Buscar un cliente existente
    def test_buscar_cliente_existente(self):
        self.banco.registrar_cliente("111", "Carlos", "Silva", 100.0, "clave123")
        cliente = self.banco.buscar_cliente("111")
        self.assertIsNotNone(cliente)
        self.assertEqual(cliente.nombre, "Carlos")

    # 3. Buscar un cliente inexistente
    def test_buscar_cliente_inexistente(self):
        cliente = self.banco.buscar_cliente("999")
        self.assertIsNone(cliente)

    # 4. Evitar clientes con CI repetido
    def test_evitar_ci_repetido(self):
        self.banco.registrar_cliente("111", "Carlos", "Silva", 100.0, "clave123")
        resultado_repetido = self.banco.registrar_cliente(
            "111", "Andres", "Lopez", 50.0, "clave456"
        )
        self.assertFalse(resultado_repetido)

    # 5. Realizar un depósito válido
    def test_deposito_valido(self):
        self.banco.registrar_cliente("111", "Carlos", "Silva", 100.0, "clave123")
        resultado = self.banco.depositar("111", 50.0, "clave123")
        self.assertTrue(resultado)
        self.assertEqual(self.banco.buscar_cliente("111").saldo, 150.0)

    # 6. Evitar depósitos negativos o cero
    def test_deposito_invalido(self):
        self.banco.registrar_cliente("111", "Carlos", "Silva", 100.0, "clave123")
        resultado = self.banco.depositar("111", -20.0, "clave123")
        self.assertFalse(resultado)

    # 7. Realizar un retiro válido
    def test_retiro_valido(self):
        self.banco.registrar_cliente("111", "Carlos", "Silva", 100.0, "clave123")
        resultado = self.banco.retirar("111", 40.0, "clave123")
        self.assertTrue(resultado)
        self.assertEqual(self.banco.buscar_cliente("111").saldo, 60.0)

    # 8. Evitar retiros mayores al saldo
    def test_retiro_mayor_al_saldo(self):
        self.banco.registrar_cliente("111", "Carlos", "Silva", 100.0, "clave123")
        resultado = self.banco.retirar("111", 150.0, "clave123")
        self.assertFalse(resultado)

    # 9. Comprobar que la pila almacena operaciones
    def test_pila_almacena_operaciones(self):
        self.banco.registrar_cliente("111", "Carlos", "Silva", 100.0, "clave123")
        self.banco.depositar("111", 50.0, "clave123")
        self.assertFalse(self.banco.historial.is_empty())

    # 10. Comprobar que la pila respeta LIFO
    def test_pila_respeta_lifo(self):
        pila = Pila()
        pila.push("Primer evento")
        pila.push("Segundo evento")
        self.assertEqual(pila.peek(), "Segundo evento")
        self.assertEqual(len(pila), 2)
        self.assertEqual(pila.pop(), "Segundo evento")
        self.assertEqual(pila.pop(), "Primer evento")

    # 11. Comprobar que las operaciones inválidas de una pila vacía se detectan
    def test_pila_vacia_lanza_error(self):
        pila = Pila()
        self.assertTrue(pila.esta_vacia())
        with self.assertRaises(IndexError):
            pila.pop()
        with self.assertRaises(IndexError):
            pila.peek()

    # 12. Comprobar entradas inválidas (Campos vacíos)
    def test_campos_vacios_registro(self):
        resultado = self.banco.registrar_cliente(
            "", "", "Silva", 100.0, "clave123"
        )
        self.assertFalse(resultado)

    def test_contrasena_se_guarda_con_hash_y_autentica(self):
        self.banco.registrar_cliente("111", "Carlos", "Silva", 100.0, "clave123")
        cliente = self.banco.buscar_cliente("111")
        self.assertNotIn("clave123", cliente._hash_contrasena)
        self.assertTrue(self.banco.autenticar_cliente("111", "clave123"))
        self.assertFalse(self.banco.autenticar_cliente("111", "incorrecta"))

    def test_operacion_rechaza_contrasena_incorrecta(self):
        self.banco.registrar_cliente("111", "Carlos", "Silva", 100.0, "clave123")
        resultado = self.banco.retirar("111", 20.0, "incorrecta")
        self.assertFalse(resultado)
        self.assertEqual(self.banco.buscar_cliente("111").saldo, 100.0)

    def test_turnos_se_atienden_en_orden_fifo(self):
        self.banco.registrar_cliente("111", "Carlos", "Silva", 100.0, "clave123")
        self.banco.registrar_cliente("222", "Ana", "Lopez", 50.0, "clave456")
        self.banco.solicitar_turno("111")
        self.banco.solicitar_turno("222")
        self.assertEqual(self.banco.atender_turno().ci, "111")
        self.assertEqual(self.banco.atender_turno().ci, "222")

    def test_cola_fifo_y_error_si_esta_vacia(self):
        cola = Cola()
        cola.encolar("primero")
        cola.encolar("segundo")
        self.assertEqual(cola.frente(), "primero")
        self.assertEqual(cola.desencolar(), "primero")
        self.assertEqual(cola.desencolar(), "segundo")
        with self.assertRaises(IndexError):
            cola.desencolar()

    def test_acciones_persisten_en_jsonl_sin_contrasena(self):
        self.banco.registrar_cliente("111", "Carlos", "Silva", 100.0, "clave123")
        self.banco.depositar("111", 50.0, "clave123")

        contenido = self.ruta_historial.read_text(encoding="utf-8")
        eventos = [json.loads(linea) for linea in contenido.splitlines()]
        self.assertEqual(
            [evento["accion"] for evento in eventos],
            ["registro_cliente", "deposito"],
        )
        self.assertEqual(eventos[1]["monto_bs"], 50.0)
        self.assertEqual(eventos[1]["saldo_bs"], 150.0)
        self.assertNotIn("clave123", contenido)

        banco_reiniciado = Banco(self.ruta_historial)
        self.assertEqual(len(banco_reiniciado.registro.leer()), 2)

if __name__ == '__main__':
    unittest.main()
