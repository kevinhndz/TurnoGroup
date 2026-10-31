from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from database.almacen import miclaseBase


class RecuperacionesClave(miclaseBase):
    __tablename__ = "recuperaciones_clave"

    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    codigo_protegido = Column(String(64), unique=True, nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    vencimiento = Column(DateTime, nullable=False)
    fecha_uso = Column(DateTime, nullable=True)
