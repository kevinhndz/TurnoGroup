from sqlalchemy.orm import Session
from backend.Descuentos.tabla import Descuentos


class DescuentoRepository():

    @staticmethod
    def buscar_descuento_por_nombre(db: Session, id_empresa: int, nombre: str) -> Descuentos | None:
        return db.query(Descuentos).filter(
            Descuentos.id_empresa == id_empresa,
            Descuentos.nombre == nombre
        ).first()

    @staticmethod
    def guardar_nuevo_descuento(db: Session, nuevo_descuento: Descuentos) -> Descuentos:
        db.add(nuevo_descuento)
        db.commit()
        db.refresh(nuevo_descuento)
        return nuevo_descuento

    @staticmethod
    def listar_descuentos(db: Session, id_empresa: int, pagina_actual: int, limite: int):
        salto = (pagina_actual - 1) * limite
        total = db.query(Descuentos).filter(Descuentos.id_empresa == id_empresa).count()
        lista_descuentos = db.query(Descuentos).filter(
            Descuentos.id_empresa == id_empresa
        ).order_by(Descuentos.id).offset(salto).limit(limite).all()
        return total, lista_descuentos

    @staticmethod
    def buscar_descuento_por_id(db: Session, id: int, id_empresa: int) -> Descuentos | None:
        return db.query(Descuentos).filter(
            Descuentos.id == id,
            Descuentos.id_empresa == id_empresa
        ).first()
