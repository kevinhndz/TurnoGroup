from datetime import datetime, timedelta
from fastapi import HTTPException
from backend.Usuarios.tabla import Usuarios
from backend.Usuarios.verificaciones_correo import VerificacionesCorreo
from backend.Correos.service import encolar_correo, procesar_correo
from core.config import revision
from utils.token import crear_token_sesion, proteger_token_sesion


class VerificacionCorreoService:
    @staticmethod
    def solicitar(json, db, tareas):
        if not all(
            (
                revision.SMTP_SERVIDOR,
                revision.SMTP_USUARIO,
                revision.SMTP_CLAVE,
                revision.SMTP_REMITENTE,
            )
        ):
            raise HTTPException(503, "El envio de correo no esta configurado")
        correo = str(json.correo).lower()
        if not db.query(Usuarios.id).filter_by(correo=correo).first():
            codigo = crear_token_sesion()
            vencimiento = datetime.utcnow() + timedelta(minutes=15)
            db.add(
                VerificacionesCorreo(
                    correo=correo,
                    codigo_protegido=proteger_token_sesion(codigo),
                    vencimiento=vencimiento,
                )
            )
            envio = encolar_correo(db, "verificacion", correo, codigo, vencimiento)
            db.commit()
            tareas.add_task(procesar_correo, db, envio)
        return {
            "detail": "Si puedes registrar ese correo, recibiras un codigo. Si ya tienes cuenta, inicia sesion."
        }

    @staticmethod
    def confirmar(json, db):
        registro = (
            db.query(VerificacionesCorreo)
            .filter_by(
                correo=str(json.correo).lower(),
                codigo_protegido=proteger_token_sesion(json.codigo.get_secret_value()),
            )
            .with_for_update()
            .first()
        )
        ahora = datetime.utcnow()
        if (
            not registro
            or registro.fecha_confirmacion
            or registro.fecha_uso
            or registro.vencimiento <= ahora
        ):
            raise HTTPException(400, "El codigo no es valido o ya vencio")
        comprobante = crear_token_sesion()
        registro.comprobante_protegido = proteger_token_sesion(comprobante)
        registro.fecha_confirmacion = ahora
        # Hay tiempo para completar los pasos, sin crear todavia una cuenta.
        registro.vencimiento = ahora + timedelta(hours=2)
        db.commit()
        return {"comprobante_correo": comprobante}

    @staticmethod
    def consumir(correo, comprobante, db):
        registro = (
            db.query(VerificacionesCorreo)
            .filter_by(
                correo=str(correo).lower(),
                comprobante_protegido=proteger_token_sesion(comprobante),
            )
            .with_for_update()
            .first()
        )
        if (
            not registro
            or not registro.fecha_confirmacion
            or registro.fecha_uso
            or registro.vencimiento <= datetime.utcnow()
        ):
            raise HTTPException(
                400, "Verifica tu correo de nuevo antes de registrar el negocio"
            )
        # Se confirma junto con el negocio. Si falla el registro, se revierte.
        registro.fecha_uso = datetime.utcnow()
