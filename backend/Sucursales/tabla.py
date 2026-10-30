from database.almacen import miclaseBase
from database.base import PoderAuditor
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint


class Sucursales(miclaseBase, PoderAuditor):

    __tablename__ = "sucursales"
    __table_args__ = (
        UniqueConstraint("id_empresa", "nombre", name="uq_sucursal_empresa_nombre"),
    )

    id = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=True)
    es_principal = Column(Boolean, default=False, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
