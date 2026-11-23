from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database.almacen import miclaseBase
from database.base import PoderAuditor


class Empresas(miclaseBase, PoderAuditor):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True)
    tipo_negocio = Column(String)
    codigo_pais = Column(String)
    zona_horaria = Column(String)
    codigo_moneda = Column(String)
    estado = Column(String, default="En Prueba")
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
