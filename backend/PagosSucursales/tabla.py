from sqlalchemy import Boolean, Column, ForeignKey, Integer
from database.almacen import miclaseBase


class PagosSucursales(miclaseBase):
    __tablename__ = "pagos_sucursales"
    id_sucursal = Column(Integer, ForeignKey("sucursales.id"), primary_key=True)
    id_metodo_pago = Column(Integer, ForeignKey("metodos_pago.id"), primary_key=True)
    habilitado = Column(Boolean, default=False, nullable=False)
