import logging
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from utils.auditoria_seguridad import AuditoriaSeguridad


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
