from sqlalchemy.orm import Session
from backend.Categorias.repository import CategoriaRepository as repo_categoria
from backend.Productos.repository import ProductoRepository as repo
from backend.Productos.schema import Revisar_Json_Nuevo_Producto, Revisar_Json_Editar_Producto
from backend.Productos.tabla import Productos
from core.exceptions import RecursoNoEncontradoError


class ProductoService():

    @staticmethod
    def crear_producto_service(json: Revisar_Json_Nuevo_Producto, db: Session):
        if json.id_categoria is not None:
            categoria = repo_categoria.buscar_categoria_por_id(
                db, json.id_categoria, json.id_empresa
            )
            if categoria is None:
                raise RecursoNoEncontradoError("No se encontro la categoria de esta empresa")

        nuevo_producto = Productos(
            id_empresa=json.id_empresa,
            id_categoria=json.id_categoria,
            nombre=json.nombre,
            descripcion=json.descripcion,
            precio=json.precio
        )
        return repo.guardar_nuevo_producto(db, nuevo_producto)

    @staticmethod
    def listar_productos_service(id_empresa: int, db: Session):
        return repo.listar_productos(db, id_empresa)

    @staticmethod
    def ver_producto_service(id: int, id_empresa: int, db: Session):
        look_up = repo.buscar_producto_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el producto")

        return look_up

    @staticmethod
    def editar_producto_service(json: Revisar_Json_Editar_Producto, id: int, id_empresa: int, db: Session):
        look_up = repo.buscar_producto_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el producto")

        cambios = json.model_dump(exclude_unset=True)

        if "id_categoria" in cambios and cambios["id_categoria"] is not None:
            categoria = repo_categoria.buscar_categoria_por_id(
                db, cambios["id_categoria"], id_empresa
            )
            if categoria is None:
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
        look_up = repo.buscar_producto_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el producto")

        look_up.disponible = False
        db.commit()
        db.refresh(look_up)
        return look_up
