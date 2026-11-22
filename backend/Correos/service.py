"""Bandeja persistente: conserva mensajes cifrados hasta entregarlos o vencer."""

import base64
import hashlib
import json
import logging
from datetime import datetime, timedelta
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import select
from core.config import revision
from backend.Correos.tabla import CorreosPendientes

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
    db.add(mensaje)
    db.flush()
    return mensaje.id


def procesar_correo(db, id, enviar=None):
    mensaje = db.execute(
        select(CorreosPendientes)
        .where(CorreosPendientes.id == id, CorreosPendientes.estado == "pendiente")
        .with_for_update(skip_locked=True)
    ).scalar_one_or_none()
    if not mensaje:
        return
    ahora = datetime.utcnow()
    if mensaje.vencimiento <= ahora:
        mensaje.estado = "vencido"
        mensaje.contenido_cifrado = None
        db.commit()
        return
    if mensaje.proximo_intento > ahora:
        return
    mensaje.intentos += 1
    try:
        datos = json.loads(cifrador().decrypt(mensaje.contenido_cifrado.encode()))
        if enviar is None:
            from utils.correo import (
                enviar_recuperacion,
                enviar_invitacion,
            )

            enviar = {
                "recuperacion": enviar_recuperacion,
                "invitacion": enviar_invitacion,
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
        mensaje.proximo_intento = ahora + timedelta(seconds=30 * 2**mensaje.intentos)
        registro.warning(
            "correo_reintento id=%s intento=%s", mensaje.id, mensaje.intentos
        )
    db.commit()
