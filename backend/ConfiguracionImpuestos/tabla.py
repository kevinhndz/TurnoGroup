from sqlalchemy import (
    Boolean, CheckConstraint, Column, ForeignKey, Integer, Numeric, String, UniqueConstraint
)
from database.almacen import miclaseBase
from database.base import PoderAuditor


class ConfiguracionImpuestos(miclaseBase, PoderAuditor):
    __tablename__ = "configuracion_impuestos"
    __table_args__ = (
        UniqueConstraint("id_empresa", name="uq_configuracion_impuestos_empresa"),
        CheckConstraint("porcentaje >= 0 AND porcentaje <= 100", name="ck_impuestos_porcentaje"),
    )

    id = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    nombre = Column(String(80), nullable=True)
    porcentaje = Column(Numeric(6, 3), nullable=False)
    precios_incluyen_impuesto = Column(Boolean, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
