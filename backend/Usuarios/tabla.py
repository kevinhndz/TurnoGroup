from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from database.almacen import miclaseBase
from database.base import PoderAuditor


class Usuarios(miclaseBase, PoderAuditor):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    correo = Column(String(255), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    estado = Column(Boolean, default=True, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
