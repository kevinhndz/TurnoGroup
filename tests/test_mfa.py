import pyotp
import pytest
from fastapi import HTTPException
from backend.Usuarios.tabla import Usuarios
from backend.Correos.service import cifrador
from core.config import revision
from utils.mfa import verificar_mfa


def test_codigo_correcto_y_repetido():
    secreto = pyotp.random_base32()
    usuario = Usuarios(
        mfa_secreto_cifrado=cifrador().encrypt(secreto.encode()).decode()
    )
    codigo = pyotp.TOTP(secreto).now()
    verificar_mfa(usuario, codigo)
    with pytest.raises(HTTPException) as error:
        verificar_mfa(usuario, codigo)
    assert error.value.status_code == 401


def test_codigo_incorrecto():
    usuario = Usuarios(
        mfa_secreto_cifrado=cifrador().encrypt(pyotp.random_base32().encode()).decode()
    )
    with pytest.raises(HTTPException):
        verificar_mfa(usuario, "no")


def test_produccion_exige_mfa_para_plataforma(monkeypatch):
    monkeypatch.setattr(revision, "ENTORNO", "produccion")
    with pytest.raises(HTTPException) as error:
        verificar_mfa(Usuarios(rol_plataforma="Superadministrador"), None)
    assert error.value.status_code == 403


def test_usuario_sin_mfa_conserva_acceso(monkeypatch):
    monkeypatch.setattr(revision, "ENTORNO", "produccion")
    verificar_mfa(Usuarios(rol_plataforma="Usuario"), None)
