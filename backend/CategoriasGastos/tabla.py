from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from database.almacen import miclaseBase
from database.base import PoderAuditor


class CategoriasGastos(miclaseBase, PoderAuditor):
    __tablename__ = "categorias_gastos"
    __table_args__ = (
        UniqueConstraint("id_empresa", "nombre", name="uq_categoria_gasto_empresa_nombre"),
    )

    id = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
