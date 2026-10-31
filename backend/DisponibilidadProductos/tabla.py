from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, Numeric
from database.almacen import miclaseBase


class DisponibilidadProductos(miclaseBase):
    __tablename__ = "disponibilidad_productos"
    __table_args__ = (
        CheckConstraint("precio_especial >= 0", name="ck_disponibilidad_precio_especial"),
    )

    id_producto = Column(Integer, ForeignKey("productos.id"), primary_key=True)
    id_sucursal = Column(Integer, ForeignKey("sucursales.id"), primary_key=True)
    disponible = Column(Boolean, default=True, nullable=False)
    precio_especial = Column(Numeric(12, 2), nullable=True)
