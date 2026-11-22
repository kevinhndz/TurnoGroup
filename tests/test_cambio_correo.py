from datetime import datetime, timedelta
import pytest
from fastapi import BackgroundTasks, HTTPException
from backend.Usuarios.tabla import Usuarios
from backend.Usuarios.schema import (
    SolicitarCambioCorreo,
    ConfirmarCambioCorreo,
    Revisar_Json_Editar_Usuario,
)
from backend.Usuarios.seguridad import SeguridadUsuarioService as servicio
from backend.Usuarios.service import UsuarioService
from backend.Usuarios.cambios_correo import CambiosCorreo
from backend.Correos.tabla import CorreosPendientes
from backend.Correos.service import cifrador
from utils.hash import encriptar_contrasena
from core.config import revision
import json


@pytest.fixture
def usuario(db, monkeypatch):
    for nombre in ("SMTP_SERVIDOR", "SMTP_USUARIO", "SMTP_CLAVE", "SMTP_REMITENTE"):
        monkeypatch.setattr(revision, nombre, "prueba")
    usuario = Usuarios(
        correo="anterior@example.com",
        nombre="Prueba",
        clave_protegida=encriptar_contrasena("Prueba-segura123"),
    )
    db.add(usuario)
    db.commit()
    return usuario


def solicitar(db, usuario):
    servicio.solicitar(
        SolicitarCambioCorreo(
            correo_nuevo="nuevo@example.com", clave_actual="Prueba-segura123"
        ),
        usuario.id,
        db,
        BackgroundTasks(),
    )
    mensaje = db.query(CorreosPendientes).filter_by(tipo="cambio_correo").one()
    return json.loads(cifrador().decrypt(mensaje.contenido_cifrado.encode()))["codigo"]


def test_no_cambia_hasta_confirmar_y_no_reutiliza(db, usuario):
    codigo = solicitar(db, usuario)
    assert usuario.correo == "anterior@example.com"
    datos = ConfirmarCambioCorreo(codigo=codigo, clave_actual="Prueba-segura123")
    servicio.confirmar(datos, usuario.id, db, BackgroundTasks())
    assert usuario.correo == "nuevo@example.com"
    with pytest.raises(HTTPException) as error:
        servicio.confirmar(datos, usuario.id, db, BackgroundTasks())
    assert error.value.status_code == 400


def test_requiere_contrasena_correcta(db, usuario):
    with pytest.raises(HTTPException) as error:
        servicio.solicitar(
            SolicitarCambioCorreo(
                correo_nuevo="nuevo@example.com", clave_actual="incorrecta"
            ),
            usuario.id,
            db,
            BackgroundTasks(),
        )
    assert error.value.status_code == 401


def test_rechaza_codigo_vencido(db, usuario):
    codigo = solicitar(db, usuario)
    db.query(CambiosCorreo).one().vencimiento = datetime.utcnow() - timedelta(minutes=1)
    db.commit()
    with pytest.raises(HTTPException):
        servicio.confirmar(
            ConfirmarCambioCorreo(codigo=codigo, clave_actual="Prueba-segura123"),
            usuario.id,
            db,
            BackgroundTasks(),
        )
    assert usuario.correo == "anterior@example.com"


def test_no_permite_saltar_verificacion_con_patch(db, usuario):
    with pytest.raises(HTTPException) as error:
        UsuarioService.editar_usuario_service(
            Revisar_Json_Editar_Usuario(correo="nuevo@example.com"), usuario.id, db
        )
    assert error.value.status_code == 403
