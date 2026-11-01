from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from backend.Sesiones.repository import SesionRepository as repo
from backend.Sesiones.tabla import Sesiones
from backend.Usuarios.repository import UsuarioRepository as repo_usuario
from core.config import revision
from utils.hash import verificar_contrasena, encriptar_contrasena
from utils.token import crear_token_sesion, proteger_token_sesion

_hash_sin_usuario = encriptar_contrasena(crear_token_sesion())


class SesionService():

    @staticmethod
    def iniciar_sesion_service(json, db):
        look_up = repo.buscar_usuario_para_sesion(db, str(json.correo).lower())
        hash_guardado = look_up.clave_protegida if look_up and look_up.clave_protegida else _hash_sin_usuario
        correcta = verificar_contrasena(json.clave.get_secret_value(), hash_guardado)

        if not look_up or not look_up.estado or not look_up.clave_protegida or not correcta:
            raise HTTPException(401, "Correo o clave incorrectos")

        token = crear_token_sesion()
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)
        nueva_sesion = Sesiones(
            id_usuario=look_up.id,
            token_protegido=proteger_token_sesion(token),
            fecha_inicio=ahora,
            vencimiento=ahora + timedelta(hours=revision.SESION_HORAS)
        )
        if look_up.rol_plataforma != "Superadministrador":
            vinculo = repo.buscar_vinculo_autorizado(db, look_up.id)
            if vinculo:
                nueva_sesion.id_vinculo_laboral = vinculo.id
                sucursal = repo.buscar_sucursal_autorizada(db, vinculo)
                nueva_sesion.id_sucursal = sucursal.id if sucursal else None
        sesion = repo.guardar_nueva_sesion(db, nueva_sesion)
        return sesion, look_up, token

    @staticmethod
    def consultar_sesion_service(token, db):
        if not token or len(token) > 128:
            raise HTTPException(401, "Debes iniciar sesion")

        look_up = repo.buscar_sesion_con_usuario(db, proteger_token_sesion(token))
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)
        if not look_up:
            raise HTTPException(401, "La sesion no esta vigente")
        sesion, usuario = look_up
        if sesion.fecha_revocacion or sesion.vencimiento <= ahora or not usuario.estado:
            raise HTTPException(401, "La sesion no esta vigente")
        return sesion, usuario

    @staticmethod
    def renovar_sesion_service(sesion, db):
        token = crear_token_sesion()
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)
        editados = repo.renovar_sesion(
            db, sesion.id, sesion.token_protegido, proteger_token_sesion(token), ahora
        )
        if editados != 1:
            raise HTTPException(401, "La sesion no esta vigente")
        db.commit()
        db.refresh(sesion)
        return token

    @staticmethod
    def cerrar_sesion_service(token, db):
        if token and len(token) <= 128:
            look_up = repo.buscar_sesion(db, proteger_token_sesion(token))
            if look_up and not look_up.fecha_revocacion:
                look_up.fecha_revocacion = datetime.now(timezone.utc).replace(tzinfo=None)
                db.commit()

    @staticmethod
    def revocar_sesiones_service(id_usuario, db):
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)
        repo.revocar_sesiones(db, id_usuario, ahora)
        db.commit()


    @staticmethod
    def obtener_contexto_service(sesion, usuario, db):
        contexto = {"sesion": sesion, "usuario": usuario, "vinculo": None,
                    "id_empresa": None, "id_sucursal": None, "rol": None,
                    "rol_plataforma": usuario.rol_plataforma}
        if usuario.rol_plataforma == "Superadministrador":
            return contexto
        if sesion.id_vinculo_laboral is None:
            return contexto
        vinculo = repo.buscar_vinculo_autorizado(db, usuario.id, sesion.id_vinculo_laboral)
        if not vinculo or vinculo.rol not in ("Gerente", "Administrador", "Mesero"):
            raise HTTPException(403, "El vinculo no esta autorizado")
        contexto.update(vinculo=vinculo, id_empresa=vinculo.id_empresa, rol=vinculo.rol)
        if sesion.id_sucursal is not None:
            sucursal = repo.buscar_sucursal_autorizada(db, vinculo, sesion.id_sucursal)
            if not sucursal:
                raise HTTPException(403, "La sucursal no esta autorizada")
            contexto["id_sucursal"] = sucursal.id
        return contexto

    @staticmethod
    def seleccionar_contexto_service(json, sesion, usuario, db):
        if usuario.rol_plataforma == "Superadministrador":
            raise HTTPException(403, "La plataforma no opera empresas de clientes")
        vinculo = repo.buscar_vinculo_autorizado(db, usuario.id, json.id_vinculo_laboral)
        if not vinculo:
            raise HTTPException(403, "El vinculo no esta autorizado")
        sucursal = repo.buscar_sucursal_autorizada(db, vinculo, json.id_sucursal)
        if json.id_sucursal is not None and not sucursal:
            raise HTTPException(403, "La sucursal no esta autorizada")
        if vinculo.rol != "Gerente" and not sucursal:
            raise HTTPException(403, "Debes tener una sucursal asignada")
        sesion.id_vinculo_laboral = vinculo.id
        sesion.id_sucursal = sucursal.id if sucursal else None
        token = SesionService.renovar_sesion_service(sesion, db)
        return token

    @staticmethod
    def respuesta_sesion_service(sesion, usuario, db):
        contexto = SesionService.obtener_contexto_service(sesion, usuario, db)
        from backend.ServiciosSucursales.tabla import ServiciosSucursales
        from backend.Suscripciones.repository import SuscripcionRepository
        from backend.Suscripciones.service import SuscripcionService
        servicio = db.query(ServiciosSucursales).filter(ServiciosSucursales.id_sucursal == contexto['id_sucursal'], ServiciosSucursales.habilitado.is_(True), ServiciosSucursales.mesas_habilitadas.is_(True)).first() if contexto['id_sucursal'] else None
        suscripcion = SuscripcionRepository.buscar_suscripcion(db, contexto['id_empresa']) if contexto['id_empresa'] else None
        return {"usuario": usuario, "vencimiento": sesion.vencimiento,
                "id_empresa": contexto["id_empresa"], "id_sucursal": contexto["id_sucursal"],
                "rol_empresa": contexto["rol"], "mesas_habilitadas": bool(servicio),
                "reservas_habilitadas": bool(servicio and servicio.reservas_habilitadas),
                "finanzas_habilitadas": bool(suscripcion and suscripcion.finanzas_habilitadas and SuscripcionService.vigente(suscripcion))}
