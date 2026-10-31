from sqlalchemy.orm import Session
from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
from backend.Productos.tabla import Productos


class DisponibilidadProductoRepository():

    @staticmethod
    def buscar_disponibilidad_producto(db: Session, id_producto: int, id_sucursal: int):
        return db.query(DisponibilidadProductos).filter(
            DisponibilidadProductos.id_producto == id_producto,
            DisponibilidadProductos.id_sucursal == id_sucursal
        ).first()

    @staticmethod
    def guardar_nueva_disponibilidad_producto(db: Session, nueva_disponibilidad_producto: DisponibilidadProductos):
        db.add(nueva_disponibilidad_producto)
        db.commit()
        db.refresh(nueva_disponibilidad_producto)
        return nueva_disponibilidad_producto

    @staticmethod
    def listar_disponibilidad_productos(db: Session, id_sucursal: int, id_empresa: int, pagina_actual: int, limite: int):
        salto = (pagina_actual - 1) * limite
        consulta = db.query(DisponibilidadProductos).join(
            Productos, DisponibilidadProductos.id_producto == Productos.id
        ).filter(
            DisponibilidadProductos.id_sucursal == id_sucursal,
            Productos.id_empresa == id_empresa
        )
        total = consulta.count()
        lista_disponibilidad_productos = consulta.order_by(
            DisponibilidadProductos.id_producto
        ).offset(salto).limit(limite).all()
        return total, lista_disponibilidad_productos

    @staticmethod
    def retirar_disponibilidad_producto(db: Session, look_up: DisponibilidadProductos):
        db.delete(look_up)
        db.commit()
