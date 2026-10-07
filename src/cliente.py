from .seguridad import crear_hash_contrasena, verificar_contrasena


class Cliente:
    def __init__(self, ci, nombre, apellido, saldo_inicial, contrasena):
        self.ci = ci
        self.nombre = nombre
        self.apellido = apellido
        self.saldo = float(saldo_inicial)
        self._hash_contrasena = crear_hash_contrasena(contrasena)

    def verificar_contrasena(self, contrasena):
        return verificar_contrasena(contrasena, self._hash_contrasena)

    def mostrar_informacion(self):
        return f"CI: {self.ci} | Cliente: {self.nombre} {self.apellido} | Saldo: Bs. {self.saldo:.2f}"
