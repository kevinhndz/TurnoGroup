from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import SQLAlchemyError

from backend.Sesiones.repository import SesionRepository as repo
from backend.Sesiones.tabla import Sesiones
from backend.Suscripciones.repository import SuscripcionRepository
from backend.Suscripciones.service import SuscripcionService
from core.config import revision
from core.exceptions import SolicitudError
from utils.hash import encriptar_contrasena, verificar_contrasena
from utils.mfa import verificar_segundo_factor
from utils.rate_limiting import limitar_por_cuenta
from utils.token import crear_token_sesion, proteger_token_sesion

_hash_sin_usuario = encriptar_contrasena(crear_token_sesion())


class SesionService:
    @staticmethod
    def iniciar_sesion_service(json, db):
        try:
            limitar_por_cuenta(str(json.correo))
            look_up = repo.buscar_usuario_para_sesion(db, str(json.correo).lower())
            hash_guardado = (
                look_up.clave_protegida
                if look_up and look_up.clave_protegida
                else _hash_sin_usuario
            )
            correcta = verificar_contrasena(
                json.clave.get_secret_value(), hash_guardado
            )

            if not look_up or not look_up.clave_protegida or not correcta:
                raise SolicitudError(401, "Correo o clave incorrectos")

            codigo = json.codigo_mfa.get_secret_value() if json.codigo_mfa else None
            respaldo = (
                json.codigo_recuperacion_mfa.get_secret_value()
                if json.codigo_recuperacion_mfa
                else None
            )
            verificar_segundo_factor(look_up, codigo, respaldo, db)

            if not look_up.estado:
                if not look_up.fecha_desactivacion_voluntaria:
                    raise SolicitudError(401, "Correo o clave incorrectos")

                if not json.reactivar:
                    raise SolicitudError(
                        409,
                        {
                            "codigo": "CUENTA_DESACTIVADA",
                            "mensaje": "Tu cuenta esta desactivada. Puedes reactivarla para recuperar el acceso.",
                        },
                    )
                look_up.estado = True
                look_up.fecha_desactivacion_voluntaria = None

            token = crear_token_sesion()
            ahora = datetime.now(timezone.utc).replace(tzinfo=None)
            nueva_sesion = Sesiones(
                id_usuario=look_up.id,
                token_protegido=proteger_token_sesion(token),
                fecha_inicio=ahora,
                vencimiento=ahora + timedelta(hours=revision.SESION_HORAS),
            )

            if look_up.rol_plataforma != "Superadministrador":
                vinculo = repo.buscar_vinculo_autorizado(db, look_up.id)

                if vinculo:
                    nueva_sesion.id_vinculo_laboral = vinculo.id
                    sucursal = repo.buscar_sucursal_autorizada(db, vinculo)
                    nueva_sesion.id_sucursal = sucursal.id if sucursal else None
            sesion = repo.guardar_nueva_sesion(db, nueva_sesion)
            repo.guardar_cambios(db)
            db.commit()
            repo.actualizar(db, sesion)

            return sesion, look_up, token
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def consultar_sesion_service(token, db):
        if not token or len(token) > 128:
            raise SolicitudError(401, "Debes iniciar sesion")

        look_up = repo.buscar_sesion_con_usuario(db, proteger_token_sesion(token))
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)

        if not look_up:
            raise SolicitudError(401, "La sesion no esta vigente")
        sesion, usuario = look_up

        if sesion.fecha_revocacion or sesion.vencimiento <= ahora or not usuario.estado:
            raise SolicitudError(401, "La sesion no esta vigente")

        return sesion, usuario

    @staticmethod
    def renovar_sesion_service(sesion, db):
        try:
            token = crear_token_sesion()
            ahora = datetime.now(timezone.utc).replace(tzinfo=None)
            editados = repo.renovar_sesion(
                db,
                sesion.id,
                sesion.token_protegido,
                proteger_token_sesion(token),
                ahora,
            )

            if editados != 1:
                raise SolicitudError(401, "La sesion no esta vigente")
            repo.guardar_cambios(db)
            db.commit()
            repo.actualizar(db, sesion)

            return token
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def cerrar_sesion_service(token, db):
        try:
            if token and len(token) <= 128:
                look_up = repo.buscar_sesion(db, proteger_token_sesion(token))

                if look_up and not look_up.fecha_revocacion:
                    look_up.fecha_revocacion = datetime.now(timezone.utc).replace(
                        tzinfo=None
                    )
                    repo.guardar_cambios(db)
                    db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def revocar_sesiones_service(id_usuario, db):
        try:
            ahora = datetime.now(timezone.utc).replace(tzinfo=None)
            repo.revocar_sesiones(db, id_usuario, ahora)
            repo.guardar_cambios(db)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def obtener_contexto_service(sesion, usuario, db):
        contexto = {
            "sesion": sesion,
            "usuario": usuario,
            "vinculo": None,
            "id_empresa": None,
            "id_sucursal": None,
            "rol": None,
            "rol_plataforma": usuario.rol_plataforma,
        }

        if usuario.rol_plataforma == "Superadministrador":
            return contexto

        if sesion.id_vinculo_laboral is None:
            return contexto
        vinculo = repo.buscar_vinculo_autorizado(
            db, usuario.id, sesion.id_vinculo_laboral
        )

        if not vinculo or vinculo.rol not in ("Gerente", "Administrador", "Mesero"):
            raise SolicitudError(403, "El vinculo no esta autorizado")
        contexto.update(vinculo=vinculo, id_empresa=vinculo.id_empresa, rol=vinculo.rol)

        if sesion.id_sucursal is not None:
            sucursal = repo.buscar_sucursal_autorizada(db, vinculo, sesion.id_sucursal)

            if not sucursal:
                raise SolicitudError(403, "La sucursal no esta autorizada")
            contexto["id_sucursal"] = sucursal.id

        return contexto

    @staticmethod
    def seleccionar_contexto_service(json, sesion, usuario, db):
        if usuario.rol_plataforma == "Superadministrador":
            raise SolicitudError(403, "La plataforma no opera empresas de clientes")
        vinculo = repo.buscar_vinculo_autorizado(
            db, usuario.id, json.id_vinculo_laboral
        )

        if not vinculo:
            raise SolicitudError(403, "El vinculo no esta autorizado")

        if sesion.id_vinculo_laboral and sesion.id_vinculo_laboral != vinculo.id:
            raise SolicitudError(403, "La sesion pertenece a una sola empresa")

        if vinculo.rol != "Gerente":
            asignada = repo.buscar_sucursal_autorizada(db, vinculo)
            id_asignada = sesion.id_sucursal or (asignada.id if asignada else None)

            if json.id_sucursal != id_asignada:
                raise SolicitudError(403, "Solo el gerente puede cambiar de sucursal")
        sucursal = repo.buscar_sucursal_autorizada(db, vinculo, json.id_sucursal)

        if json.id_sucursal is not None and not sucursal:
            raise SolicitudError(403, "La sucursal no esta autorizada")

        if vinculo.rol != "Gerente" and not sucursal:
            raise SolicitudError(403, "Debes tener una sucursal asignada")
        sesion.id_vinculo_laboral = vinculo.id
        sesion.id_sucursal = sucursal.id if sucursal else None
        token = SesionService.renovar_sesion_service(sesion, db)

        return token

    @staticmethod
    def respuesta_sesion_service(sesion, usuario, db):
        contexto = SesionService.obtener_contexto_service(sesion, usuario, db)

        servicio = (
            repo.buscar_servicio_con_mesas(db, contexto)
            if contexto["id_sucursal"]
            else None
        )
        suscripcion = (
            SuscripcionRepository.buscar_suscripcion(db, contexto["id_empresa"])
            if contexto["id_empresa"]
            else None
        )

        return {
            "usuario": usuario,
            "vencimiento": sesion.vencimiento,
            "id_empresa": contexto["id_empresa"],
            "id_sucursal": contexto["id_sucursal"],
            "rol_empresa": contexto["rol"],
            "mesas_habilitadas": bool(servicio),
            "reservas_habilitadas": bool(servicio and servicio.reservas_habilitadas),
            "finanzas_habilitadas": bool(
                suscripcion
                and suscripcion.finanzas_habilitadas
                and SuscripcionService.vigente(suscripcion)
            ),
        }
