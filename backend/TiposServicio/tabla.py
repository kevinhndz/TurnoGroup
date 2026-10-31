from sqlalchemy import Boolean, CheckConstraint, Column, Integer, String
from database.almacen import miclaseBase


class TiposServicio(miclaseBase):
    __tablename__ = "tipos_servicio"
    __table_args__ = (
        CheckConstraint("clave_concepto IN ('comer_aqui', 'para_llevar', 'domicilio')", name="ck_tipos_servicio_clave"),
    )

    id = Column(Integer, primary_key=True)
    clave_concepto = Column(String(30), unique=True, nullable=False)
    nombre_visible = Column(String(60), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
