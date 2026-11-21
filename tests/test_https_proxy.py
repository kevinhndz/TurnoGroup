import pytest
from fastapi import HTTPException, Response
from starlette.requests import Request

from backend.Sesiones.router import poner_cookie
from core.config import revision
from utils.autorizacion import revisar_solicitud_sesion


def solicitud(esquema="http", cabeceras=None):
    return Request(
        {
            "type": "http",
            "scheme": esquema,
            "method": "POST",
            "path": "/sesiones/iniciar",
            "headers": [
                (clave.lower().encode(), valor.encode())
                for clave, valor in (cabeceras or {}).items()
            ],
            "client": ("203.0.113.10", 4000),
        }
    )


def test_rechaza_cabecera_https_falsa(monkeypatch):
    monkeypatch.setattr(revision, "COOKIE_SEGURA", True)
    monkeypatch.setattr(revision, "BACKEND_PROXY_SECRET", "clave-de-prueba")
    with pytest.raises(HTTPException) as error:
        revisar_solicitud_sesion(solicitud(cabeceras={"X-Forwarded-Proto": "https"}))
    assert error.value.status_code == 400


def test_rechaza_secreto_incorrecto(monkeypatch):
    monkeypatch.setattr(revision, "COOKIE_SEGURA", True)
    monkeypatch.setattr(revision, "BACKEND_PROXY_SECRET", "clave-de-prueba")
    with pytest.raises(HTTPException) as error:
        revisar_solicitud_sesion(
            solicitud(
                cabeceras={
                    "X-Forwarded-Proto": "https",
                    "X-TurnoGroup-Proxy-Secret": "otra-clave",
                }
            )
        )
    assert error.value.status_code == 400


def test_no_confia_en_esquema_indicado_por_otro_proxy(monkeypatch):
    monkeypatch.setattr(revision, "COOKIE_SEGURA", True)
    monkeypatch.setattr(revision, "BACKEND_PROXY_SECRET", "clave-de-prueba")
    with pytest.raises(HTTPException) as error:
        revisar_solicitud_sesion(solicitud(esquema="https"))
    assert error.value.status_code == 400


def test_acepta_https_del_proxy_verificado(monkeypatch):
    monkeypatch.setattr(revision, "COOKIE_SEGURA", True)
    monkeypatch.setattr(revision, "BACKEND_PROXY_SECRET", "clave-de-prueba")
    revisar_solicitud_sesion(
        solicitud(
            cabeceras={
                "X-Forwarded-Proto": "https",
                "X-TurnoGroup-Proxy-Secret": "clave-de-prueba",
                "X-Solicitud": "TurnoGroup",
            }
        )
    )


def test_cookie_de_produccion_es_segura(monkeypatch):
    from datetime import datetime, timedelta, timezone

    monkeypatch.setattr(revision, "COOKIE_SEGURA", True)
    respuesta = Response()
    poner_cookie(
        respuesta,
        "token-de-prueba",
        datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1),
    )
    cookie = respuesta.headers["set-cookie"]
    assert "Secure" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie
