from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from database.almacen import miclaseBase


class CodigosRecuperacionMfa(miclaseBase):
    __tablename__ = "codigos_recuperacion_mfa"

    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    codigo_protegido = Column(String(64), unique=True, nullable=False)
    fecha_uso = Column(DateTime)
