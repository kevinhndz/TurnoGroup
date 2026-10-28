from sqlalchemy.orm import Session
from backend.Empresas.repository import EmpresaRepository as repo_empresa
from backend.Categorias.repository import CategoriaRepository as repo
from backend.Categorias.schema import Revisar_Json_Nueva_Categoria, Revisar_Json_Editar_Categoria
from backend.Categorias.tabla import Categorias
from core.exceptions import RecursoDuplicadoError, RecursoNoEncontradoError


class CategoriaService():

    @staticmethod
    def crear_categoria_service(json: Revisar_Json_Nueva_Categoria, db: Session):
        empresa_actual = repo_empresa.buscar_empresa_actual(db)

        if empresa_actual is None:
            raise RecursoNoEncontradoError("No hay una empresa de demostracion registrada")

        look_up = repo.buscar_categoria_por_nombre(db, empresa_actual.id, json.nombre)

        if look_up is not None:
            raise RecursoDuplicadoError("Ya existe una categoria activa con ese nombre")

        nueva_categoria = Categorias(
            id_empresa=empresa_actual.id,
            nombre=json.nombre,
            orden_presentacion=json.orden_presentacion
        )
        return repo.guardar_nueva_categoria(db, nueva_categoria)

    @staticmethod
    def listar_categorias_service(pagina_actual: int, limite: int, db: Session):
        empresa_actual = repo_empresa.buscar_empresa_actual(db)

        if empresa_actual is None:
            raise RecursoNoEncontradoError("No hay una empresa de demostracion registrada")

        total, lista_categorias = repo.listar_categorias(
            db, empresa_actual.id, pagina_actual, limite
        )
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_categorias
        }

    @staticmethod
    def ver_categoria_service(id: int, db: Session):
        empresa_actual = repo_empresa.buscar_empresa_actual(db)

        if empresa_actual is None:
            raise RecursoNoEncontradoError("No hay una empresa de demostracion registrada")

        look_up = repo.buscar_categoria_por_id(db, id, empresa_actual.id)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la categoria activa")

        return look_up

    @staticmethod
    def editar_categoria_service(json: Revisar_Json_Editar_Categoria, id: int, db: Session):
        look_up = CategoriaService.ver_categoria_service(id, db)

        if json.nombre is not None and json.nombre != look_up.nombre:
            categoria_existente = repo.buscar_categoria_por_nombre(
                db, look_up.id_empresa, json.nombre
            )
            if categoria_existente is not None:
                raise RecursoDuplicadoError("Ya existe una categoria activa con ese nombre")

        if json.nombre is not None:
            look_up.nombre = json.nombre
        if json.orden_presentacion is not None:
            look_up.orden_presentacion = json.orden_presentacion

        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def desactivar_categoria_service(id: int, db: Session):
        look_up = CategoriaService.ver_categoria_service(id, db)
        look_up.activo = False
        db.commit()
        db.refresh(look_up)
        return look_up
