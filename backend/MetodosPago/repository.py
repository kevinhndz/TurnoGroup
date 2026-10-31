from sqlalchemy.orm import Session
from backend.MetodosPago.tabla import MetodosPago


class MetodoPagoRepository():

    @staticmethod
    def listar_metodos_pago(db: Session, pagina_actual: int, limite: int):
        salto = (pagina_actual - 1) * limite
        total = db.query(MetodosPago).filter(MetodosPago.activo.is_(True)).count()
        lista_metodos_pago = db.query(MetodosPago).filter(
            MetodosPago.activo.is_(True)
        ).order_by(MetodosPago.id).offset(salto).limit(limite).all()
        return total, lista_metodos_pago

    @staticmethod
    def buscar_metodo_pago_por_id(db: Session, id: int) -> MetodosPago | None:
        return db.query(MetodosPago).filter(
            MetodosPago.id == id,
            MetodosPago.activo.is_(True)
        ).first()
