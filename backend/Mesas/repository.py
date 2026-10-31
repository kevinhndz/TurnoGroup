from sqlalchemy.orm import Session
from backend.Mesas.tabla import Mesas


class MesaRepository():

    @staticmethod
    def buscar_mesa_por_nombre(db: Session, id_sucursal: int, nombre: str) -> Mesas | None:
        return db.query(Mesas).filter(
            Mesas.id_sucursal == id_sucursal,
            Mesas.nombre == nombre
        ).first()

    @staticmethod
    def guardar_nueva_mesa(db: Session, nueva_mesa: Mesas) -> Mesas:
        db.add(nueva_mesa)
        db.commit()
        db.refresh(nueva_mesa)
        return nueva_mesa

    @staticmethod
    def listar_mesas(db: Session, id_sucursal: int, pagina_actual: int, limite: int):
        salto = (pagina_actual - 1) * limite
        total = db.query(Mesas).filter(Mesas.id_sucursal == id_sucursal).count()
        lista_mesas = db.query(Mesas).filter(
            Mesas.id_sucursal == id_sucursal
        ).order_by(Mesas.id).offset(salto).limit(limite).all()
        return total, lista_mesas

    @staticmethod
    def buscar_mesa_por_id(db: Session, id: int, id_sucursal: int) -> Mesas | None:
        return db.query(Mesas).filter(
            Mesas.id == id,
            Mesas.id_sucursal == id_sucursal
        ).first()
