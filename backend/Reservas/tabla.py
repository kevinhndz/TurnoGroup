from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint
from database.almacen import miclaseBase


class Reservas(miclaseBase):
    __tablename__ = "reservas"
    __table_args__ = (
        CheckConstraint("fin > inicio AND personas > 0", name="ck_reserva_horario"),
        CheckConstraint(
            "estado IN ('Confirmada','Atendida','Cancelada')", name="ck_reserva_estado"
        ),
    )
    id = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    id_sucursal = Column(
        Integer, ForeignKey("sucursales.id"), nullable=False, index=True
    )
    id_mesa = Column(Integer, ForeignKey("mesas.id"), nullable=False, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cliente = Column(String(100), nullable=False)
    telefono = Column(String(30))
    personas = Column(Integer, nullable=False)
    inicio = Column(DateTime, nullable=False)
    fin = Column(DateTime, nullable=False)
    estado = Column(String(15), nullable=False, default="Confirmada")
    nota = Column(String(500))
