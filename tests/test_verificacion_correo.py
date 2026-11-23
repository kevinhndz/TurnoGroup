import json
from datetime import datetime, timedelta
import pytest
from fastapi import BackgroundTasks, HTTPException
from backend.Usuarios.schema import (
    SolicitarVerificacionCorreo,
    ConfirmarVerificacionCorreo,
)
from backend.Usuarios.verificacion import VerificacionCorreoService as servicio
from backend.Usuarios.verificaciones_correo import VerificacionesCorreo
from backend.Correos.tabla import CorreosPendientes
from backend.Correos.service import cifrador
from backend.Usuarios.tabla import Usuarios
from core.config import revision


@pytest.fixture
def correo(db, monkeypatch):
    for nombre in ("SMTP_SERVIDOR", "SMTP_USUARIO", "SMTP_CLAVE", "SMTP_REMITENTE"):
        monkeypatch.setattr(revision, nombre, "prueba")
    correo = "nuevo-registro@example.com"
    servicio.solicitar(
        SolicitarVerificacionCorreo(correo=correo), db, BackgroundTasks()
    )
    mensaje = db.query(CorreosPendientes).filter_by(tipo="verificacion").one()
    codigo = json.loads(cifrador().decrypt(mensaje.contenido_cifrado.encode()))[
        "codigo"
    ]
    return correo, codigo


def test_verificar_no_crea_cuenta_y_no_guarda_codigo_en_claro(db, correo):
    direccion, codigo = correo
    assert db.query(Usuarios).filter_by(correo=direccion).first() is None
    assert db.query(VerificacionesCorreo).one().codigo_protegido != codigo
    respuesta = servicio.confirmar(
        ConfirmarVerificacionCorreo(correo=direccion, codigo=codigo), db
    )
    assert (
        db.query(VerificacionesCorreo).one().comprobante_protegido
        != respuesta["comprobante_correo"]
    )
    with pytest.raises(HTTPException):
        servicio.confirmar(
            ConfirmarVerificacionCorreo(correo=direccion, codigo=codigo), db
        )


@pytest.mark.parametrize("caso", ["vencido", "otro_correo", "incorrecto"])
def test_rechaza_verificaciones_invalidas(db, correo, caso):
    direccion, codigo = correo
    if caso == "vencido":
        db.query(VerificacionesCorreo).one().vencimiento = (
            datetime.utcnow() - timedelta(seconds=1)
        )
        db.commit()
    if caso == "otro_correo":
        direccion = "ajeno@example.com"
    if caso == "incorrecto":
        codigo = "x" * 43
    with pytest.raises(HTTPException):
        servicio.confirmar(
            ConfirmarVerificacionCorreo(correo=direccion, codigo=codigo), db
        )


def test_comprobante_no_se_presta_a_otro_correo_ni_se_reutiliza(db, correo):
    direccion, codigo = correo
    comprobante = servicio.confirmar(
        ConfirmarVerificacionCorreo(correo=direccion, codigo=codigo), db
    )["comprobante_correo"]
    with pytest.raises(HTTPException):
        servicio.consumir("ajeno@example.com", comprobante, db)
    servicio.consumir(direccion, comprobante, db)
    db.commit()
    with pytest.raises(HTTPException):
        servicio.consumir(direccion, comprobante, db)


def test_registro_exige_comprobante(client):
    from test_registro_seguro import datos_registro

    client.cookies.clear()
    assert (
        client.post("/usuarios/registro-negocio", json=datos_registro()).status_code
        == 422
    )
