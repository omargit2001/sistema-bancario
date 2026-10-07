# Sistema Bancario

Proyecto educativo de consola para practicar estructuras de datos, operaciones bancarias básicas, autenticación y registro de acciones en archivos, sin utilizar una base de datos.

## Funcionalidades

- Registrar y buscar clientes por CI.
- Depositar y retirar dinero después de verificar la contraseña.
- Mostrar clientes y saldos de la sesión actual.
- Solicitar turnos y atenderlos en orden de llegada.
- Consultar el historial de acciones guardado en un archivo.

## Estructuras de datos

- **Diccionario (`dict`)**: almacena los clientes usando su CI como clave. La búsqueda tiene un costo promedio de $O(1)$.
- **Pila (`Pila`)**: mantiene las acciones recientes en orden LIFO (última en entrar, primera en salir). Incluye `push`, `pop`, `peek`, `esta_vacia` y `len`.
- **Cola (`Cola`)**: administra los turnos en orden FIFO (primero en entrar, primero en salir), usando `collections.deque`.

## Estructura del proyecto

```text
.
├── main.py                  # Lanzador de la aplicación
├── README.md
├── historial_banco.jsonl    # Se crea al registrar la primera acción
├── src/
│   ├── main.py              # Entrada de la aplicación
│   ├── menu.py              # Menú de consola
│   ├── banco.py             # Operaciones y coordinación de estructuras
│   ├── cliente.py           # Cliente y autenticación
│   ├── pila.py              # Historial LIFO en memoria
│   ├── cola.py              # Turnos FIFO
│   ├── seguridad.py         # Hashes de contraseñas
│   └── registro.py          # Lectura y escritura JSONL
└── tests/
	└── test_sistema_bancario.py
```

## Requisitos

Python 3.10 o posterior. El proyecto usa únicamente la biblioteca estándar de Python, por lo que no hace falta instalar paquetes adicionales.

## Ejecutar

Desde la carpeta raíz del proyecto, inicia el programa con:

```sh
python3 main.py
```

En el menú puedes registrar clientes, hacer operaciones con su CI y contraseña, pedir turnos y consultar el historial guardado. La contraseña se solicita con `getpass`, así que no se muestra mientras se escribe.

## Historial en archivo

El banco agrega las acciones exitosas a `historial_banco.jsonl`, ubicado en la raíz del proyecto. El archivo se crea automáticamente al realizar la primera acción registrada. Cada línea contiene un objeto JSON independiente con campos como fecha, tipo de acción, CI, detalle, monto y saldo resultante. Por ejemplo:

```json
{"fecha":"2026-10-07T12:00:00+00:00","accion":"deposito","ci":"111","detalle":"Depósito de Bs. 50.00 para Carlos Silva","monto_bs":50.0,"saldo_bs":150.0}
```

La opción 6 del menú muestra los eventos que están en el archivo. Las contraseñas no se incluyen en el JSONL. Los valores monetarios del ejemplo son ilustrativos.

## Ejecutar las pruebas

```sh
python3 -m unittest discover -s tests -v
```

Las pruebas comprueban, entre otras cosas, operaciones bancarias, orden LIFO/FIFO, autenticación y persistencia del historial. Usan archivos temporales y no deberían crear un historial de prueba en la carpeta del proyecto.

## Alcance y seguridad

Este programa es una demostración educativa, no un sistema bancario de producción. Los clientes, sus hashes y saldos viven en memoria y se pierden al cerrar el programa; únicamente el historial de eventos queda guardado en el JSONL. Por tanto, el archivo no permite recuperar el estado actual de las cuentas.

El historial contiene datos personales como CI y nombres y se guarda como texto legible. Protégelo con permisos adecuados y no lo publiques. El hash de contraseña evita guardar la contraseña original, pero no sustituye las medidas de seguridad, almacenamiento duradero, control de acceso, auditoría y gestión de transacciones necesarias en una aplicación real.
