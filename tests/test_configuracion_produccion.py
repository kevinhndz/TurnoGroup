import pytest
from pydantic import ValidationError

from core.config import GuardiaSeguridad


def configuracion(**cambios):
    datos = dict(
        _env_file=None,
        ENTORNO="produccion",
        REDIS_URL="redis://redis:6379/0",
        DATABASE_URL="postgresql://app:clave@db.example/turno",
        SECRET_KEY="a" * 40,
        BACKEND_PROXY_SECRET="b" * 40,
        COOKIE_SEGURA=True,
        URL_FRONTEND="https://turno.example",
        ORIGENES_PERMITIDOS=["https://turno.example"],
        CORREO_CLAVE_CIFRADO="YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXphYmNkZWY=",
        SMTP_SERVIDOR="smtp.example",
        SMTP_USUARIO="usuario",
        SMTP_CLAVE="secreto",
        SMTP_REMITENTE="correo@example.com",
    )
    datos.update(cambios)
    return GuardiaSeguridad(**datos)


def test_acepta_configuracion_segura():
    assert configuracion().COOKIE_SEGURA


@pytest.mark.parametrize(
    "cambios",
    [
        {"COOKIE_SEGURA": False},
        {"SECRET_KEY": "corta"},
        {"BACKEND_PROXY_SECRET": ""},
        {"BACKEND_PROXY_SECRET": "a" * 40},
        {"URL_FRONTEND": "http://localhost:3000"},
        {"ORIGENES_PERMITIDOS": ["*"]},
        {"DATABASE_URL": "sqlite://"},
        {"SMTP_CLAVE": ""},
    ],
)
def test_rechaza_produccion_insegura(cambios):
    with pytest.raises(ValidationError):
        configuracion(**cambios)


def test_desarrollo_conserva_configuracion_local():
    assert (
        configuracion(ENTORNO="desarrollo", COOKIE_SEGURA=False).ENTORNO == "desarrollo"
    )
