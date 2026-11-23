from sqlalchemy import Column, DateTime, Integer, String

from database.almacen import miclaseBase


class VerificacionesCorreo(miclaseBase):
    __tablename__ = "verificaciones_correo"

    id = Column(Integer, primary_key=True)
    correo = Column(String(255), nullable=False, index=True)
    codigo_protegido = Column(String(64), unique=True, nullable=False)
    comprobante_protegido = Column(String(64), unique=True)
    vencimiento = Column(DateTime, nullable=False)
    fecha_confirmacion = Column(DateTime)
    fecha_uso = Column(DateTime)
