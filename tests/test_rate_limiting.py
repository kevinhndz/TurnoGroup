import pytest
from fastapi import HTTPException

from utils.rate_limiting import limpiar_limites, limitar_por_ip


def solicitud(ip="127.0.0.1"):
    return type("Solicitud", (), {"client": type("Cliente", (), {"host": ip})()})()


def setup_function():
    limpiar_limites()


def test_permite_hasta_el_limite():
    for _ in range(2):
        limitar_por_ip(solicitud(), "login", 2, 60)


def test_rechaza_el_siguiente_intento():
    limitar_por_ip(solicitud(), "login", 1, 60)

    with pytest.raises(HTTPException) as error:
        limitar_por_ip(solicitud(), "login", 1, 60)

    assert error.value.status_code == 429
    assert error.value.headers["Retry-After"]


def test_separa_las_ips():
    limitar_por_ip(solicitud("10.0.0.1"), "login", 1, 60)
    limitar_por_ip(solicitud("10.0.0.2"), "login", 1, 60)


def test_no_confia_en_ip_sin_secreto(monkeypatch):
    from core.config import revision
    from utils.rate_limiting import obtener_ip

    monkeypatch.setattr(revision, "BACKEND_PROXY_SECRET", "secreto")
    request = solicitud("10.0.0.1")
    request.headers = {"X-TurnoGroup-Client-IP": "203.0.113.1"}
    assert obtener_ip(request) == "10.0.0.1"


def test_proxy_identifica_cliente(monkeypatch):
    from core.config import revision
    from utils.rate_limiting import obtener_ip

    monkeypatch.setattr(revision, "BACKEND_PROXY_SECRET", "secreto")
    request = solicitud("10.0.0.1")
    request.headers = {
        "X-TurnoGroup-Proxy-Secret": "secreto",
        "X-TurnoGroup-Client-IP": "203.0.113.1",
    }
    assert obtener_ip(request) == "203.0.113.1"


def test_redis_caido_no_permite_intentos(monkeypatch):
    from redis import ConnectionError
    from core.config import revision
    from utils import rate_limiting

    class RedisCaido:
        def eval(self, *args):
            raise ConnectionError("dato que no debe salir en respuesta")

    monkeypatch.setattr(revision, "REDIS_URL", "redis://localhost:6379/15")
    monkeypatch.setattr(rate_limiting, "conexion_redis", lambda url: RedisCaido())
    with pytest.raises(HTTPException) as error:
        limitar_por_ip(solicitud(), "login", 1, 60)
    assert error.value.status_code == 503
    assert "dato" not in error.value.detail


def test_redis_comparte_contador_y_expira(monkeypatch):
    import os
    import uuid
    from redis import Redis
    from core.config import revision
    from utils.rate_limiting import limitar_compartido, conexion_redis

    url = os.environ.get("TEST_REDIS_URL")
    if not url:
        pytest.skip("Requiere Redis de pruebas")
    cliente = Redis.from_url(url)
    cliente.ping()
    monkeypatch.setattr(revision, "REDIS_URL", url)
    nombre = "pytest-" + uuid.uuid4().hex
    limitar_compartido(nombre, "prueba", 1, 60)
    conexion_redis.cache_clear()
    with pytest.raises(HTTPException) as error:
        limitar_compartido(nombre, "prueba", 1, 60)
    assert error.value.status_code == 429
    claves = list(cliente.scan_iter("turnogroup:limites:" + nombre + ":*"))
    assert len(claves) == 1
    assert 0 < cliente.ttl(claves[0]) <= 60
    cliente.delete(*claves)
