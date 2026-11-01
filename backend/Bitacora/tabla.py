from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Index
from database.almacen import miclaseBase
from core.operaciones import ahora


class Bitacora(miclaseBase):
    __tablename__ = "bitacora"
    __table_args__ = (
        Index(
            "ix_bitacora_empresa_sucursal_fecha", "id_empresa", "id_sucursal", "fecha"
        ),
    )
    id = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    id_sucursal = Column(Integer, ForeignKey("sucursales.id"), nullable=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    recurso = Column(String(20), nullable=False)
    id_registro = Column(Integer, nullable=False)
    cliente = Column(String(100), nullable=True)
    accion = Column(String(60), nullable=False)
    fecha = Column(DateTime, nullable=False, default=ahora)
