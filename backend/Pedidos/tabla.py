from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Numeric,
    UniqueConstraint,
    CheckConstraint,
)
from database.almacen import miclaseBase


class Pedidos(miclaseBase):
    __tablename__ = "pedidos"
    __table_args__ = (
        UniqueConstraint("id_empresa", "clave_operacion", name="uq_pedido_operacion"),
        CheckConstraint(
            "estado IN ('Abierto','Cerrado','Cancelado')", name="ck_pedido_estado"
        ),
        CheckConstraint("total >= 0", name="ck_pedido_total"),
    )
    id = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    id_sucursal = Column(
        Integer, ForeignKey("sucursales.id"), nullable=False, index=True
    )
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    id_tipo_servicio = Column(Integer, ForeignKey("tipos_servicio.id"), nullable=False)
    id_metodo_pago = Column(Integer, ForeignKey("metodos_pago.id"), nullable=False)
    id_mesa = Column(Integer, ForeignKey("mesas.id"))
    id_descuento = Column(Integer, ForeignKey("descuentos.id"))
    id_caja = Column(Integer, ForeignKey("cajas.id"))
    id_usuario_cobro = Column(Integer, ForeignKey("usuarios.id"))
    id_usuario_cancelacion = Column(Integer, ForeignKey("usuarios.id"))
    clave_operacion = Column(String(36), nullable=False)
    huella_solicitud = Column(String(64), nullable=False)
    fecha_registro = Column(DateTime, nullable=False)
    fecha_entrega = Column(DateTime)
    fecha_pago = Column(DateTime)
    fecha_cancelacion = Column(DateTime)
    estado = Column(String(15), nullable=False, default="Abierto")
    cliente = Column(String(100))
    telefono = Column(String(30))
    direccion = Column(String(500))
    nota = Column(String(1000))
    motivo_cancelacion = Column(String(500))
    subtotal = Column(Numeric(12, 2), nullable=False)
    descuento = Column(Numeric(12, 2), nullable=False)
    impuesto = Column(Numeric(12, 2), nullable=False)
    porcentaje_impuesto = Column(Numeric(6, 3), nullable=False)
    impuesto_incluido = Column(Boolean, nullable=False)
    total = Column(Numeric(12, 2), nullable=False)
    moneda = Column(String(5), nullable=False)


class DetallesPedidos(miclaseBase):
    __tablename__ = "detalles_pedidos"
    __table_args__ = (
        CheckConstraint(
            "cantidad > 0 AND precio_unitario >= 0", name="ck_detalle_cantidad_precio"
        ),
    )
    id = Column(Integer, primary_key=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id"), nullable=False, index=True)
    id_producto = Column(Integer, ForeignKey("productos.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    nota = Column(String(300))
