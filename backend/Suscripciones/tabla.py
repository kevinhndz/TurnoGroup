from datetime import timedelta
from core.operaciones import ahora
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime, Numeric, CheckConstraint, UniqueConstraint, Text
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
    renovacion_automatica = Column(Boolean, nullable=False, default=True, server_default="true")


class TarjetasSuscripcion(miclaseBase):
    __tablename__ = "tarjetas_suscripcion"
    __table_args__ = (
        CheckConstraint("mes >= 1 AND mes <= 12", name="ck_tarjeta_mes"),
        CheckConstraint("prioridad IN ('Principal', 'Secundaria', 'Adicional')", name="ck_tarjeta_prioridad"),
        CheckConstraint("modo IN ('simulado', 'paddle')", name="ck_tarjeta_modo"),
    )
    id = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    titular = Column(String(100), nullable=False)
    marca = Column(String(20), nullable=False)
    ultimos_cuatro = Column(String(4), nullable=False)
    mes = Column(Integer, nullable=False)
    anio = Column(Integer, nullable=False)
    prioridad = Column(String(15), nullable=False, default="Adicional")
    modo = Column(String(10), nullable=False, default="simulado")
    referencia_proveedor = Column(String(100), unique=True)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_registro = Column(DateTime, nullable=False, default=ahora)


class ComprobantesSuscripcion(miclaseBase):
    __tablename__ = "comprobantes_suscripcion"
    __table_args__ = (UniqueConstraint("id_empresa", "concepto", name="uq_comprobante_empresa_concepto"),)
    id = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    concepto = Column(String(100), nullable=False)
    nombre_empresa = Column(String(100), nullable=False)
    fecha = Column(DateTime, nullable=False, default=ahora)
    periodo_inicio = Column(DateTime, nullable=False)
    periodo_fin = Column(DateTime, nullable=False)
    importe = Column(Numeric(12, 2), nullable=False)
    moneda = Column(String(3), nullable=False, default="USD")
    modo = Column(String(10), nullable=False, default="simulado")
    referencia_proveedor = Column(String(100), unique=True)
    detalle = Column(Text, nullable=False)
