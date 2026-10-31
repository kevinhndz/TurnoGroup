from passlib.context import CryptContext

contexto = CryptContext(schemes=["argon2"], deprecated="auto")


def encriptar_contrasena(password: str) -> str:
    hash_contrasena = contexto.hash(password)
    return hash_contrasena


def verificar_contrasena(password: str, hash_guardado: str) -> bool:
    resultado = contexto.verify(password, hash_guardado)
    return resultado
