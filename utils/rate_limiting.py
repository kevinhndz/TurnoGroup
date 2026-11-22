"""Limites sencillos para frenar intentos repetidos desde una misma IP."""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from hashlib import sha256
from hmac import compare_digest
from ipaddress import ip_address
from functools import lru_cache

from redis import Redis, RedisError
from core.config import revision

from fastapi import HTTPException, Request

_intentos = defaultdict(deque)
_candado = Lock()


def limitar_por_ip(
    request: Request,
    nombre: str,
    limite: int,
    ventana: int,
) -> None:
    """Permite `limite` intentos dentro de `ventana` segundos por IP."""
    ip = obtener_ip(request)
    if revision.REDIS_URL:
        limitar_compartido(nombre, ip, limite, ventana)
        return
    ahora = monotonic()
    clave = (nombre, ip)

    with _candado:
        intentos = _intentos[clave]
        while intentos and ahora - intentos[0] >= ventana:
            intentos.popleft()

        if len(intentos) >= limite:
            espera = max(1, ventana - int(ahora - intentos[0]))
            raise HTTPException(
                status_code=429,
                detail="Demasiadas solicitudes. Intenta de nuevo mas tarde.",
                headers={"Retry-After": str(espera)},
            )

        intentos.append(ahora)


def limpiar_limites() -> None:
    """Limpia los datos; se usa en pruebas y al reiniciar el servicio."""
    with _candado:
        _intentos.clear()


# Redis ejecuta contador y vencimiento juntos, aunque haya varias instancias.
CONTAR = """
local cantidad = redis.call('INCR', KEYS[1])
if cantidad == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
return {cantidad, redis.call('TTL', KEYS[1])}
"""


@lru_cache(maxsize=1)
def conexion_redis(url):
    return Redis.from_url(url, socket_timeout=2, socket_connect_timeout=2)


def limitar_compartido(nombre, identidad, limite, ventana):
    resumen = sha256(identidad.encode()).hexdigest()
    clave = "turnogroup:limites:" + nombre + ":" + resumen
    try:
        cantidad, espera = conexion_redis(revision.REDIS_URL).eval(
            CONTAR, 1, clave, ventana
        )
    except RedisError:
        # Si falla el contador compartido, no permito intentos ilimitados.
        raise HTTPException(503, "Proteccion temporalmente no disponible") from None
    if cantidad > limite:
        raise HTTPException(
            429,
            "Demasiadas solicitudes. Intenta de nuevo mas tarde.",
            headers={"Retry-After": str(max(1, espera))},
        )


def obtener_ip(request):
    cabeceras = getattr(request, "headers", {})
    secreto = cabeceras.get("X-TurnoGroup-Proxy-Secret", "")
    if revision.BACKEND_PROXY_SECRET and compare_digest(
        secreto, revision.BACKEND_PROXY_SECRET
    ):
        valor = cabeceras.get("X-TurnoGroup-Client-IP")
        if valor:
            try:
                return str(ip_address(valor))
            except ValueError:
                raise HTTPException(400, "Direccion de cliente invalida") from None
    return request.client.host if request.client else "desconocida"


def limitar_por_cuenta(correo):
    # Limite separado para ataques que cambian de IP contra el mismo correo.
    identidad = correo.strip().lower()
    if revision.REDIS_URL:
        limitar_compartido("cuenta", identidad, 20, 300)
