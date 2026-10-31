from sqlalchemy import Boolean, Column, ForeignKey, Integer, CheckConstraint
from database.almacen import miclaseBase


class ServiciosSucursales(miclaseBase):
    __tablename__ = "servicios_sucursales"
    __table_args__ = (
        CheckConstraint("NOT mesas_habilitadas OR habilitado", name="ck_servicio_mesas_habilitado"),
        CheckConstraint("NOT reservas_habilitadas OR mesas_habilitadas", name="ck_servicio_reservas_mesas"),
    )

    id_sucursal = Column(Integer, ForeignKey("sucursales.id"), primary_key=True)
    id_tipo_servicio = Column(Integer, ForeignKey("tipos_servicio.id"), primary_key=True)
    habilitado = Column(Boolean, default=False, nullable=False)
    mesas_habilitadas = Column(Boolean, default=False, nullable=False)
    reservas_habilitadas = Column(Boolean, default=False, nullable=False)
