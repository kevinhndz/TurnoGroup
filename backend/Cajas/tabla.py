from sqlalchemy import (
    Boolean,
    String,
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Numeric,
    CheckConstraint,
)
from database.almacen import miclaseBase


class Cajas(miclaseBase):
    __tablename__ = "cajas"
    __table_args__ = (
        CheckConstraint("monto_inicial >= 0", name="ck_caja_monto_inicial"),
    )
    id = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    id_sucursal = Column(
        Integer, ForeignKey("sucursales.id"), nullable=False, index=True
    )
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_apertura = Column(DateTime, nullable=False)
    fecha_cierre = Column(DateTime)
    monto_inicial = Column(Numeric(12, 2), nullable=False)
    efectivo_esperado = Column(Numeric(12, 2))
    efectivo_contado = Column(Numeric(12, 2))
    diferencia = Column(Numeric(12, 2))
    nota = Column(String(500))
