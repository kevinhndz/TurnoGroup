from sqlalchemy.orm import Session
from backend.Sucursales.tabla import Sucursales


class SucursalRespository():

    @staticmethod
    def buscar_sucursal(db: Session, id_empresa: int, nombre: str) -> Sucursales | None:
        return db.query(Sucursales).filter(
            Sucursales.id_empresa == id_empresa,
            Sucursales.nombre == nombre
        ).first()

    @staticmethod
    def buscar_sucursal_principal(db: Session, id_empresa: int) -> Sucursales | None:
        return db.query(Sucursales).filter(
            Sucursales.id_empresa == id_empresa,
            Sucursales.es_principal.is_(True),
            Sucursales.activo.is_(True)
        ).first()

    @staticmethod
    def guardar_nueva_sucursal(db: Session, nueva_sucursal: Sucursales) -> Sucursales:
        db.add(nueva_sucursal)
        db.commit()
        db.refresh(nueva_sucursal)
        return nueva_sucursal
