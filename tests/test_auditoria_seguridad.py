import logging
import pytest
import json
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from utils.auditoria_seguridad import AuditoriaSeguridad


@pytest.fixture(autouse=True)
def capturar_auditoria(caplog):
    registro = logging.getLogger("turnogroup.seguridad")
    registro.addHandler(caplog.handler)
    yield
    registro.removeHandler(caplog.handler)


def test_registra_rechazo_sin_secretos(caplog):
    app = FastAPI()
    app.add_middleware(AuditoriaSeguridad)

    @app.post("/sesiones/iniciar")
    def iniciar():
        raise HTTPException(401, "No autorizado")

    with caplog.at_level(logging.INFO, logger="turnogroup.seguridad"):
        respuesta = TestClient(app).post(
            "/sesiones/iniciar?codigo=secreto-query",
            json={"clave": "secreto-body"},
            headers={"Cookie": "sesion_turnogroup=secreto-cookie"},
        )
    assert respuesta.headers["x-request-id"]
    assert "acceso_rechazado" in caplog.text
    assert "secreto" not in caplog.text


def test_registra_operacion_exitosa_sin_cambiar_nivel_de_logging(caplog):
    app = FastAPI()
    app.add_middleware(AuditoriaSeguridad)

    @app.post("/usuarios/{id}")
    def editar(id: int):
        return {"resultado": "guardado"}

    respuesta = TestClient(app).post("/usuarios/7", json={"clave": "secreto-body"})
    eventos = [
        json.loads(item.message)
        for item in caplog.records
        if item.name == "turnogroup.seguridad"
    ]
    assert eventos[-1]["evento"] == "operacion_sensible"
    assert eventos[-1]["ruta"] == "/usuarios/{id}"
    assert eventos[-1]["solicitud"] == respuesta.headers["x-request-id"]
    assert "secreto-body" not in caplog.text


def test_error_interno_no_guarda_excepcion_con_secretos(caplog):
    app = FastAPI()
    app.add_middleware(AuditoriaSeguridad)

    @app.post("/usuarios/ejemplo")
    def fallar():
        raise RuntimeError("secreto-excepcion")

    respuesta = TestClient(app, raise_server_exceptions=False).post("/usuarios/ejemplo")
    assert respuesta.status_code == 500
    assert "error_interno" in caplog.text
    assert "secreto-excepcion" not in caplog.text


def test_archivo_guarda_info_con_permisos_privados_y_no_duplica(tmp_path, monkeypatch):
    from utils.registro_seguridad import configurar_auditoria
    from core.config import revision

    registro = logging.getLogger("turnogroup.seguridad")
    anteriores = registro.handlers[:]
    registro.handlers = []
    archivo = tmp_path / "auditoria.log"
    monkeypatch.setattr(revision, "AUDITORIA_ARCHIVO", str(archivo))
    try:
        configurar_auditoria()
        configurar_auditoria()
        registro.info('{"evento":"prueba_exitosa"}')
        assert archivo.read_text().count("prueba_exitosa") == 1
        assert archivo.stat().st_mode & 0o777 == 0o600
        handler = registro.handlers[0]
        handler.doRollover()
        registro.info('{"evento":"despues_de_rotar"}')
        assert "despues_de_rotar" in archivo.read_text()
        assert archivo.stat().st_mode & 0o777 == 0o600
    finally:
        for handler in registro.handlers:
            handler.close()
        registro.handlers = anteriores
