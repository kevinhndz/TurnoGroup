from sqlalchemy import Column, Integer, String, Text, DateTime
from database.almacen import miclaseBase


class CorreosPendientes(miclaseBase):
    __tablename__ = "correos_pendientes"

    id = Column(Integer, primary_key=True)
    tipo = Column(String(30), nullable=False)
    contenido_cifrado = Column(Text, nullable=True)
    estado = Column(String(20), nullable=False, default="pendiente")
    intentos = Column(Integer, nullable=False, default=0)
    proximo_intento = Column(DateTime, nullable=False, index=True)
    vencimiento = Column(DateTime, nullable=False)
    fecha_envio = Column(DateTime, nullable=True)
