from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.DisponibilidadProductos.repository import DisponibilidadProductoRepository as repo
from backend.DisponibilidadProductos.schema import (
    Revisar_Json_Crear_Disponibilidad_Producto,
    Revisar_Json_Editar_Disponibilidad_Producto,
)
from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
from backend.Productos.repository import ProductoRepository as repo_producto
from backend.Sucursales.repository import SucursalRespository as repo_sucursal
from core.exceptions import RecursoDuplicadoError, RecursoNoEncontradoError


class DisponibilidadProductoService():

    @staticmethod
    def crear_disponibilidad_producto_service(json: Revisar_Json_Crear_Disponibilidad_Producto, id_empresa: int, db: Session, id_sucursal: int):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)
        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro el recurso")
        producto = repo_producto.buscar_producto_por_id(db, json.id_producto, id_empresa)
        if producto is None:
            raise RecursoNoEncontradoError("No se encontro el recurso")

        look_up = repo.buscar_disponibilidad_producto(db, json.id_producto, id_sucursal)
        if look_up is not None:
            raise RecursoDuplicadoError("Ya existe esta asignacion de producto y sucursal")

        nueva_disponibilidad_producto = DisponibilidadProductos(
            id_producto=json.id_producto,
            id_sucursal=id_sucursal,
            disponible=json.disponible,
            precio_especial=json.precio_especial
        )
        return repo.guardar_nueva_disponibilidad_producto(db, nueva_disponibilidad_producto)

    @staticmethod
    def listar_disponibilidad_productos_service(id_sucursal: int, id_empresa: int, pagina_actual: int, limite: int, db: Session):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)
        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro el recurso")

        total, lista_disponibilidad_productos = repo.listar_disponibilidad_productos(
            db, id_sucursal, id_empresa, pagina_actual, limite
        )
        total_paginas = (total + limite - 1) // limite
        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_disponibilidad_productos
        }

    @staticmethod
    def ver_disponibilidad_producto_service(id_producto: int, id_sucursal: int, id_empresa: int, db: Session):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)
        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro el recurso")
        producto = repo_producto.buscar_producto_por_id(db, id_producto, id_empresa)
        if producto is None:
            raise RecursoNoEncontradoError("No se encontro el recurso")
        look_up = repo.buscar_disponibilidad_producto(db, id_producto, id_sucursal)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el recurso")

        return look_up

    @staticmethod
    def editar_disponibilidad_producto_service(json: Revisar_Json_Editar_Disponibilidad_Producto, id_producto: int, id_sucursal: int, id_empresa: int, db: Session):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)
        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro el recurso")
        producto = repo_producto.buscar_producto_por_id(db, id_producto, id_empresa)
        if producto is None:
            raise RecursoNoEncontradoError("No se encontro el recurso")
        look_up = repo.buscar_disponibilidad_producto(db, id_producto, id_sucursal)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el recurso")

        cambios = json.model_dump(exclude_unset=True)
        if not cambios:
            raise HTTPException(status_code=422, detail="Debes enviar al menos un campo para editar")
        if "disponible" in cambios and cambios["disponible"] is None:
            raise HTTPException(status_code=422, detail="El campo disponible no acepta null")
        for campo, valor in cambios.items():
            setattr(look_up, campo, valor)
        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def retirar_disponibilidad_producto_service(id_producto: int, id_sucursal: int, id_empresa: int, db: Session):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)
        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro el recurso")
        producto = repo_producto.buscar_producto_por_id(db, id_producto, id_empresa)
        if producto is None:
            raise RecursoNoEncontradoError("No se encontro el recurso")
        look_up = repo.buscar_disponibilidad_producto(db, id_producto, id_sucursal)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el recurso")

        repo.retirar_disponibilidad_producto(db, look_up)
