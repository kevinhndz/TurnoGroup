"""Segundo factor con codigos temporales y proteccion contra reutilizacion."""

import pyotp
from cryptography.fernet import InvalidToken
from fastapi import HTTPException
from backend.Correos.service import cifrador
from core.config import revision


def verificar_mfa(usuario, codigo):
    if not usuario.mfa_secreto_cifrado:
        if (
            usuario.rol_plataforma == "Superadministrador"
            and revision.ENTORNO == "produccion"
        ):
            raise HTTPException(
                403, "Configura el segundo factor de la cuenta de plataforma"
            )
        return
    try:
        secreto = cifrador().decrypt(usuario.mfa_secreto_cifrado.encode()).decode()
        contador = pyotp.TOTP(secreto).verify_and_get_timecode(
            codigo or "", valid_window=1
        )
    except (InvalidToken, ValueError, pyotp.OTPVerificationError):
        raise HTTPException(401, "Codigo de autenticador incorrecto") from None
    if (
        usuario.mfa_ultimo_contador is not None
        and contador <= usuario.mfa_ultimo_contador
    ):
        raise HTTPException(401, "Espera un codigo nuevo del autenticador")
    # El servicio de login bloquea la fila hasta guardar la sesion y este contador.
    usuario.mfa_ultimo_contador = contador


def generar_codigos_respaldo(db, usuario):
    from secrets import token_urlsafe
    from backend.Usuarios.repository import UsuarioRepository
    from utils.token import proteger_token_sesion

    codigos = [token_urlsafe(18) for _ in range(10)]
    UsuarioRepository.reemplazar_codigos_mfa(
        db, usuario.id, [proteger_token_sesion(codigo) for codigo in codigos]
    )
    return codigos


def verificar_segundo_factor(usuario, codigo, respaldo, db):
    if not respaldo:
        verificar_mfa(usuario, codigo)
        return
    from datetime import datetime
    from backend.Usuarios.repository import UsuarioRepository
    from utils.token import proteger_token_sesion

    if codigo or not usuario.mfa_secreto_cifrado:
        raise HTTPException(401, "Usa el autenticador o un codigo de respaldo")
    usados = UsuarioRepository.consumir_codigo_mfa(
        db, usuario.id, proteger_token_sesion(respaldo), datetime.utcnow()
    )
    if usados != 1:
        raise HTTPException(401, "El codigo de respaldo no es valido o ya fue usado")
