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
    def buscar_producto_por_nombre(db: Session, id_empresa: int, nombre: str) -> Productos | None:
        return db.query(Productos).filter(
            Productos.id_empresa == id_empresa,
            Productos.nombre == nombre
        ).first()

    @staticmethod
    def listar_productos(db: Session, id_empresa: int, pagina_actual: int, limite: int):
        salto = (pagina_actual - 1) * limite
        total = db.query(Productos).filter(Productos.id_empresa == id_empresa).count()
        lista_productos = db.query(Productos).filter(
            Productos.id_empresa == id_empresa
        ).order_by(Productos.id).offset(salto).limit(limite).all()
        return total, lista_productos

    @staticmethod
    def buscar_producto_por_id(db: Session, id: int, id_empresa: int) -> Productos | None:
        return db.query(Productos).filter(
            Productos.id == id,
            Productos.id_empresa == id_empresa
        ).first()
