from database.base import PoderAuditor
from database.almacen import miclaseBase
from sqlalchemy import UniqueConstraint, Boolean, Column, ForeignKey, Integer, String


class Categorias(miclaseBase, PoderAuditor):
    __tablename__ = "categorias"
    __table_args__ = (
        UniqueConstraint("id_empresa", "nombre", name="uq_categorias_empresa_nombre"),
    )

    id = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    nombre = Column(String(60), nullable=False)
    orden_presentacion = Column(Integer, default=1, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
