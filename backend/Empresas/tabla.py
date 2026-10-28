from database.base import PoderAuditor
from database.almacen import miclaseBase
from sqlalchemy import Integer, String, Column, DateTime
from datetime import datetime


class Empresas(miclaseBase, PoderAuditor):

    __tablename__ = "empresas"

    id = Column(Integer, primary_key= True)
    nombre = Column(String, unique = True)
    tipo_negocio = Column(String)
    codigo_pais = Column(String)
    zona_horaria = Column(String)
    codigo_moneda = Column(String)
    estado = Column(String, default= "En Prueba")
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
