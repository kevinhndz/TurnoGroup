from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.Categorias.repository import CategoriaRepository as repo_categoria
from backend.Empresas.repository import EmpresaRepository as repo_empresa
from backend.Productos.repository import ProductoRepository as repo
from backend.Productos.schema import Revisar_Json_Nuevo_Producto, Revisar_Json_Editar_Producto
from backend.Productos.tabla import Productos
from core.exceptions import RecursoNoEncontradoError, RecursoDuplicadoError


class ProductoService():

    @staticmethod
    def crear_producto_service(json: Revisar_Json_Nuevo_Producto, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, json.id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        if json.id_categoria is not None:
            categoria = repo_categoria.buscar_categoria_por_id(
                db, json.id_categoria, json.id_empresa
            )
            if categoria is None or not categoria.activo:
                raise RecursoNoEncontradoError("No se encontro la categoria de esta empresa")

        look_up = repo.buscar_producto_por_nombre(db, json.id_empresa, json.nombre)
        if look_up is not None:
            raise RecursoDuplicadoError("Ya existe un producto con ese nombre en la empresa")

        nuevo_producto = Productos(
            id_empresa=json.id_empresa,
            id_categoria=json.id_categoria,
            nombre=json.nombre,
            descripcion=json.descripcion,
            precio=json.precio
        )
        return repo.guardar_nuevo_producto(db, nuevo_producto)

    @staticmethod
    def listar_productos_service(id_empresa: int, pagina_actual: int, limite: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        total, lista_productos = repo.listar_productos(db, id_empresa, pagina_actual, limite)
        total_paginas = (total + limite - 1) // limite
        return {
            "total": total, "pagina_actual": pagina_actual, "limite": limite,
            "total_paginas": total_paginas, "data": lista_productos
        }

    @staticmethod
    def ver_producto_service(id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_producto_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el producto")

        return look_up

    @staticmethod
    def editar_producto_service(json: Revisar_Json_Editar_Producto, id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_producto_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el producto")

        cambios = json.model_dump(exclude_unset=True)
        if not cambios:
            raise HTTPException(status_code=422, detail="Debes enviar al menos un campo para editar")
        for campo, valor in cambios.items():
            if valor is None and campo not in ('id_categoria', 'descripcion'):
                raise HTTPException(status_code=422, detail="El campo " + campo + " no acepta null")

        if "nombre" in cambios and cambios["nombre"] != look_up.nombre:
            producto_existente = repo.buscar_producto_por_nombre(db, id_empresa, cambios["nombre"])
            if producto_existente is not None:
                raise RecursoDuplicadoError("Ya existe un producto con ese nombre en la empresa")

        if "id_categoria" in cambios and cambios["id_categoria"] is not None:
            categoria = repo_categoria.buscar_categoria_por_id(
                db, cambios["id_categoria"], id_empresa
            )
            if categoria is None or not categoria.activo:
                raise RecursoNoEncontradoError("No se encontro la categoria de esta empresa")

        # Recorre el diccionario y actualiza cada campo enviado.
        for campo, valor in cambios.items():
            if valor is not None:
                setattr(look_up, campo, valor)
            elif campo == "id_categoria" or campo == "descripcion":
                setattr(look_up, campo, None)

        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def desactivar_producto_service(id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_producto_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el producto")

        look_up.disponible = False
        db.commit()
        db.refresh(look_up)
        return look_up
