from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.Correos.service import encolar_correo, procesar_correo
from backend.RecuperacionesClave.repository import RecuperacionClaveRepository
from backend.Sesiones.repository import SesionRepository
from backend.Usuarios.cambios_correo import CambiosCorreo
from backend.Usuarios.repository import UsuarioRepository as repo
from core.config import revision
from core.exceptions import (
    CredencialesInvalidasError,
    RecursoDuplicadoError,
    SolicitudError,
)
from utils.hash import verificar_contrasena
from utils.token import crear_token_sesion, proteger_token_sesion


class SeguridadUsuarioService:
    @staticmethod
    def autenticar(db, id_usuario, clave):
        usuario = repo.buscar_usuario_para_cambio_correo(db, id_usuario)

        if (
            not usuario
            or not usuario.estado
            or not usuario.clave_protegida
            or not verificar_contrasena(clave, usuario.clave_protegida or "")
        ):
            raise CredencialesInvalidasError("Verifica tu contrasena actual")

        return usuario

    @staticmethod
    def solicitar(json, id_usuario, db, tareas):
        try:
            usuario = SeguridadUsuarioService.autenticar(
                db, id_usuario, json.clave_actual.get_secret_value()
            )
            nuevo = str(json.correo_nuevo).lower()

            if nuevo == usuario.correo:
                raise SolicitudError(422, "Indica un correo diferente")

            if repo.buscar_correo_nuevo(db, nuevo):
                raise RecursoDuplicadoError("No se puede utilizar ese correo")

            if not all(
                (
                    revision.SMTP_SERVIDOR,
                    revision.SMTP_USUARIO,
                    revision.SMTP_CLAVE,
                    revision.SMTP_REMITENTE,
                )
            ):
                raise SolicitudError(503, "El envio de correo no esta configurado")
            ahora = datetime.utcnow()
            repo.invalidar_cambios_pendientes(db, ahora, usuario)
            codigo = crear_token_sesion()
            vencimiento = ahora + timedelta(minutes=15)
            repo.agregar(
                db,
                CambiosCorreo(
                    id_usuario=usuario.id,
                    correo_anterior=usuario.correo,
                    correo_nuevo=nuevo,
                    codigo_protegido=proteger_token_sesion(codigo),
                    vencimiento=vencimiento,
                ),
            )
            envio = encolar_correo(db, "cambio_correo", nuevo, codigo, vencimiento)
            repo.guardar_cambios(db)
            db.commit()
            tareas.add_task(procesar_correo, db, envio)

            return {
                "detail": "Confirma el codigo enviado al correo nuevo. Tu correo actual no ha cambiado."
            }
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def confirmar(json, id_usuario, db, tareas):
        try:
            usuario = SeguridadUsuarioService.autenticar(
                db, id_usuario, json.clave_actual.get_secret_value()
            )
            ahora = datetime.utcnow()
            cambio = repo.buscar_cambio_correo_vigente(db, ahora, usuario, json)

            if not cambio or cambio.correo_anterior != usuario.correo:
                raise SolicitudError(400, "El codigo no es valido o ya vencio")
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
                repo.guardar_cambios(db)
                db.commit()
            except IntegrityError:
                db.rollback()
                raise RecursoDuplicadoError("No se puede utilizar ese correo") from None
            tareas.add_task(procesar_correo, db, aviso)

            return {"detail": "Correo confirmado. Inicia sesion con tu nuevo correo."}
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise
