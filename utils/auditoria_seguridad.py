"""Eventos de seguridad sin cuerpos, cookies, correos ni codigos de acceso."""

import json
import logging
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

        async def responder(mensaje):
            if mensaje["type"] == "http.response.start":
                mensaje.setdefault("headers", []).append(
                    (b"x-request-id", id_solicitud.encode())
                )
                estado = mensaje["status"]
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
                if estado in (401, 403, 429) or (
                    sensible and scope["method"] not in ("GET", "HEAD", "OPTIONS")
                ):
                    sesion = scope.get("state", {}).get("sesion_validada")
                    usuario = sesion[1].id if sesion else None
                    evento = json.dumps(
                        {
                            "evento": (
                                "acceso_rechazado"
                                if estado >= 400
                                else "operacion_sensible"
                            ),
                            "solicitud": id_solicitud,
                            "ruta": ruta,
                            "metodo": scope["method"],
                            "estado": estado,
                            "id_usuario": usuario,
                        }
                    )
                    registro.log(
                        logging.WARNING if estado >= 400 else logging.INFO, evento
                    )
            await send(mensaje)

        await self.app(scope, receive, responder)
