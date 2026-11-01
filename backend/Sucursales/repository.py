from core.listados import pagina_listado
from sqlalchemy.orm import Session
from backend.Sucursales.tabla import Sucursales


class SucursalRespository():

    @staticmethod
    def buscar_sucursal(db: Session, id_empresa: int, nombre: str, direccion=None) -> Sucursales | None:
        consulta = db.query(Sucursales).filter(
            Sucursales.id_empresa == id_empresa,
            Sucursales.nombre == nombre
        )
        if direccion is not None:
            consulta = consulta.filter(Sucursales.direccion == direccion)
        return consulta.first()

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

    @staticmethod
    def listar_sucursales(db: Session, id_empresa: int, pagina_actual: int, limite: int, id_sucursal=None, filtros=None):
        consulta = db.query(Sucursales).filter(Sucursales.id_empresa == id_empresa)
        if id_sucursal is not None:
            consulta = consulta.filter(Sucursales.id == id_sucursal)
        return pagina_listado(consulta, Sucursales, pagina_actual, limite, filtros)

    @staticmethod
    def buscar_sucursal_por_id(db: Session, id: int, id_empresa: int) -> Sucursales | None:
        return db.query(Sucursales).filter(
            Sucursales.id == id,
            Sucursales.id_empresa == id_empresa
        ).first()

    @staticmethod
    def buscar_sucursal_por_id_sin_empresa(db: Session, id: int) -> Sucursales | None:
        return db.query(Sucursales).filter(Sucursales.id == id).first()
