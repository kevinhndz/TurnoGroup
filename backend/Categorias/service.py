from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.Categorias.repository import CategoriaRepository as repo
from backend.Categorias.schema import Revisar_Json_Nueva_Categoria, Revisar_Json_Editar_Categoria
from backend.Categorias.tabla import Categorias
from backend.Empresas.repository import EmpresaRepository as repo_empresa
from core.exceptions import RecursoDuplicadoError, RecursoNoEncontradoError


class CategoriaService():

    @staticmethod
    def crear_categoria_service(json: Revisar_Json_Nueva_Categoria, db: Session, id_empresa: int):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_categoria_por_nombre(db, id_empresa, json.nombre)

        if look_up is not None:
            raise RecursoDuplicadoError("Ya existe una categoria con ese nombre")

        nueva_categoria = Categorias(
            id_empresa=id_empresa,
            nombre=json.nombre,
            orden_presentacion=json.orden_presentacion
        )
        return repo.guardar_nueva_categoria(db, nueva_categoria)

    @staticmethod
    def listar_categorias_service(id_empresa: int, pagina_actual: int, limite: int, db: Session, id_sucursal=None, filtros=None):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        total, lista_categorias = repo.listar_categorias(
            db, id_empresa, pagina_actual, limite, id_sucursal, filtros=filtros)
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_categorias
        }

    @staticmethod
    def ver_categoria_service(id: int, id_empresa: int, db: Session, id_sucursal=None):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_categoria_por_id(db, id, id_empresa, id_sucursal)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la categoria")

        return look_up

    @staticmethod
    def editar_categoria_service(json: Revisar_Json_Editar_Categoria, id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_categoria_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la categoria")

        # Guarda en un diccionario solo los campos que llegaron en la peticion.
        cambios = json.model_dump(exclude_unset=True)
        if not cambios:
            raise HTTPException(status_code=422, detail="Debes enviar al menos un campo para editar")
        for campo, valor in cambios.items():
            if valor is None:
                raise HTTPException(status_code=422, detail="El campo " + campo + " no acepta null")

        if "nombre" in cambios and cambios["nombre"] != look_up.nombre:
            categoria_existente = repo.buscar_categoria_por_nombre(
                db, look_up.id_empresa, cambios["nombre"]
            )
            if categoria_existente is not None:
                raise RecursoDuplicadoError("Ya existe una categoria con ese nombre")

        # Recorre el diccionario y actualiza cada campo enviado.
        for campo, valor in cambios.items():
            setattr(look_up, campo, valor)

        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def desactivar_categoria_service(id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_categoria_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la categoria")

        look_up.activo = False
        db.commit()
        db.refresh(look_up)
        return look_up
