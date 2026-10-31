from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from database.almacen import miclaseBase


class Sesiones(miclaseBase):
    __tablename__ = "sesiones"

    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    id_vinculo_laboral = Column(Integer, ForeignKey("vinculos_laborales.id", name="fk_sesion_vinculo_laboral"), nullable=True)
    id_sucursal = Column(Integer, ForeignKey("sucursales.id", name="fk_sesion_sucursal"), nullable=True)
    token_protegido = Column(String(64), unique=True, nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    vencimiento = Column(DateTime, nullable=False)
    fecha_revocacion = Column(DateTime, nullable=True)
