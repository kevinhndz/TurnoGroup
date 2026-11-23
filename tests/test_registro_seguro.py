from collections import Counter
from http.cookies import SimpleCookie

import pytest
from fastapi.routing import iter_route_contexts

from backend.Sesiones.tabla import Sesiones
from core.config import revision
from main import app
from utils.token import proteger_token_sesion


def datos_registro():
    # Uso una cuenta nueva para revisar el registro completo.
    return {
        "cuenta": {
            "correo": "registro-seguro@example.com",
            "nombre": "Persona de prueba",
            "clave": "Clave de prueba segura 123",
        },
        "negocio": {
            "nombre": "Negocio de registro seguro",
            "tipo_negocio": "Otro",
            "codigo_pais": "HN",
            "codigo_moneda": "HNL",
            "zona_horaria": "America/Tegucigalpa",
        },
        "sucursales": [
            {
                "id_local": 1,
                "nombre": "Principal",
                "direccion": "Direccion de prueba",
                "es_principal": True,
                "servicios": {"comer_aqui": {"habilitado": True}},
                "pagos": ["efectivo"],
            }
        ],
        "tarjeta_suscripcion": {
            "tarjeta_prueba": "visa",
            "titular": "Persona de prueba",
            "mes": 12,
            "anio": 2099,
        },
    }


def test_rutas_no_se_repiten():
    # Reviso las rutas reales porque OpenAPI puede ocultar los duplicados.
    rutas = Counter(
        (metodo, ruta.path)
        for ruta in iter_route_contexts(app.routes)
        for metodo in (getattr(ruta, "methods", None) or [])
    )
    repetidas = [ruta for ruta, cantidad in rutas.items() if cantidad > 1]
    assert repetidas == []


def test_registro_guarda_token_solo_en_cookie(client, db, verificar_correo_registro):
    client.cookies.clear()
    respuesta = client.post(
        "/usuarios/registro-negocio", json=verificar_correo_registro(datos_registro())
    )
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert isinstance(datos, dict)
    token = respuesta.cookies["sesion_turnogroup"]
    assert token not in respuesta.text
    assert "clave_protegida" not in respuesta.text
    sesion = (
        db.query(Sesiones)
        .filter(Sesiones.token_protegido == proteger_token_sesion(token))
        .one()
    )
    assert sesion.id_usuario == datos["usuario"]["id"]
    assert respuesta.headers["cache-control"] == "no-store"
    assert client.get("/sesiones/actual").status_code == 200
    assert client.get("/productos/").status_code == 200
    assert client.post("/sesiones/cerrar").status_code == 204
    assert client.get("/sesiones/actual").status_code == 401


@pytest.mark.parametrize("segura", [False, True])
def test_cookie_registro_respeta_https(
    client, monkeypatch, segura, verificar_correo_registro
):
    client.cookies.clear()
    monkeypatch.setattr(revision, "COOKIE_SEGURA", segura)
    monkeypatch.setattr(revision, "BACKEND_PROXY_SECRET", "clave-de-prueba")
    cabeceras = {}
    if segura:
        # Simulo la senal que Next manda despues de recibir HTTPS en Nginx.
        cabeceras = {
            "X-Forwarded-Proto": "https",
            "X-TurnoGroup-Proxy-Secret": "clave-de-prueba",
        }
    respuesta = client.post(
        "http://testserver/usuarios/registro-negocio",
        json=verificar_correo_registro(datos_registro()),
        headers=cabeceras,
    )
    assert respuesta.status_code == 201
    cookies = SimpleCookie()
    cookies.load(respuesta.headers["set-cookie"])
    cookie = cookies["sesion_turnogroup"]
    assert cookie["httponly"]
    assert bool(cookie["secure"]) is segura
    assert cookie["samesite"] == "lax"
    assert cookie["path"] == "/"
    assert int(cookie["max-age"]) > 0
