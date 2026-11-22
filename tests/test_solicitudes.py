from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from utils.solicitudes import LimitarSolicitudes


def cliente():
    app = FastAPI()
    app.add_middleware(LimitarSolicitudes)

    @app.post("/prueba")
    async def recibir(request: Request):
        return {"bytes": len(await request.body())}

    return TestClient(app)


def test_cuerpo_normal_llega_completo():
    respuesta = cliente().post("/prueba", content=b"hola")
    assert respuesta.json() == {"bytes": 4}


def test_rechaza_cuerpo_grande():
    respuesta = cliente().post("/prueba", content=b"a" * 1_000_001)
    assert respuesta.status_code == 413


def test_rechaza_fragmentos_sin_content_length():
    respuesta = cliente().post(
        "/prueba", content=iter([b"a" * 600_000, b"b" * 600_000])
    )
    assert respuesta.status_code == 413
