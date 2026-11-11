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
