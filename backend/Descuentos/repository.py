from core.listados import pagina_listado
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
    def listar_descuentos(db: Session, id_empresa: int, pagina_actual: int, limite: int, filtros=None):
        consulta = db.query(Descuentos).filter(Descuentos.id_empresa == id_empresa)
        return pagina_listado(consulta, Descuentos, pagina_actual, limite, filtros)

    @staticmethod
    def buscar_descuento_por_id(db: Session, id: int, id_empresa: int) -> Descuentos | None:
        return db.query(Descuentos).filter(
            Descuentos.id == id,
            Descuentos.id_empresa == id_empresa
        ).first()
