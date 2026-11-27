"""Limita el cuerpo antes de que FastAPI intente interpretar el JSON."""

import asyncio
from starlette.responses import JSONResponse


def limite_cuerpo(ruta):
    if ruta == "/productos/menu-inteligente/preparar":
        return 4_100_000
    if ruta.startswith("/productos/") and ruta.endswith("/imagen"):
        return 7_100_000
    if ruta == "/productos/revisar-archivo":
        return 1_400_000
    return 1_000_000


class LimitarSolicitudes:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] in ("GET", "HEAD", "OPTIONS"):
            await self.app(scope, receive, send)
            return

        limite = limite_cuerpo(scope["path"])
        contenido = bytearray()
        try:
            # Es el tiempo total de lectura, no un plazo nuevo por cada fragmento.
            async with asyncio.timeout(15):
                while True:
                    mensaje = await receive()
                    if mensaje["type"] == "http.disconnect":
                        return
                    fragmento = mensaje.get("body", b"")
                    if len(contenido) + len(fragmento) > limite:
                        respuesta = JSONResponse(
                            {"detail": "La solicitud es demasiado grande"},
                            status_code=413,
                        )
                        await respuesta(scope, receive, send)
                        return
                    contenido.extend(fragmento)
                    if not mensaje.get("more_body", False):
                        break
        except TimeoutError:
            respuesta = JSONResponse(
                {"detail": "Tiempo de lectura agotado"}, status_code=408
            )
            await respuesta(scope, receive, send)
            return

        entregado = False

        async def leer():
            nonlocal entregado
            if entregado:
                return await receive()
            entregado = True
            return {
                "type": "http.request",
                "body": bytes(contenido),
                "more_body": False,
            }

        await self.app(scope, leer, send)
