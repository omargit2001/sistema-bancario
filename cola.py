from collections import deque


class Cola:
    """Cola FIFO: el primer elemento que entra es el primero que sale."""

    def __init__(self):
        self._datos = deque()

    def encolar(self, elemento):
        self._datos.append(elemento)

    def desencolar(self):
        if self.esta_vacia():
            raise IndexError("cola vacía")
        return self._datos.popleft()

    def frente(self):
        if self.esta_vacia():
            raise IndexError("cola vacía")
        return self._datos[0]

    def esta_vacia(self):
        return len(self._datos) == 0

    def __len__(self):
        return len(self._datos)