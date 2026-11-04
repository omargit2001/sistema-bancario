import time


class HeapTurnos:
    """Cola de prioridad max-heap para turnos, con FIFO dentro de cada nivel."""

    PRIORIDAD_NORMAL = 0
    PRIORIDAD_PREFERENTE = 1
    PRIORIDAD_URGENTE = 2
    MAX_TURNOS_PRIORITARIOS_CONSECUTIVOS = 3
    SEGUNDOS_POR_ENVEJECIMIENTO = 60

    def __init__(self, reloj=None):
        self._heap = []
        self._siguiente_orden = 0
        self._prioritarios_consecutivos = 0
        self._reloj = reloj if reloj is not None else time.monotonic

    def esta_vacia(self):
        return not self._heap

    def __len__(self):
        return len(self._heap)

    @staticmethod
    def validar_prioridad(prioridad):
        if type(prioridad) is not int or prioridad not in (0, 1, 2):
            raise ValueError(
                "La prioridad debe ser 0 (normal), 1 (preferente) o 2 (urgente)."
            )

    def encolar(self, ci, prioridad=PRIORIDAD_NORMAL):
        self.validar_prioridad(prioridad)

        turno = {
            "ci": ci,
            "prioridad_base": prioridad,
            "prioridad_efectiva": prioridad,
            "orden": self._siguiente_orden,
            "llegada": self._reloj(),
        }
        self._siguiente_orden += 1
        self._heap.append(turno)
        self._sift_up(len(self._heap) - 1)

    def insertar(self, ci, prioridad=PRIORIDAD_NORMAL):
        self.encolar(ci, prioridad)

    def frente(self):
        if self.esta_vacia():
            raise IndexError("No hay turnos pendientes.")
        self._actualizar_prioridades_por_espera()
        return self._heap[self._indice_siguiente_turno()]["ci"]

    def desencolar(self):
        if self.esta_vacia():
            raise IndexError("No hay turnos pendientes.")

        self._actualizar_prioridades_por_espera()
        indice = self._indice_siguiente_turno()
        prioridad_maxima = self._heap[0]["prioridad_efectiva"]
        hay_prioridad_menor = any(
            turno["prioridad_efectiva"] < prioridad_maxima
            for turno in self._heap
        )
        turno = self._eliminar(indice)
        if indice != 0:
            self._prioritarios_consecutivos = 0
            return turno["ci"]

        if (
            turno["prioridad_efectiva"] > self.PRIORIDAD_NORMAL
            and hay_prioridad_menor
        ):
            self._prioritarios_consecutivos += 1
        else:
            self._prioritarios_consecutivos = 0
        return turno["ci"]

    def extraer_maximo(self):
        if self.esta_vacia():
            raise IndexError("No hay turnos pendientes.")
        self._actualizar_prioridades_por_espera()
        return self._eliminar(0)["ci"]

    def _indice_siguiente_turno(self):
        prioridad_maxima = self._heap[0]["prioridad_efectiva"]
        hay_prioridad_menor = any(
            turno["prioridad_efectiva"] < prioridad_maxima
            for turno in self._heap
        )
        if (
            self._prioritarios_consecutivos
            >= self.MAX_TURNOS_PRIORITARIOS_CONSECUTIVOS
            and hay_prioridad_menor
        ):
            return min(
                (
                    indice
                    for indice, turno in enumerate(self._heap)
                    if turno["prioridad_efectiva"] < prioridad_maxima
                ),
                key=lambda indice: (
                    self._heap[indice]["prioridad_efectiva"],
                    self._heap[indice]["orden"],
                ),
            )
        return 0

    def _actualizar_prioridades_por_espera(self):
        ahora = self._reloj()
        for turno in self._heap:
            niveles_ganados = int(
                (ahora - turno["llegada"])
                // self.SEGUNDOS_POR_ENVEJECIMIENTO
            )
            turno["prioridad_efectiva"] = min(
                self.PRIORIDAD_URGENTE,
                turno["prioridad_base"] + niveles_ganados,
            )

        for indice in range(len(self._heap) // 2 - 1, -1, -1):
            self._sift_down(indice)

    def _es_mayor(self, izquierda, derecha):
        turno_izquierdo = self._heap[izquierda]
        turno_derecho = self._heap[derecha]
        return (
            turno_izquierdo["prioridad_efectiva"],
            -turno_izquierdo["orden"],
        ) > (
            turno_derecho["prioridad_efectiva"],
            -turno_derecho["orden"],
        )

    def _sift_up(self, indice):
        while indice > 0:
            padre = (indice - 1) // 2
            if not self._es_mayor(indice, padre):
                break
            self._heap[indice], self._heap[padre] = (
                self._heap[padre],
                self._heap[indice],
            )
            indice = padre

    def _sift_down(self, indice):
        cantidad = len(self._heap)
        while True:
            izquierda = 2 * indice + 1
            derecha = izquierda + 1
            mayor = indice

            if izquierda < cantidad and self._es_mayor(izquierda, mayor):
                mayor = izquierda
            if derecha < cantidad and self._es_mayor(derecha, mayor):
                mayor = derecha
            if mayor == indice:
                return

            self._heap[indice], self._heap[mayor] = (
                self._heap[mayor],
                self._heap[indice],
            )
            indice = mayor

    def _eliminar(self, indice):
        eliminado = self._heap[indice]
        ultimo = self._heap.pop()
        if indice < len(self._heap):
            self._heap[indice] = ultimo
            padre = (indice - 1) // 2
            if indice > 0 and self._es_mayor(indice, padre):
                self._sift_up(indice)
            else:
                self._sift_down(indice)
        return eliminado
