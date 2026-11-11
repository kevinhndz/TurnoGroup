"""Limites sencillos para frenar intentos repetidos desde una misma IP."""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic

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
    ip = request.client.host if request.client else "desconocida"
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
