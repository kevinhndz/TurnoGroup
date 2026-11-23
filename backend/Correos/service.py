"""Bandeja persistente: conserva mensajes cifrados hasta entregarlos o vencer."""

import base64
import hashlib
import json
import logging
from datetime import datetime, timedelta

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.exc import SQLAlchemyError

from backend.Correos.repository import CorreoRepository as repo
from backend.Correos.tabla import CorreosPendientes
from core.config import revision
from utils.correo import (
    enviar_aviso_correo,
    enviar_cambio_correo,
    enviar_invitacion,
    enviar_recuperacion,
    enviar_verificacion,
)

registro = logging.getLogger("turnogroup.seguridad")


def cifrador():
    # La clave se mantiene fuera de PostgreSQL. No se guardan codigos en claro.
    clave = revision.CORREO_CLAVE_CIFRADO

    if not clave:
        clave = base64.urlsafe_b64encode(
            hashlib.sha256(revision.SECRET_KEY.encode()).digest()
        )

    return Fernet(clave)


def encolar_correo(db, tipo, correo, codigo, vencimiento):
    contenido = json.dumps({"correo": correo, "codigo": codigo}).encode()
    mensaje = CorreosPendientes(
        tipo=tipo,
        contenido_cifrado=cifrador().encrypt(contenido).decode(),
        estado="pendiente",
        intentos=0,
        proximo_intento=datetime.utcnow(),
        vencimiento=vencimiento,
    )
    repo.agregar(db, mensaje)
    repo.guardar_cambios(db)

    return mensaje.id


def procesar_correo(db, id, enviar=None):
    try:
        mensaje = repo.buscar_mensaje_pendiente(db, id)

        if not mensaje:
            return
        ahora = datetime.utcnow()

        if mensaje.vencimiento <= ahora:
            mensaje.estado = "vencido"
            mensaje.contenido_cifrado = None
            repo.guardar_cambios(db)
            db.commit()

            return

        if mensaje.proximo_intento > ahora:
            return
        mensaje.intentos += 1

        try:
            datos = json.loads(cifrador().decrypt(mensaje.contenido_cifrado.encode()))

            if enviar is None:
                enviar = {
                    "verificacion": enviar_verificacion,
                    "recuperacion": enviar_recuperacion,
                    "invitacion": enviar_invitacion,
                    "cambio_correo": enviar_cambio_correo,
                    "aviso_correo": enviar_aviso_correo,
                }[mensaje.tipo]
            correcto = enviar(datos["correo"], datos["codigo"]) is not False
        except (InvalidToken, ValueError, KeyError):
            correcto = False

        if correcto:
            mensaje.estado = "enviado"
            mensaje.fecha_envio = ahora
            mensaje.contenido_cifrado = None
        elif mensaje.intentos >= 5:
            mensaje.estado = "fallido"
            mensaje.contenido_cifrado = None
            registro.error("correo_agotado id=%s tipo=%s", mensaje.id, mensaje.tipo)
        else:
            mensaje.proximo_intento = ahora + timedelta(
                seconds=30 * 2**mensaje.intentos
            )
            registro.warning(
                "correo_reintento id=%s intento=%s", mensaje.id, mensaje.intentos
            )
        repo.guardar_cambios(db)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
