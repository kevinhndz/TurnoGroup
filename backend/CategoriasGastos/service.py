from sqlalchemy.orm import Session
from backend.CategoriasGastos.repository import CategoriaGastoRepository as repo
from backend.CategoriasGastos.schema import (
    Revisar_Json_Crear_Categoria_Gasto,
    Revisar_Json_Editar_Categoria_Gasto,
)
from backend.CategoriasGastos.tabla import CategoriasGastos
from backend.Empresas.repository import EmpresaRepository as repo_empresa
from core.exceptions import RecursoDuplicadoError, RecursoNoEncontradoError


class CategoriaGastoService():

    @staticmethod
    def crear_categoria_gasto_service(json: Revisar_Json_Crear_Categoria_Gasto, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, json.id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_categoria_gasto_por_nombre(db, json.id_empresa, json.nombre)
        if look_up is not None:
            raise RecursoDuplicadoError("Ya existe una categoria de gasto con ese nombre en la empresa")

        nueva_categoria_gasto = CategoriasGastos(
            id_empresa=json.id_empresa,
            nombre=json.nombre
        )
        return repo.guardar_nueva_categoria_gasto(db, nueva_categoria_gasto)

    @staticmethod
    def listar_categorias_gastos_service(id_empresa: int, pagina_actual: int, limite: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        total, lista_categorias_gastos = repo.listar_categorias_gastos(db, id_empresa, pagina_actual, limite)
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_categorias_gastos
        }

    @staticmethod
    def ver_categoria_gasto_service(id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_categoria_gasto_por_id(db, id, id_empresa)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la categoria de gasto")

        return look_up

    @staticmethod
    def editar_categoria_gasto_service(json: Revisar_Json_Editar_Categoria_Gasto, id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_categoria_gasto_por_id(db, id, id_empresa)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la categoria de gasto")

        cambios = json.model_dump(exclude_unset=True, exclude_none=True)

        if "nombre" in cambios and cambios["nombre"] != look_up.nombre:
            categoria_gasto_existente = repo.buscar_categoria_gasto_por_nombre(
                db, id_empresa, cambios["nombre"]
            )
            if categoria_gasto_existente is not None:
                raise RecursoDuplicadoError("Ya existe una categoria de gasto con ese nombre en la empresa")

        for campo, valor in cambios.items():
            setattr(look_up, campo, valor)

        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def desactivar_categoria_gasto_service(id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_categoria_gasto_por_id(db, id, id_empresa)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la categoria de gasto")

        look_up.activo = False
        db.commit()
        db.refresh(look_up)
        return look_up
