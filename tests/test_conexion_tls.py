from pathlib import Path

import certifi
import pytest
from sqlalchemy import create_engine

from database.conexion import CA_SUPABASE, preparar_url_bd


@pytest.mark.parametrize(
    "driver", ["postgresql", "postgresql+psycopg", "postgresql+psycopg2"]
)
def test_supabase_exige_certificado_y_nombre(driver):
    # Reviso las opciones que recibe el driver sin abrir una conexion externa.
    url = preparar_url_bd(
        f"{driver}://usuario:clave@ejemplo.pooler.supabase.com:5432/postgres"
    )
    motor = create_engine(url)
    try:
        _, opciones = motor.dialect.create_connect_args(url)
        assert opciones["sslmode"] == "verify-full"
        assert opciones["sslrootcert"] == str(CA_SUPABASE)
        assert opciones["ssl_min_protocol_version"] == "TLSv1.2"
        assert opciones["gssencmode"] == "disable"
    finally:
        motor.dispose()


@pytest.mark.parametrize("modo", ["disable", "allow", "prefer", "require", "verify-ca"])
def test_remoto_rechaza_tls_debil(modo):
    with pytest.raises(ValueError, match="verify-full"):
        preparar_url_bd(f"postgresql://usuario:clave@db.example.com/app?sslmode={modo}")


@pytest.mark.parametrize(
    "parametro", ["host", "hostaddr", "service", "servicefile", "port"]
)
def test_no_permite_cambiar_servidor_por_parametros(parametro):
    with pytest.raises(ValueError, match="servidor"):
        preparar_url_bd(f"postgresql://usuario:clave@localhost/app?{parametro}=otro")


def test_no_acepta_parametros_repetidos():
    with pytest.raises(ValueError, match="un valor"):
        preparar_url_bd(
            "postgresql://usuario:clave@db.example.com/app?sslmode=disable&sslmode=verify-full"
        )


def test_remoto_rechaza_tls_antiguo():
    with pytest.raises(ValueError, match="TLS 1.2"):
        preparar_url_bd(
            "postgresql://usuario:clave@db.example.com/app?ssl_min_protocol_version=TLSv1"
        )


@pytest.mark.parametrize(
    "url",
    [
        "sqlite://",
        "postgresql://usuario@127.0.0.1/app",
        "postgresql://usuario@localhost/app",
        "postgresql://usuario@[::1]/app",
    ],
)
def test_pruebas_locales_conservan_su_conexion(url):
    assert preparar_url_bd(url).render_as_string(hide_password=False) == url


def test_certificado_personalizado(tmp_path):
    archivo = tmp_path / "raiz.crt"
    archivo.write_bytes(Path(certifi.where()).read_bytes())
    url = preparar_url_bd("postgresql://usuario:clave@db.example.com/app", str(archivo))
    assert url.query["sslrootcert"] == str(archivo)
    assert url.query["sslmode"] == "verify-full"


@pytest.mark.parametrize("existe", [False, True])
def test_certificado_ausente_o_invalido(tmp_path, existe):
    archivo = tmp_path / "raiz.crt"
    if existe:
        archivo.write_text("esto no es un certificado")
    with pytest.raises(ValueError, match="certificado raiz"):
        preparar_url_bd("postgresql://usuario:clave@db.example.com/app", str(archivo))


def test_nombre_parecido_a_supabase_no_recibe_su_ca():
    url = preparar_url_bd("postgresql://usuario@supabase.com.otro.example/app")
    assert url.query["sslrootcert"] == certifi.where()


def test_error_no_muestra_credenciales():
    with pytest.raises(ValueError) as error:
        preparar_url_bd("postgresql://usuario:clave-privada@db.example.com:puerto/app")
    assert "clave-privada" not in str(error.value)
