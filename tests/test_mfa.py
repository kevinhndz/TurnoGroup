import pyotp
import pytest
from fastapi import HTTPException
from backend.Usuarios.tabla import Usuarios
from backend.Correos.service import cifrador
from core.config import revision
from utils.mfa import verificar_mfa


def test_codigo_correcto_y_repetido():
    secreto = pyotp.random_base32()
    usuario = Usuarios(
        mfa_secreto_cifrado=cifrador().encrypt(secreto.encode()).decode()
    )
    codigo = pyotp.TOTP(secreto).now()
    verificar_mfa(usuario, codigo)
    with pytest.raises(HTTPException) as error:
        verificar_mfa(usuario, codigo)
    assert error.value.status_code == 401


def test_codigo_incorrecto():
    usuario = Usuarios(
        mfa_secreto_cifrado=cifrador().encrypt(pyotp.random_base32().encode()).decode()
    )
    with pytest.raises(HTTPException):
        verificar_mfa(usuario, "no")


def test_produccion_exige_mfa_para_plataforma(monkeypatch):
    monkeypatch.setattr(revision, "ENTORNO", "produccion")
    with pytest.raises(HTTPException) as error:
        verificar_mfa(Usuarios(rol_plataforma="Superadministrador"), None)
    assert error.value.status_code == 403


def test_usuario_sin_mfa_conserva_acceso(monkeypatch):
    monkeypatch.setattr(revision, "ENTORNO", "produccion")
    verificar_mfa(Usuarios(rol_plataforma="Usuario"), None)


def test_respaldo_se_guarda_como_hash_y_solo_sirve_una_vez(db):
    from backend.Usuarios.codigos_mfa import CodigosRecuperacionMfa
    from utils.mfa import generar_codigos_respaldo, verificar_segundo_factor

    usuario = Usuarios(
        nombre="Plataforma",
        correo="mfa@example.com",
        mfa_secreto_cifrado=cifrador().encrypt(pyotp.random_base32().encode()).decode(),
    )
    db.add(usuario)
    db.flush()
    codigos = generar_codigos_respaldo(db, usuario)
    db.commit()
    assert len(codigos) == 10
    assert all(
        item.codigo_protegido not in codigos
        for item in db.query(CodigosRecuperacionMfa).all()
    )
    verificar_segundo_factor(usuario, None, codigos[0], db)
    db.commit()
    with pytest.raises(HTTPException):
        verificar_segundo_factor(usuario, None, codigos[0], db)


def test_regenerar_invalida_respaldo_anterior(db):
    from utils.mfa import generar_codigos_respaldo, verificar_segundo_factor

    usuario = Usuarios(
        nombre="Plataforma",
        correo="rotacion@example.com",
        mfa_secreto_cifrado="configurado",
    )
    db.add(usuario)
    db.flush()
    anterior = generar_codigos_respaldo(db, usuario)[0]
    db.flush()
    nuevo = generar_codigos_respaldo(db, usuario)[0]
    db.commit()
    with pytest.raises(HTTPException):
        verificar_segundo_factor(usuario, None, anterior, db)
    verificar_segundo_factor(usuario, None, nuevo, db)


def test_respaldo_no_pertenece_a_otra_cuenta(db):
    from utils.mfa import generar_codigos_respaldo, verificar_segundo_factor

    uno = Usuarios(
        nombre="Uno", correo="uno-mfa@example.com", mfa_secreto_cifrado="configurado"
    )
    otro = Usuarios(
        nombre="Otro", correo="otro-mfa@example.com", mfa_secreto_cifrado="configurado"
    )
    db.add_all([uno, otro])
    db.flush()
    codigo = generar_codigos_respaldo(db, uno)[0]
    db.commit()
    with pytest.raises(HTTPException):
        verificar_segundo_factor(otro, None, codigo, db)


def test_login_no_consume_respaldo_con_contrasena_incorrecta(db, monkeypatch):
    from backend.Sesiones.service import SesionService
    from backend.Sesiones.schema import Revisar_Json_Iniciar_Sesion
    from backend.Usuarios.codigos_mfa import CodigosRecuperacionMfa
    from utils.mfa import generar_codigos_respaldo
    from utils.hash import encriptar_contrasena

    usuario = Usuarios(
        nombre="Plataforma",
        correo="login-mfa@example.com",
        clave_protegida=encriptar_contrasena("Clave-prueba123"),
        mfa_secreto_cifrado="configurado",
    )
    db.add(usuario)
    db.flush()
    codigo = generar_codigos_respaldo(db, usuario)[0]
    db.commit()
    with pytest.raises(HTTPException):
        SesionService.iniciar_sesion_service(
            Revisar_Json_Iniciar_Sesion(
                correo=usuario.correo,
                clave="incorrecta",
                codigo_recuperacion_mfa=codigo,
            ),
            db,
        )
    assert (
        db.query(CodigosRecuperacionMfa)
        .filter(CodigosRecuperacionMfa.fecha_uso.is_not(None))
        .count()
        == 0
    )
