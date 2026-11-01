from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from backend.InvitacionesLaborales.repository import InvitacionLaboralRepository as repo
from backend.InvitacionesLaborales.tabla import (
    InvitacionesLaborales,
    SucursalesInvitacion,
)
from backend.VinculosLaborales.tabla import VinculosLaborales
from core.config import revision
from utils.token import crear_token_sesion, proteger_token_sesion
from utils.correo import enviar_invitacion


class InvitacionLaboralService:

    @staticmethod
    def respuesta_invitacion(invitacion, db):
        return {
            "id": invitacion.id,
            "correo": invitacion.correo,
            "id_empresa": invitacion.id_empresa,
            "rol": invitacion.rol,
            "vencimiento": invitacion.vencimiento,
            "fecha_aceptacion": invitacion.fecha_aceptacion,
            "fecha_revocacion": invitacion.fecha_revocacion,
            "sucursales": repo.sucursales_invitacion(db, invitacion.id),
        }

    @staticmethod
    def crear_invitacion_service(json, contexto, tareas, db):
        empresa = repo.bloquear_empresa(db, contexto["id_empresa"])
        ids = json.sucursales
        if (
            len(ids) != len(set(ids))
            or any(id <= 0 for id in ids)
            or (json.rol != "Gerente" and len(ids) != 1)
        ):
            raise HTTPException(422, "Indica una sola sucursal para administrador o mesero, sin repetir")
        for id_sucursal in ids:
            if not repo.buscar_sucursal(db, id_sucursal, empresa.id):
                raise HTTPException(404, "No se encontro la sucursal")
        correo = str(json.correo).lower()
        usuario = repo.buscar_usuario(db, correo)
        if usuario and repo.buscar_otra_empresa(db, usuario.id, empresa.id):
            raise HTTPException(409, "El usuario ya pertenece a otra empresa")
        existente = repo.buscar_vinculo(db, usuario.id, empresa.id) if usuario else None
        if existente and existente.activo:
            raise HTTPException(409, "El usuario ya tiene un vinculo activo")
        if not all(
            (
                revision.SMTP_SERVIDOR,
                revision.SMTP_USUARIO,
                revision.SMTP_CLAVE,
                revision.SMTP_REMITENTE,
            )
        ):
            raise HTTPException(503, "El envio de correo no esta configurado")
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)
        repo.revocar_anteriores(db, correo, empresa.id, ahora)
        codigo = crear_token_sesion()
        invitacion = InvitacionesLaborales(
            correo=correo,
            id_empresa=empresa.id,
            id_usuario_invitante=contexto["usuario"].id,
            rol=json.rol,
            codigo_protegido=proteger_token_sesion(codigo),
            fecha_creacion=ahora,
            vencimiento=ahora + timedelta(hours=48),
        )
        db.add(invitacion)
        db.flush()
        for id_sucursal in ids:
            db.add(
                SucursalesInvitacion(
                    id_invitacion=invitacion.id, id_sucursal=id_sucursal
                )
            )
        db.commit()
        tareas.add_task(enviar_invitacion, correo, codigo)
        return InvitacionLaboralService.respuesta_invitacion(invitacion, db)

    @staticmethod
    def listar_invitaciones_service(id_empresa, pagina_actual, limite, db):
        total, lista = repo.listar_invitaciones(db, id_empresa, pagina_actual, limite)
        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": (total + limite - 1) // limite,
            "data": [
                InvitacionLaboralService.respuesta_invitacion(fila, db)
                for fila in lista
            ],
        }

    @staticmethod
    def ver_invitacion_service(id, id_empresa, db):
        look_up = repo.buscar_invitacion(db, id, id_empresa)
        if not look_up:
            raise HTTPException(404, "No se encontro la invitacion")
        return InvitacionLaboralService.respuesta_invitacion(look_up, db)

    @staticmethod
    def revocar_invitacion_service(id, id_empresa, db):
        repo.bloquear_empresa(db, id_empresa)
        look_up = repo.buscar_invitacion(db, id, id_empresa)
        if not look_up:
            raise HTTPException(404, "No se encontro la invitacion")
        if look_up.fecha_aceptacion:
            raise HTTPException(409, "La invitacion ya fue aceptada")
        look_up.fecha_revocacion = datetime.now(timezone.utc).replace(tzinfo=None)
        db.commit()
        return InvitacionLaboralService.respuesta_invitacion(look_up, db)

    @staticmethod
    def aceptar_invitacion_service(json, usuario, db, confirmar=True):
        look_up = repo.buscar_por_codigo(
            db, proteger_token_sesion(json.codigo.get_secret_value())
        )
        if not look_up:
            raise HTTPException(400, "La invitacion no es valida")
        empresa = repo.bloquear_empresa(db, look_up.id_empresa)
        db.refresh(look_up)
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)
        if (
            look_up.correo != usuario.correo
            or look_up.fecha_aceptacion
            or look_up.fecha_revocacion
            or look_up.vencimiento <= ahora
            or empresa.estado not in ("En Prueba", "Activa")
        ):
            raise HTTPException(400, "La invitacion no es valida")
        invitante = repo.buscar_invitante_activo(
            db, look_up.id_usuario_invitante, empresa.id
        )
        if not invitante or not invitante.activo or invitante.rol != "Gerente":
            raise HTTPException(400, "La invitacion no es valida")
        sucursales = repo.sucursales_invitacion(db, look_up.id)
        if look_up.rol != "Gerente" and len(sucursales) != 1:
            raise HTTPException(400, "Solicita una invitacion con una sola sucursal")
        if repo.buscar_otra_empresa(db, usuario.id, empresa.id):
            raise HTTPException(409, "El usuario ya pertenece a otra empresa")
        for id_sucursal in sucursales:
            if not repo.buscar_sucursal(db, id_sucursal, empresa.id):
                raise HTTPException(400, "La invitacion no es valida")
        vinculo = repo.buscar_vinculo(db, usuario.id, empresa.id)
        if vinculo and vinculo.activo:
            raise HTTPException(409, "Ya tienes un vinculo activo con esta empresa")
        if not vinculo:
            vinculo = VinculosLaborales(
                id_usuario=usuario.id, id_empresa=empresa.id, rol=look_up.rol
            )
            db.add(vinculo)
            db.flush()
        vinculo.rol = look_up.rol
        vinculo.activo = True
        repo.reemplazar_asignaciones(db, vinculo.id, sucursales)
        look_up.fecha_aceptacion = ahora
        if confirmar:
            db.commit()
            db.refresh(vinculo)
        else:
            db.flush()
        return vinculo

    @staticmethod
    def registrar_invitado_service(json, db):
        from backend.Usuarios.tabla import Usuarios
        from backend.Sesiones.tabla import Sesiones
        from backend.Sesiones.service import SesionService
        from utils.hash import encriptar_contrasena

        invitacion = repo.buscar_por_codigo(
            db, proteger_token_sesion(json.codigo.get_secret_value())
        )
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)
        if (
            not invitacion
            or invitacion.fecha_aceptacion
            or invitacion.fecha_revocacion
            or invitacion.vencimiento <= ahora
        ):
            raise HTTPException(400, "La invitacion no es valida")
        if repo.buscar_usuario(db, invitacion.correo):
            raise HTTPException(
                409, "Ya tienes una cuenta. Inicia sesion para aceptar la invitacion"
            )
        try:
            usuario = Usuarios(
                nombre=json.nombre,
                correo=invitacion.correo,
                clave_protegida=encriptar_contrasena(json.clave.get_secret_value()),
            )
            db.add(usuario)
            db.flush()
            vinculo = InvitacionLaboralService.aceptar_invitacion_service(
                json, usuario, db, confirmar=False
            )
            sucursales = repo.sucursales_invitacion(db, invitacion.id)
            token = crear_token_sesion()
            sesion = Sesiones(
                id_usuario=usuario.id,
                id_vinculo_laboral=vinculo.id,
                id_sucursal=sucursales[0] if sucursales else None,
                token_protegido=proteger_token_sesion(token),
                fecha_inicio=ahora,
                vencimiento=ahora + timedelta(hours=revision.SESION_HORAS),
            )
            db.add(sesion)
            db.flush()
            respuesta = SesionService.respuesta_sesion_service(sesion, usuario, db)
            from backend.Sesiones.schema import RespuestaSesion

            respuesta = RespuestaSesion.model_validate(respuesta)
            db.commit()
            return respuesta, token, sesion.vencimiento
        except Exception:
            db.rollback()
            raise
