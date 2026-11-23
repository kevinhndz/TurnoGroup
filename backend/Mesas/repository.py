from sqlalchemy.orm import Session

from backend.Mesas.tabla import Mesas
from core.listados import pagina_listado


class MesaRepository:
    @staticmethod
    def buscar_mesa_por_nombre(
        db: Session, id_sucursal: int, nombre: str
    ) -> Mesas | None:
        return (
            db.query(Mesas)
            .filter(Mesas.id_sucursal == id_sucursal, Mesas.nombre == nombre)
            .first()
        )

    @staticmethod
    def guardar_nueva_mesa(db: Session, nueva_mesa: Mesas) -> Mesas:
        db.add(nueva_mesa)
        db.flush()

        return nueva_mesa

    @staticmethod
    def listar_mesas(
        db: Session, id_sucursal: int, pagina_actual: int, limite: int, filtros=None
    ):
        consulta = db.query(Mesas).filter(Mesas.id_sucursal == id_sucursal)

        return pagina_listado(consulta, Mesas, pagina_actual, limite, filtros)

    @staticmethod
    def buscar_mesa_por_id(db: Session, id: int, id_sucursal: int) -> Mesas | None:
        return (
            db.query(Mesas)
            .filter(Mesas.id == id, Mesas.id_sucursal == id_sucursal)
            .first()
        )

    @staticmethod
    def agregar(db, registro):
        db.add(registro)

        return registro

    @staticmethod
    def guardar_cambios(db):
        db.flush()

    @staticmethod
    def actualizar(db, registro):
        db.refresh(registro)

        return registro

    @staticmethod
    def listar_mesas_de_sucursal(db, id_sucursal):
        return db.query(Mesas).filter(Mesas.id_sucursal == id_sucursal).all()
