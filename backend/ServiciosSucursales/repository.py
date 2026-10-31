from sqlalchemy.orm import Session
from backend.ServiciosSucursales.tabla import ServiciosSucursales
from backend.TiposServicio.tabla import TiposServicio


class ServicioSucursalRepository():

    @staticmethod
    def buscar_servicio_sucursal(db: Session, id_sucursal: int, id_tipo_servicio: int) -> ServiciosSucursales | None:
        return db.query(ServiciosSucursales).filter(
            ServiciosSucursales.id_sucursal == id_sucursal,
            ServiciosSucursales.id_tipo_servicio == id_tipo_servicio
        ).first()

    @staticmethod
    def guardar_nuevo_servicio_sucursal(db: Session, nuevo_servicio_sucursal: ServiciosSucursales) -> ServiciosSucursales:
        db.add(nuevo_servicio_sucursal)
        db.commit()
        db.refresh(nuevo_servicio_sucursal)
        return nuevo_servicio_sucursal

    @staticmethod
    def listar_servicios_sucursales(
        db: Session, id_sucursal: int, solo_habilitados: bool, pagina_actual: int, limite: int
    ):
        salto = (pagina_actual - 1) * limite
        consulta = db.query(ServiciosSucursales).join(
            TiposServicio, ServiciosSucursales.id_tipo_servicio == TiposServicio.id
        ).filter(ServiciosSucursales.id_sucursal == id_sucursal)
        if solo_habilitados:
            consulta = consulta.filter(
                ServiciosSucursales.habilitado.is_(True),
                TiposServicio.activo.is_(True)
            )
        total = consulta.count()
        lista_servicios_sucursales = consulta.order_by(
            ServiciosSucursales.id_tipo_servicio
        ).offset(salto).limit(limite).all()
        return total, lista_servicios_sucursales
