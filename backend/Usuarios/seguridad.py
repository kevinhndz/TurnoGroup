from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from backend.Usuarios.tabla import Usuarios
from backend.Usuarios.cambios_correo import CambiosCorreo
from backend.Correos.service import encolar_correo, procesar_correo
from backend.Sesiones.repository import SesionRepository
from backend.RecuperacionesClave.repository import RecuperacionClaveRepository
from utils.hash import verificar_contrasena
from utils.token import crear_token_sesion, proteger_token_sesion
from core.config import revision


class SeguridadUsuarioService:
    @staticmethod
    def autenticar(db, id_usuario, clave):
        usuario = (
            db.query(Usuarios)
            .filter(Usuarios.id == id_usuario)
            .with_for_update()
            .first()
        )
        if (
            not usuario
            or not usuario.estado
            or not usuario.clave_protegida
            or not verificar_contrasena(clave, usuario.clave_protegida or "")
        ):
            raise HTTPException(401, "Verifica tu contrasena actual")
        return usuario

    @staticmethod
    def solicitar(json, id_usuario, db, tareas):
        usuario = SeguridadUsuarioService.autenticar(
            db, id_usuario, json.clave_actual.get_secret_value()
        )
        nuevo = str(json.correo_nuevo).lower()
        if nuevo == usuario.correo:
            raise HTTPException(422, "Indica un correo diferente")
        if db.query(Usuarios.id).filter(Usuarios.correo == nuevo).first():
            raise HTTPException(409, "No se puede utilizar ese correo")
        if not all(
            (
                revision.SMTP_SERVIDOR,
                revision.SMTP_USUARIO,
                revision.SMTP_CLAVE,
                revision.SMTP_REMITENTE,
            )
        ):
            raise HTTPException(503, "El envio de correo no esta configurado")
        ahora = datetime.utcnow()
        db.query(CambiosCorreo).filter(
            CambiosCorreo.id_usuario == usuario.id, CambiosCorreo.fecha_uso.is_(None)
        ).update({"fecha_uso": ahora})
        codigo = crear_token_sesion()
        vencimiento = ahora + timedelta(minutes=15)
        db.add(
            CambiosCorreo(
                id_usuario=usuario.id,
                correo_anterior=usuario.correo,
                correo_nuevo=nuevo,
                codigo_protegido=proteger_token_sesion(codigo),
                vencimiento=vencimiento,
            )
        )
        envio = encolar_correo(db, "cambio_correo", nuevo, codigo, vencimiento)
        db.commit()
        tareas.add_task(procesar_correo, db, envio)
        return {
            "detail": "Confirma el codigo enviado al correo nuevo. Tu correo actual no ha cambiado."
        }

    @staticmethod
    def confirmar(json, id_usuario, db, tareas):
        usuario = SeguridadUsuarioService.autenticar(
            db, id_usuario, json.clave_actual.get_secret_value()
        )
        ahora = datetime.utcnow()
        cambio = (
            db.query(CambiosCorreo)
            .filter(
                CambiosCorreo.id_usuario == usuario.id,
                CambiosCorreo.codigo_protegido
                == proteger_token_sesion(json.codigo.get_secret_value()),
                CambiosCorreo.fecha_uso.is_(None),
                CambiosCorreo.vencimiento > ahora,
            )
            .first()
        )
        if not cambio or cambio.correo_anterior != usuario.correo:
            raise HTTPException(400, "El codigo no es valido o ya vencio")
        anterior = usuario.correo
        usuario.correo = cambio.correo_nuevo
        cambio.fecha_uso = ahora
        SesionRepository.revocar_sesiones(db, usuario.id, ahora)
        RecuperacionClaveRepository.invalidar_codigos(db, usuario.id, ahora)
        aviso = encolar_correo(
            db,
            "aviso_correo",
            anterior,
            "Tu correo de acceso fue cambiado. Si no fuiste tu, contacta al administrador.",
            ahora + timedelta(days=1),
        )
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(409, "No se puede utilizar ese correo") from None
        tareas.add_task(procesar_correo, db, aviso)
        return {"detail": "Correo confirmado. Inicia sesion con tu nuevo correo."}
