from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, CheckConstraint
from database.almacen import miclaseBase
from database.base import PoderAuditor


class Usuarios(miclaseBase, PoderAuditor):
    __tablename__ = "usuarios"
    __table_args__ = (CheckConstraint("rol_plataforma IN ('Usuario', 'Superadministrador')", name="ck_usuario_rol_plataforma"),)

    id = Column(Integer, primary_key=True)
    correo = Column(String(255), unique=True, nullable=False)
    clave_protegida = Column(String(255), nullable=True)
    nombre = Column(String(100), nullable=False)
    rol_plataforma = Column(String(30), nullable=False, default="Usuario", server_default="Usuario")
    estado = Column(Boolean, default=True, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
