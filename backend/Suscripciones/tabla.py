from datetime import timedelta
from core.operaciones import ahora
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime
from database.almacen import miclaseBase


class Suscripciones(miclaseBase):
    __tablename__ = "suscripciones"
    id = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False, unique=True)
    finanzas_habilitadas = Column(Boolean, nullable=False, default=False)
    estado = Column(String(20), nullable=False, default="Prueba")
    inicio_prueba = Column(DateTime, nullable=False, default=ahora)
    fin_prueba = Column(
        DateTime, nullable=False, default=lambda: ahora() + timedelta(days=30)
    )
    id_cliente_paddle = Column(String(100), unique=True)
    id_suscripcion_paddle = Column(String(100), unique=True)
    proximo_cobro = Column(DateTime)
