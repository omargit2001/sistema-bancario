import hashlib
import hmac
import secrets


ITERACIONES_HASH = 600_000


def crear_hash_contrasena(contrasena):
    sal = secrets.token_bytes(16)
    derivado = hashlib.pbkdf2_hmac(
        "sha256", contrasena.encode("utf-8"), sal, ITERACIONES_HASH
    )
    return f"{sal.hex()}${derivado.hex()}"


def verificar_contrasena(contrasena, hash_guardado):
    try:
        sal_hex, derivado_guardado = hash_guardado.split("$", maxsplit=1)
        sal = bytes.fromhex(sal_hex)
    except (AttributeError, ValueError):
        return False

    derivado = hashlib.pbkdf2_hmac(
        "sha256", contrasena.encode("utf-8"), sal, ITERACIONES_HASH
    ).hex()
    return hmac.compare_digest(derivado, derivado_guardado)