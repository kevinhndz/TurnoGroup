"""Eventos de seguridad sin cuerpos, cookies, correos ni codigos de acceso."""

import json
import logging
from time import monotonic
from uuid import uuid4

registro = logging.getLogger("turnogroup.seguridad")


class AuditoriaSeguridad:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        id_solicitud = uuid4().hex
        inicio = monotonic()
        registrado = False

        def registrar(estado):
            nonlocal registrado
            if registrado:
                return
            ruta = getattr(scope.get("route"), "path", "desconocida")
            sensible = ruta.startswith(
                (
                    "/sesiones",
                    "/usuarios",
                    "/recuperaciones-clave",
                    "/invitaciones-laborales",
                    "/vinculos-laborales",
                    "/suscripciones",
                )
            )
            if (
                estado not in (401, 403, 429)
                and estado < 500
                and not (sensible and scope["method"] not in ("GET", "HEAD", "OPTIONS"))
            ):
                return
            registrado = True
            sesion = scope.get("state", {}).get("sesion_validada")
            evento = {
                "evento": (
                    "error_interno"
                    if estado >= 500
                    else ("acceso_rechazado" if estado >= 400 else "operacion_sensible")
                ),
                "solicitud": id_solicitud,
                "ruta": ruta,
                "metodo": scope["method"],
                "estado": estado,
                "id_usuario": sesion[1].id if sesion else None,
                "duracion_ms": round((monotonic() - inicio) * 1000),
            }
            nivel = (
                logging.ERROR
                if estado >= 500
                else (logging.WARNING if estado >= 400 else logging.INFO)
            )
            registro.log(nivel, json.dumps(evento))

        async def responder(mensaje):
            if mensaje["type"] == "http.response.start":
                mensaje.setdefault("headers", []).append(
                    (b"x-request-id", id_solicitud.encode())
                )
                registrar(mensaje["status"])
            await send(mensaje)

        try:
            await self.app(scope, receive, responder)
        except Exception:
            # La excepcion puede contener secretos: registro solo el resultado.
            registrar(500)
            raise
