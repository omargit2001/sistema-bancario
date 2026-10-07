class Pila:
    def __init__(self):
        self._datos = []

    def push(self, elemento):
        self._datos.append(elemento)

    def pop(self):
        if self.esta_vacia():
            raise IndexError("pila vacía")
        return self._datos.pop()

    def peek(self):
        if self.esta_vacia():
            raise IndexError("pila vacía")
        return self._datos[-1]

    def esta_vacia(self):
        return len(self._datos) == 0

    def is_empty(self):
        return self.esta_vacia()

    def __len__(self):
        return len(self._datos)

    def mostrar(self):
        # Muestra los elementos desde el último ingresado hasta el primero
        if self.esta_vacia():
            print("El historial está vacío.")
            return
        
        print("\n--- HISTORIAL DE OPERACIONES (LIFO) ---")
        # Recorremos la lista de atrás hacia adelante
        for item in reversed(self._datos):
            print(f"- {item}")
        print("---------------------------------------")
