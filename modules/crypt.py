import hashlib
import hmac
import os
import typing

"""
Configuración de la función scrypt
* SCRYPT_N:  Costo de CPU y memoria
* SCRYPT_R:  Tamaño del bloque
* SCRYPT_P:  Factor de paralelización
* SALT_SIZE: Tamaño del salt en bytes
"""
SCRYPT_N: typing.Final[int] = 2**14 
SCRYPT_R: typing.Final[int] = 8
SCRYPT_P: typing.Final[int] = 1
SALT_SIZE: typing.Final[int] = 16

def hash_password(password: str) -> str:
    """
    Devuelve la contraseña encriptada
    """
    salt: bytes = os.urandom(SALT_SIZE)
    password_hash: bytes = hashlib.scrypt(
        password.encode(),
        salt = salt,
        n = SCRYPT_N,
        r = SCRYPT_R,
        p = SCRYPT_P
    )
    return f"{SCRYPT_N}:{SCRYPT_R}:{SCRYPT_P}:{salt.hex()}:{password_hash.hex()}"

def check_password(password: str | None, stored_password: str | None) -> bool:
    """
    Comprueba si una contraseña coincide con la encriptada
    """
    if not password or not stored_password:
        return False
    parts: list[str] = stored_password.split(":")
    if len(parts) != 5:
        return False
    n: int = int(parts[0])
    r: int = int(parts[1])
    p: int = int(parts[2])
    salt: bytes = bytes.fromhex(parts[3])
    expected_hash: bytes = bytes.fromhex(parts[4])
    password_hash: bytes = hashlib.scrypt(
        password.encode(),
        salt = salt,
        n = n,
        r = r,
        p = p
    )
    return hmac.compare_digest(password_hash, expected_hash)