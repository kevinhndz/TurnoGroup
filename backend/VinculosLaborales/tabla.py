from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint, Boolean, CheckConstraint
from database.almacen import miclaseBase
from database.base import PoderAuditor


class VinculosLaborales(miclaseBase, PoderAuditor):
    __tablename__ = "vinculos_laborales"
    __table_args__ = (
        CheckConstraint("rol IN ('Gerente', 'Administrador', 'Mesero', 'Cajero')", name="ck_vinculo_rol"),
        UniqueConstraint("id_usuario", "id_empresa", name="uq_vinculo_usuario_empresa"),
    )

    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    rol = Column(String(40), nullable=False)
    activo = Column(Boolean, nullable=False, default=True, server_default="true")


class AsignacionesSucursales(miclaseBase):
    __tablename__ = "asignaciones_sucursales"
    __table_args__ = (
        UniqueConstraint(
            "id_vinculo_laboral",
            "id_sucursal",
            name="uq_asignacion_vinculo_sucursal"
        ),
    )

    id = Column(Integer, primary_key=True)
    id_vinculo_laboral = Column(Integer, ForeignKey("vinculos_laborales.id"), nullable=False)
    id_sucursal = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
