from utils.hash import encriptar_contrasena
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.Usuarios.tabla import Usuarios
from backend.Usuarios.repository import UsuarioRepository as repo
from backend.Usuarios.schema import Revisar_Json_Nuevo_Usuario, Revisar_Json_Editar_Usuario
from core.exceptions import RecursoDuplicadoError, RecursoNoEncontradoError


class UsuarioService():

    @staticmethod
    def crear_usuario_service(json: Revisar_Json_Nuevo_Usuario, db: Session):
        correo = str(json.correo).lower()
        look_up = repo.buscar_usuario_por_correo(db, correo)

        if look_up is not None:
            raise RecursoDuplicadoError("Ya existe un usuario con ese correo")

        nuevo_usuario = Usuarios(
            correo=correo,
            clave_protegida=encriptar_contrasena(json.clave.get_secret_value()),
            nombre=json.nombre
        )
        return repo.guardar_nuevo_usuario(db, nuevo_usuario)

    @staticmethod
    def listar_usuarios_service(pagina_actual: int, limite: int, db: Session):
        total, lista_usuarios = repo.listar_usuarios(db, pagina_actual, limite)
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_usuarios
        }

    @staticmethod
    def ver_usuario_service(id: int, db: Session):
        look_up = repo.buscar_usuario_por_id(db, id)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el usuario")

        return look_up

    @staticmethod
    def editar_usuario_service(json: Revisar_Json_Editar_Usuario, id: int, db: Session):
        look_up = repo.buscar_usuario_por_id(db, id)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el usuario")

        cambios = json.model_dump(exclude_unset=True)
        if not cambios:
            raise HTTPException(status_code=422, detail="Debes enviar al menos un campo para editar")
        for campo, valor in cambios.items():
            if valor is None:
                raise HTTPException(status_code=422, detail="El campo " + campo + " no acepta null")

        if "correo" in cambios:
            cambios["correo"] = str(cambios["correo"]).lower()
            if cambios["correo"] != look_up.correo:
                usuario_existente = repo.buscar_usuario_por_correo(db, cambios["correo"])
                if usuario_existente is not None:
                    raise RecursoDuplicadoError("Ya existe un usuario con ese correo")

        if cambios.get("estado") is False:
            UsuarioService.revisar_ultimo_superadministrador(look_up, db)
            UsuarioService.revocar_accesos_service(id, db)
        for campo, valor in cambios.items():
            setattr(look_up, campo, valor)

        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def desactivar_usuario_service(id: int, db: Session):
        look_up = repo.buscar_usuario_por_id(db, id)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el usuario")

        UsuarioService.revisar_ultimo_superadministrador(look_up, db)
        UsuarioService.revocar_accesos_service(id, db)
        look_up.estado = False
        db.commit()
        db.refresh(look_up)
        return look_up


    @staticmethod
    def cambiar_rol_plataforma_service(json, id, db):
        look_up = repo.buscar_usuario_por_id(db, id)
        if not look_up:
            raise RecursoNoEncontradoError("No se encontro el usuario")
        if look_up.rol_plataforma == "Superadministrador" and json.rol_plataforma != "Superadministrador":
            UsuarioService.revisar_ultimo_superadministrador(look_up, db)
        look_up.rol_plataforma = json.rol_plataforma
        from backend.Sesiones.repository import SesionRepository
        from datetime import datetime, timezone
        SesionRepository.revocar_sesiones(db, id, datetime.now(timezone.utc).replace(tzinfo=None))
        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def revisar_ultimo_superadministrador(usuario, db):
        administradores = db.query(Usuarios).filter(
            Usuarios.rol_plataforma == "Superadministrador", Usuarios.estado.is_(True)
        ).order_by(Usuarios.id).with_for_update().all()
        if usuario.estado and usuario.rol_plataforma == "Superadministrador" and len(administradores) <= 1:
            raise HTTPException(409, "La plataforma debe conservar un superadministrador activo")


    @staticmethod
    def revocar_accesos_service(id, db):
        from datetime import datetime, timezone
        from backend.Sesiones.repository import SesionRepository
        from backend.RecuperacionesClave.repository import RecuperacionClaveRepository
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)
        SesionRepository.revocar_sesiones(db, id, ahora)
        RecuperacionClaveRepository.invalidar_codigos(db, id, ahora)
