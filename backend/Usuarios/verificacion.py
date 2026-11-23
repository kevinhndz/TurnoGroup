from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError

from backend.Correos.service import encolar_correo, procesar_correo
from backend.Usuarios.repository import UsuarioRepository as repo
from backend.Usuarios.verificaciones_correo import VerificacionesCorreo
from core.config import revision
from core.exceptions import SolicitudError
from utils.token import crear_token_sesion, proteger_token_sesion


class VerificacionCorreoService:
    @staticmethod
    def solicitar(json, db, tareas):
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
            correo = str(json.correo).lower()

            if not repo.buscar_id_para_verificacion(db, correo):
                codigo = crear_token_sesion()
                vencimiento = datetime.utcnow() + timedelta(minutes=15)
                repo.agregar(
                    db,
                    VerificacionesCorreo(
                        correo=correo,
                        codigo_protegido=proteger_token_sesion(codigo),
                        vencimiento=vencimiento,
                    ),
                )
                envio = encolar_correo(db, "verificacion", correo, codigo, vencimiento)
                repo.guardar_cambios(db)
                db.commit()
                tareas.add_task(procesar_correo, db, envio)

            return {
                "detail": "Si puedes registrar ese correo, recibiras un codigo. Si ya tienes cuenta, inicia sesion."
            }
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def confirmar(json, db):
        try:
            registro = repo.buscar_verificacion_por_codigo(db, json)
            ahora = datetime.utcnow()

            if (
                not registro
                or registro.fecha_confirmacion
                or registro.fecha_uso
                or registro.vencimiento <= ahora
            ):
                raise SolicitudError(400, "El codigo no es valido o ya vencio")
            comprobante = crear_token_sesion()
            registro.comprobante_protegido = proteger_token_sesion(comprobante)
            registro.fecha_confirmacion = ahora
            # Hay tiempo para completar los pasos, sin crear todavia una cuenta.
            registro.vencimiento = ahora + timedelta(hours=2)
            repo.guardar_cambios(db)
            db.commit()

            return {"comprobante_correo": comprobante}
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def consumir(correo, comprobante, db):
        registro = repo.buscar_verificacion_por_comprobante(db, comprobante, correo)

        if (
            not registro
            or not registro.fecha_confirmacion
            or registro.fecha_uso
            or registro.vencimiento <= datetime.utcnow()
        ):
            raise SolicitudError(
                400, "Verifica tu correo de nuevo antes de registrar el negocio"
            )
        # Se confirma junto con el negocio. Si falla el registro, se revierte.
        registro.fecha_uso = datetime.utcnow()
