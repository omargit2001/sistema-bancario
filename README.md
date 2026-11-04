# Sistema Bancario

Proyecto educativo de consola para practicar estructuras de datos, operaciones bancarias básicas, autenticación y registro de acciones en archivos, sin utilizar una base de datos.

## Funcionalidades

- Registrar y buscar clientes por CI.
- Depositar y retirar dinero después de verificar la contraseña.
- Mostrar clientes y saldos de la sesión actual.
- Solicitar turnos y atenderlos en orden de llegada.
- Atender turnos con prioridades explícitas y una regla de equidad para evitar esperas indefinidas.
- Consultar el historial de acciones guardado en un archivo.

## Estructuras de datos

- **Diccionario (`dict`)**: almacena los clientes usando su CI como clave. La búsqueda tiene un costo promedio de $O(1)$.
- **Pila (`Pila`)**: mantiene las acciones recientes en orden LIFO (última en entrar, primera en salir). Incluye `push`, `pop`, `peek`, `esta_vacia` y `len`.
- **Cola (`Cola`)**: administra los turnos en orden FIFO (primero en entrar, primero en salir), usando `collections.deque`.
- **Heap binario (`HeapTurnos`)**: implementado desde cero sobre una lista, sin `heapq`; organiza los turnos por prioridad (normal, preferente o urgente) y conserva el orden de llegada cuando empatan. Incluye inserción y extracción del máximo con flotación y hundimiento. Para que las prioridades altas no acaparen el servicio, después de tres atenciones prioritarias consecutivas se atiende el turno pendiente de menor prioridad y más antiguo.

### Alcance de la versión v2

La familia seleccionada para el flujo nuevo es **heap** (una sola familia, como pide la consigna). El flujo es solicitar un turno con prioridad y atender el siguiente según prioridad y orden de llegada. Además, aplica **envejecimiento dinámico (aging)**: cada 60 segundos de espera, el turno gana un nivel de prioridad efectiva, hasta un máximo de urgente. Así, una solicitud normal que espere dos minutos puede empatar con los turnos urgentes; los empates conservan FIFO. La prioridad efectiva se actualiza al consultar o atender turnos. Para mantener la propiedad del heap, cada actualización reconstruye el orden de la lista; consultar o atender cuesta O(n), mientras que insertar cuesta O(log n). La regla adicional de equidad también atiende un turno de menor prioridad después de tres atenciones prioritarias consecutivas si todavía lo hay. Las prioridades originales son 0 (normal), 1 (preferente) y 2 (urgente); el sistema educativo no verifica por sí mismo la justificación de esas categorías.

No se agregan árbol binario ni BST en esta versión para respetar el requisito de elegir una sola familia. El diccionario existente sigue siendo el índice de clientes por CI.

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
│   ├── heap_turnos.py       # Turnos por prioridad mediante max-heap binario
│   ├── seguridad.py         # Hashes de contraseñas
│   └── registro.py          # Lectura y escritura JSONL
└── tests/
    ├── test_sistema_bancario.py
    └── test_heap_turnos.py
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

Las pruebas comprueban, entre otras cosas, operaciones bancarias, orden LIFO/FIFO, prioridad, envejecimiento y equidad del heap, autenticación y persistencia del historial. Usan un reloj controlado para verificar el aging y archivos temporales, por lo que no deberían crear un historial de prueba en la carpeta del proyecto.

### Entrega de la actividad

1. **Dominio:** sistema bancario.
2. **Repositorio y branch: https://github.com/omargit2001/sistema-bancario/tree/v2. Confirmo que la rama se llama v2.
3. **Flujo nuevo:** solicitar un turno con prioridad y atenderlo según prioridad, respetando FIFO en empates.
4. **Familia:** heap.
5. **La uso porque…** permite obtener el turno de mayor prioridad; el envejecimiento dinámico y la regla antiacaparamiento ayudan a que la espera no relegue indefinidamente a los turnos menos urgentes.
6. **Caso límite:** si no hay turnos pendientes, `desencolar` y `frente` lanzan `IndexError`; `Banco.atender_turno` informa que no hay turnos y devuelve `None`.

El proyecto está publicado en GitHub en la rama v2, creada desde v1.

## Alcance y seguridad

Este programa es una demostración educativa, no un sistema bancario de producción. Los clientes, sus hashes y saldos viven en memoria y se pierden al cerrar el programa; únicamente el historial de eventos queda guardado en el JSONL. Por tanto, el archivo no permite recuperar el estado actual de las cuentas.

El historial contiene datos personales como CI y nombres y se guarda como texto legible. Protégelo con permisos adecuados y no lo publiques. El hash de contraseña evita guardar la contraseña original, pero no sustituye las medidas de seguridad, almacenamiento duradero, control de acceso, auditoría y gestión de transacciones necesarias en una aplicación real.
