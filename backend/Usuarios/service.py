from sqlalchemy.orm import Session
from backend.Usuarios.repository import UsuarioRepository as repo
from backend.Usuarios.schema import Revisar_Json_Nuevo_Usuario, Revisar_Json_Editar_Usuario
from backend.Usuarios.tabla import Usuarios
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

        cambios = json.model_dump(exclude_unset=True, exclude_none=True)

        if "correo" in cambios:
            cambios["correo"] = str(cambios["correo"]).lower()
            if cambios["correo"] != look_up.correo:
                usuario_existente = repo.buscar_usuario_por_correo(db, cambios["correo"])
                if usuario_existente is not None:
                    raise RecursoDuplicadoError("Ya existe un usuario con ese correo")

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

        look_up.estado = False
        db.commit()
        db.refresh(look_up)
        return look_up
