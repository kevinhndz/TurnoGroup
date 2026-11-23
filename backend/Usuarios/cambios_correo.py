from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from database.almacen import miclaseBase


class CambiosCorreo(miclaseBase):
    __tablename__ = "cambios_correo"

    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    correo_anterior = Column(String(255), nullable=False)
    correo_nuevo = Column(String(255), nullable=False)
    codigo_protegido = Column(String(64), unique=True, nullable=False)
    vencimiento = Column(DateTime, nullable=False)
    fecha_uso = Column(DateTime)
