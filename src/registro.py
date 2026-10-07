import json
from datetime import datetime, timezone
from pathlib import Path


class RegistroOperaciones:
    def __init__(self, ruta):
        self.ruta = Path(ruta)

    def guardar(self, accion, ci, detalle, monto_bs=None, saldo_bs=None):
        evento = {
            "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "accion": accion,
            "ci": ci,
            "detalle": detalle,
            "monto_bs": monto_bs,
            "saldo_bs": saldo_bs,
        }

        with self.ruta.open("a", encoding="utf-8") as archivo:
            json.dump(evento, archivo, ensure_ascii=False)
            archivo.write("\n")

        return evento

    def leer(self):
        if not self.ruta.exists():
            return []

        eventos = []
        with self.ruta.open("r", encoding="utf-8") as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                if not linea.strip():
                    continue
                try:
                    eventos.append(json.loads(linea))
                except json.JSONDecodeError as error:
                    raise ValueError(
                        f"El registro tiene JSON inválido en la línea {numero_linea}."
                    ) from error

        return eventos