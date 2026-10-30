from sqlalchemy import (
    Boolean, CheckConstraint, Column, ForeignKey, Integer, Numeric, String, UniqueConstraint
)
from database.almacen import miclaseBase
from database.base import PoderAuditor


class Descuentos(miclaseBase, PoderAuditor):
    __tablename__ = "descuentos"
    __table_args__ = (
        UniqueConstraint("id_empresa", "nombre", name="uq_descuento_empresa_nombre"),
        CheckConstraint("valor >= 0", name="ck_descuentos_valor"),
        CheckConstraint("tipo_descuento IN ('Porcentaje', 'CantidadFija')", name="ck_descuentos_tipo"),
        CheckConstraint("tipo_descuento != 'Porcentaje' OR valor <= 100", name="ck_descuentos_porcentaje"),
    )

    id = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    tipo_descuento = Column(String(12), nullable=False)
    valor = Column(Numeric(12, 2), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
