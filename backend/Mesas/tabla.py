from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint, Boolean
from database.almacen import miclaseBase
from database.base import PoderAuditor


class Mesas(miclaseBase, PoderAuditor):
    __tablename__ = "mesas"
    __table_args__ = (
        UniqueConstraint("id_sucursal", "nombre", name="uq_mesa_sucursal_nombre"),
    )

    id = Column(Integer, primary_key=True)
    id_sucursal = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    nombre = Column(String(60), nullable=False)
    capacidad = Column(Integer, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
