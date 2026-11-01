from sqlalchemy import Boolean, Column, ForeignKey, Integer
from database.almacen import miclaseBase


class DisponibilidadProductos(miclaseBase):
    __tablename__ = "disponibilidad_productos"

    id_producto = Column(Integer, ForeignKey("productos.id"), primary_key=True)
    id_sucursal = Column(Integer, ForeignKey("sucursales.id"), primary_key=True)
    disponible = Column(Boolean, default=True, nullable=False)
