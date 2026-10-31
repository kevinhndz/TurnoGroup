from database.base import PoderAuditor
from database.almacen import miclaseBase
from sqlalchemy import UniqueConstraint, Boolean, Column, ForeignKey, Integer, Numeric, String, Text


class Productos(miclaseBase, PoderAuditor):
    __tablename__ = "productos"
    __table_args__ = (
        UniqueConstraint("id_empresa", "nombre", name="uq_productos_empresa_nombre"),
    )

    id = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Numeric(10, 2), nullable=False)
    ruta_imagen = Column(String(255), nullable=True)
    disponible = Column(Boolean, default=True, nullable=False)
