from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from database.almacen import miclaseBase


class InvitacionesLaborales(miclaseBase):
    __tablename__ = "invitaciones_laborales"
    __table_args__ = (CheckConstraint("rol IN ('Gerente', 'Administrador', 'Mesero')", name="ck_invitacion_rol"),)

    id = Column(Integer, primary_key=True)
    correo = Column(String(255), nullable=False)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    id_usuario_invitante = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    rol = Column(String(40), nullable=False)
    codigo_protegido = Column(String(64), nullable=False, unique=True)
    fecha_creacion = Column(DateTime, nullable=False)
    vencimiento = Column(DateTime, nullable=False)
    fecha_aceptacion = Column(DateTime, nullable=True)
    fecha_revocacion = Column(DateTime, nullable=True)


class SucursalesInvitacion(miclaseBase):
    __tablename__ = "sucursales_invitacion"

    id_invitacion = Column(Integer, ForeignKey("invitaciones_laborales.id"), primary_key=True)
    id_sucursal = Column(Integer, ForeignKey("sucursales.id"), primary_key=True)
