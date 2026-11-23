from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import SQLAlchemyError

from backend.Correos.service import encolar_correo, procesar_correo
from backend.RecuperacionesClave.repository import RecuperacionClaveRepository as repo
from backend.RecuperacionesClave.tabla import RecuperacionesClave
from backend.Sesiones.repository import SesionRepository as repo_sesion
from backend.Usuarios.repository import UsuarioRepository
from core.config import revision
from core.exceptions import SolicitudError
from utils.correo import enviar_recuperacion
from utils.hash import encriptar_contrasena
from utils.token import crear_token_sesion, proteger_token_sesion


class RecuperacionClaveService:
    @staticmethod
    def solicitar_recuperacion_service(json, tareas, db):
        try:
            if not all(
                (
                    revision.SMTP_SERVIDOR,
                    revision.SMTP_USUARIO,
                    revision.SMTP_CLAVE,
                    revision.SMTP_REMITENTE,
                )
            ):
                raise SolicitudError(503, "El envio de correo no esta configurado")

            look_up = repo.buscar_usuario_para_recuperacion(
                db, str(json.correo).lower()
            )

            if look_up and look_up.estado:
                ahora = datetime.now(timezone.utc).replace(tzinfo=None)
                repo.invalidar_codigos(db, look_up.id, ahora)
                codigo = crear_token_sesion()
                recuperacion = RecuperacionesClave(
                    id_usuario=look_up.id,
                    codigo_protegido=proteger_token_sesion(codigo),
                    fecha_inicio=ahora,
                    vencimiento=ahora + timedelta(minutes=15),
                )
                repo.agregar(db, recuperacion)
                id_correo = encolar_correo(
                    db, "recuperacion", look_up.correo, codigo, recuperacion.vencimiento
                )
                repo.guardar_cambios(db)
                db.commit()
                tareas.add_task(procesar_correo, db, id_correo, enviar_recuperacion)

            return {
                "detail": "Si el correo esta registrado y activo, recibiras instrucciones para recuperar tu clave"
            }
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def recuperar_clave_service(json, db):
        try:
            ahora = datetime.now(timezone.utc).replace(tzinfo=None)
            look_up = repo.buscar_recuperacion(
                db, proteger_token_sesion(json.codigo.get_secret_value()), ahora
            )

            if not look_up:
                raise SolicitudError(400, "El codigo no es valido o ya vencio")

            usuario = repo.buscar_usuario_por_id(db, look_up.id_usuario)
            # El bloqueo del usuario serializa solicitudes de la misma cuenta.
            repo.actualizar(db, look_up)
            ahora = datetime.now(timezone.utc).replace(tzinfo=None)

            if (
                not usuario
                or not usuario.estado
                or look_up.fecha_uso
                or look_up.vencimiento <= ahora
            ):
                raise SolicitudError(400, "El codigo no es valido o ya vencio")

            usuario.clave_protegida = encriptar_contrasena(
                json.nueva_clave.get_secret_value()
            )
            repo.invalidar_codigos(db, usuario.id, ahora)

            UsuarioRepository.invalidar_cambios_correo(db, usuario.id, ahora)
            repo_sesion.revocar_sesiones(db, usuario.id, ahora)
            repo.guardar_cambios(db)
            db.commit()

            return {"detail": "Clave restablecida. Ya puedes iniciar sesion"}
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise
