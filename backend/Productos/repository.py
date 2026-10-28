from sqlalchemy.orm import Session
from backend.Productos.tabla import Productos


class ProductoRepository():

    @staticmethod
    def guardar_nuevo_producto(db: Session, nuevo_producto: Productos) -> Productos:
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)
        return nuevo_producto

    @staticmethod
    def listar_productos(db: Session, id_empresa: int):
        return db.query(Productos).filter(
            Productos.id_empresa == id_empresa
        ).all()

    @staticmethod
    def buscar_producto_por_id(db: Session, id: int, id_empresa: int) -> Productos | None:
        return db.query(Productos).filter(
            Productos.id == id,
            Productos.id_empresa == id_empresa
        ).first()
