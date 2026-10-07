from getpass import getpass

from banco import Banco

def solicitar_numero_entero(mensaje):
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("Entrada inválida. Debe ingresar un número entero.")

def solicitar_numero_flotante(mensaje):
    while True:
        try:
            monto = float(input(mensaje))
            return monto
        except ValueError:
            print("Entrada inválida. Debe ingresar un número decimal válido.")

def iniciar_menu():
    banco = Banco()

    while True:
        print("\n================================")
        print("       SISTEMA BANCARIO")
        print("================================")
        print("1. Registrar cliente")
        print("2. Buscar cliente")
        print("3. Realizar depósito")
        print("4. Realizar retiro")
        print("5. Mostrar clientes")
        print("6. Ver historial de operaciones guardado")
        print("7. Solicitar turno")
        print("8. Atender siguiente turno")
        print("9. Salir")
        print("================================")
        
        opcion = solicitar_numero_entero("Seleccione una opción: ")

        if opcion == 1:
            ci = input("Ingrese el CI: ").strip()
            nombre = input("Ingrese el nombre: ").strip()
            apellido = input("Ingrese el apellido: ").strip()
            contrasena = getpass("Cree una contraseña (mínimo 8 caracteres): ")
            confirmacion = getpass("Repita la contraseña: ")

            if contrasena != confirmacion:
                print("Error: Las contraseñas no coinciden.")
                continue
            
            if not ci or not nombre or not apellido:
                print("Error: No se permiten campos vacíos.")
                continue
                
            saldo_inicial = solicitar_numero_flotante("Ingrese el saldo inicial: ")
            if saldo_inicial < 0:
                print("Error: El saldo inicial no puede ser negativo.")
                continue
                
            banco.registrar_cliente(ci, nombre, apellido, saldo_inicial, contrasena)

        elif opcion == 2:
            ci = input("Ingrese el CI del cliente a buscar: ").strip()
            cliente = banco.buscar_cliente(ci)
            if cliente:
                print("\n[Cliente Encontrado]")
                print(cliente.mostrar_informacion())
            else:
                print("Error: Cliente no encontrado.")

        elif opcion == 3:
            ci = input("Ingrese el CI del cliente: ").strip()
            monto = solicitar_numero_flotante("Ingrese el monto a depositar: ")
            contrasena = getpass("Contraseña: ")
            banco.depositar(ci, monto, contrasena)

        elif opcion == 4:
            ci = input("Ingrese el CI del cliente: ").strip()
            monto = solicitar_numero_flotante("Ingrese el monto a retirar: ")
            contrasena = getpass("Contraseña: ")
            banco.retirar(ci, monto, contrasena)

        elif opcion == 5:
            banco.mostrar_todos_los_clientes()

        elif opcion == 6:
            banco.mostrar_historial_guardado()

        elif opcion == 7:
            ci = input("Ingrese el CI para solicitar turno: ").strip()
            banco.solicitar_turno(ci)

        elif opcion == 8:
            banco.atender_turno()

        elif opcion == 9:
            print("Gracias por usar el sistema bancario. ¡Hasta luego!")
            break
        else:
            print("Error: Opción inexistente del menú. Intente de nuevo.")
