from sqlalchemy import Boolean, CheckConstraint, Column, Integer, String
from database.almacen import miclaseBase


class MetodosPago(miclaseBase):
    __tablename__ = "metodos_pago"
    __table_args__ = (
        CheckConstraint("clave_concepto IN ('efectivo', 'transferencia', 'tarjeta')", name="ck_metodos_pago_clave"),
    )

    id = Column(Integer, primary_key=True)
    clave_concepto = Column(String(30), unique=True, nullable=False)
    nombre_visible = Column(String(60), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
