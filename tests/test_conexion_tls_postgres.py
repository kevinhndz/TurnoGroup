import os
from pathlib import Path

import certifi
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError

from database.conexion import preparar_url_bd


@pytest.fixture
def destino_tls():
    # Solo conecto estas pruebas a una base local creada para pytest.
    url = os.environ.get("TEST_DATABASE_URL")
    certificado = os.environ.get("TEST_DATABASE_SSL_ROOT_CERT")
    if not url or not certificado:
        pytest.skip("Falta PostgreSQL local con certificado TLS de prueba")
    destino = make_url(url)
    assert destino.host == "127.0.0.1"
    assert destino.database.endswith("_pytest")
    assert Path(certificado).is_file()
    return destino, certificado


def test_postgres_conecta_con_ca_y_nombre_correctos(destino_tls):
    destino, certificado = destino_tls
    url = preparar_url_bd(destino.render_as_string(hide_password=False), certificado)
    motor = create_engine(url, connect_args={"connect_timeout": 5})
    try:
        with motor.connect() as conexion:
            assert (
                conexion.execute(
                    text("SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()")
                ).scalar()
                is True
            )
    finally:
        motor.dispose()


def test_postgres_rechaza_otra_ca(destino_tls):
    destino, _ = destino_tls
    url = preparar_url_bd(
        destino.render_as_string(hide_password=False), certifi.where()
    )
    motor = create_engine(url, connect_args={"connect_timeout": 5})
    try:
        with pytest.raises(OperationalError, match="certificate"):
            with motor.connect():
                pass
    finally:
        motor.dispose()


def test_postgres_rechaza_nombre_distinto(destino_tls):
    destino, certificado = destino_tls
    # El certificado de CI solo incluye 127.0.0.1; localhost no debe pasar.
    destino = destino.set(host="localhost")
    url = preparar_url_bd(destino.render_as_string(hide_password=False), certificado)
    motor = create_engine(url, connect_args={"connect_timeout": 5})
    try:
        with pytest.raises(OperationalError, match="certificate"):
            with motor.connect():
                pass
    finally:
        motor.dispose()
