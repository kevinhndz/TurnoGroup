from sqlalchemy.orm import Session
from backend.TiposServicio.tabla import TiposServicio


class TipoServicioRepository():

    @staticmethod
    def listar_tipos_servicio(db: Session, pagina_actual: int, limite: int):
        salto = (pagina_actual - 1) * limite
        total = db.query(TiposServicio).filter(TiposServicio.activo.is_(True)).count()
        lista_tipos_servicio = db.query(TiposServicio).filter(
            TiposServicio.activo.is_(True)
        ).order_by(TiposServicio.id).offset(salto).limit(limite).all()
        return total, lista_tipos_servicio

    @staticmethod
    def buscar_tipo_servicio_por_id(db: Session, id: int) -> TiposServicio | None:
        return db.query(TiposServicio).filter(
            TiposServicio.id == id,
            TiposServicio.activo.is_(True)
        ).first()
