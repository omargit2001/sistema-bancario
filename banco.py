import json
import math
from pathlib import Path

from cliente import Cliente
from cola import Cola
from pila import Pila
from registro import RegistroOperaciones

class Banco:
    def __init__(self, ruta_historial=None):
        # El CI es la clave para buscar clientes en tiempo promedio constante.
        self.clientes = {}
        self.historial = Pila()
        self.turnos = Cola()
        if ruta_historial is None:
            ruta_historial = Path(__file__).with_name("historial_banco.jsonl")
        self.registro = RegistroOperaciones(ruta_historial)

    def buscar_cliente(self, ci):
        return self.clientes.get(ci)

    def _guardar_evento(self, accion, ci, detalle, monto_bs=None, saldo_bs=None):
        try:
            self.registro.guardar(accion, ci, detalle, monto_bs, saldo_bs)
        except OSError as error:
            print(f"Error: No se pudo guardar la operación en el archivo: {error}")
            return False

        self.historial.push(detalle)
        return True

    def mostrar_historial_guardado(self):
        try:
            eventos = self.registro.leer()
        except (OSError, ValueError) as error:
            print(f"Error al leer el historial: {error}")
            return

        if not eventos:
            print("Todavía no hay operaciones guardadas en el archivo.")
            return

        print(f"\n--- HISTORIAL GUARDADO EN {self.registro.ruta.name} ---")
        for evento in eventos:
            print(json.dumps(evento, ensure_ascii=False, indent=2))

    def registrar_cliente(self, ci, nombre, apellido, saldo_inicial, contrasena):
        if not ci or not nombre or not apellido:
            print("Error: El CI, nombre y apellido no pueden estar vacíos.")
            return False

        if not contrasena or len(contrasena) < 8:
            print("Error: La contraseña debe tener al menos 8 caracteres.")
            return False

        try:
            saldo_inicial = float(saldo_inicial)
        except (TypeError, ValueError):
            print("Error: El saldo inicial debe ser un número válido.")
            return False

        if not math.isfinite(saldo_inicial) or saldo_inicial < 0:
            print("Error: El saldo inicial no puede ser negativo ni infinito.")
            return False
        
        if self.buscar_cliente(ci) is not None:
            print(f"Error: Ya existe un cliente registrado con el CI: {ci}.")
            return False

        nuevo_cliente = Cliente(ci, nombre, apellido, saldo_inicial, contrasena)
        detalle = f"Cliente {nombre} {apellido} registrado"
        if not self._guardar_evento(
            "registro_cliente", ci, detalle, saldo_bs=saldo_inicial
        ):
            return False
        self.clientes[ci] = nuevo_cliente
        print("Cliente registrado exitosamente.")
        return True

    def autenticar_cliente(self, ci, contrasena):
        cliente = self.buscar_cliente(ci)
        return cliente is not None and cliente.verificar_contrasena(contrasena)

    def depositar(self, ci, monto, contrasena):
        cliente = self.buscar_cliente(ci)
        if cliente is None or not cliente.verificar_contrasena(contrasena):
            print("Error: CI o contraseña incorrectos.")
            return False

        try:
            monto = float(monto)
        except (TypeError, ValueError):
            print("Error: El monto debe ser un número válido.")
            return False

        if not math.isfinite(monto) or monto <= 0:
            print("Error: El monto debe ser mayor que cero.")
            return False

        nuevo_saldo = cliente.saldo + monto
        detalle = f"Depósito de Bs. {monto:.2f} para {cliente.nombre} {cliente.apellido}"
        if not self._guardar_evento(
            "deposito", ci, detalle, monto_bs=monto, saldo_bs=nuevo_saldo
        ):
            return False

        cliente.saldo = nuevo_saldo
        print(f"Depósito exitoso. Nuevo saldo: Bs. {cliente.saldo:.2f}")
        return True

    def retirar(self, ci, monto, contrasena):
        cliente = self.buscar_cliente(ci)
        if cliente is None or not cliente.verificar_contrasena(contrasena):
            print("Error: CI o contraseña incorrectos.")
            return False

        try:
            monto = float(monto)
        except (TypeError, ValueError):
            print("Error: El monto debe ser un número válido.")
            return False

        if not math.isfinite(monto) or monto <= 0:
            print("Error: El monto debe ser mayor que cero.")
            return False

        if monto > cliente.saldo:
            print("Error: Saldo insuficiente.")
            return False

        nuevo_saldo = cliente.saldo - monto
        detalle = f"Retiro de Bs. {monto:.2f} para {cliente.nombre} {cliente.apellido}"
        if not self._guardar_evento(
            "retiro", ci, detalle, monto_bs=monto, saldo_bs=nuevo_saldo
        ):
            return False

        cliente.saldo = nuevo_saldo
        print(f"Retiro exitoso. Nuevo saldo: Bs. {cliente.saldo:.2f}")
        return True

    def solicitar_turno(self, ci):
        cliente = self.buscar_cliente(ci)
        if cliente is None:
            print("Error: Cliente no encontrado.")
            return False

        detalle = f"Turno solicitado por {cliente.nombre} {cliente.apellido}"
        if not self._guardar_evento("solicitud_turno", ci, detalle):
            return False

        self.turnos.encolar(ci)
        print(f"Turno agregado a la cola. Posición: {len(self.turnos)}")
        return True

    def atender_turno(self):
        if self.turnos.esta_vacia():
            print("No hay turnos pendientes.")
            return None

        ci = self.turnos.frente()
        cliente = self.buscar_cliente(ci)
        detalle = f"Turno atendido: {cliente.nombre} {cliente.apellido}"
        if not self._guardar_evento(
            "atencion_turno", ci, detalle, saldo_bs=cliente.saldo
        ):
            return None

        self.turnos.desencolar()
        print(f"Atendiendo a {cliente.nombre} {cliente.apellido} (CI: {cliente.ci}).")
        return cliente

    def mostrar_todos_los_clientes(self):
        if not self.clientes:
            print("No hay clientes registrados en el sistema.")
            return
        print("\n--- LISTA DE CLIENTES ---")
        for cliente in self.clientes.values():
            print(cliente.mostrar_informacion())
