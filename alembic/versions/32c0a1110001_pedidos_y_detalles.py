"""pedidos y detalles"""
from alembic import op
import sqlalchemy as sa

revision = "32c0a1110001"
down_revision = "102b80fc4ead"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('pedidos', sa.Column('id', sa.Integer(), nullable=False), sa.Column('id_empresa', sa.Integer(), nullable=False), sa.Column('id_sucursal', sa.Integer(), nullable=False), sa.Column('id_usuario', sa.Integer(), nullable=False), sa.Column('id_tipo_servicio', sa.Integer(), nullable=False), sa.Column('id_metodo_pago', sa.Integer(), nullable=False), sa.Column('id_mesa', sa.Integer(), nullable=True), sa.Column('id_descuento', sa.Integer(), nullable=True), sa.Column('id_caja', sa.Integer(), nullable=True), sa.Column('id_usuario_cobro', sa.Integer(), nullable=True), sa.Column('id_usuario_cancelacion', sa.Integer(), nullable=True), sa.Column('clave_operacion', sa.String(length=36), nullable=False), sa.Column('huella_solicitud', sa.String(length=64), nullable=False), sa.Column('fecha_registro', sa.DateTime(), nullable=False), sa.Column('fecha_entrega', sa.DateTime(), nullable=True), sa.Column('fecha_pago', sa.DateTime(), nullable=True), sa.Column('fecha_cancelacion', sa.DateTime(), nullable=True), sa.Column('estado', sa.String(length=15), nullable=False), sa.Column('cliente', sa.String(length=100), nullable=True), sa.Column('telefono', sa.String(length=30), nullable=True), sa.Column('direccion', sa.String(length=500), nullable=True), sa.Column('nota', sa.String(length=1000), nullable=True), sa.Column('motivo_cancelacion', sa.String(length=500), nullable=True), sa.Column('subtotal', sa.Numeric(precision=12, scale=2), nullable=False), sa.Column('descuento', sa.Numeric(precision=12, scale=2), nullable=False), sa.Column('impuesto', sa.Numeric(precision=12, scale=2), nullable=False), sa.Column('porcentaje_impuesto', sa.Numeric(precision=6, scale=3), nullable=False), sa.Column('impuesto_incluido', sa.Boolean(), nullable=False), sa.Column('total', sa.Numeric(precision=12, scale=2), nullable=False), sa.Column('moneda', sa.String(length=5), nullable=False), sa.CheckConstraint("estado IN ('Abierto','Cerrado','Cancelado')", name='ck_pedido_estado'), sa.CheckConstraint('total >= 0', name='ck_pedido_total'), sa.ForeignKeyConstraint(['id_caja'], ['cajas.id']), sa.ForeignKeyConstraint(['id_descuento'], ['descuentos.id']), sa.ForeignKeyConstraint(['id_empresa'], ['empresas.id']), sa.ForeignKeyConstraint(['id_mesa'], ['mesas.id']), sa.ForeignKeyConstraint(['id_metodo_pago'], ['metodos_pago.id']), sa.ForeignKeyConstraint(['id_sucursal'], ['sucursales.id']), sa.ForeignKeyConstraint(['id_tipo_servicio'], ['tipos_servicio.id']), sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id']), sa.ForeignKeyConstraint(['id_usuario_cancelacion'], ['usuarios.id']), sa.ForeignKeyConstraint(['id_usuario_cobro'], ['usuarios.id']), sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('id_empresa', 'clave_operacion', name='uq_pedido_operacion'))
    op.create_index(op.f('ix_pedidos_id_empresa'), 'pedidos', ['id_empresa'], unique=False)
    op.create_index(op.f('ix_pedidos_id_sucursal'), 'pedidos', ['id_sucursal'], unique=False)
    op.create_table('detalles_pedidos', sa.Column('id', sa.Integer(), nullable=False), sa.Column('id_pedido', sa.Integer(), nullable=False), sa.Column('id_producto', sa.Integer(), nullable=False), sa.Column('nombre', sa.String(length=100), nullable=False), sa.Column('cantidad', sa.Integer(), nullable=False), sa.Column('precio_unitario', sa.Numeric(precision=12, scale=2), nullable=False), sa.Column('nota', sa.String(length=300), nullable=True), sa.CheckConstraint('cantidad > 0 AND precio_unitario >= 0', name='ck_detalle_cantidad_precio'), sa.ForeignKeyConstraint(['id_pedido'], ['pedidos.id']), sa.ForeignKeyConstraint(['id_producto'], ['productos.id']), sa.PrimaryKeyConstraint('id'))
    op.create_index(op.f('ix_detalles_pedidos_id_pedido'), 'detalles_pedidos', ['id_pedido'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_detalles_pedidos_id_pedido'), table_name='detalles_pedidos')
    op.drop_table('detalles_pedidos')
    op.drop_index(op.f('ix_pedidos_id_sucursal'), table_name='pedidos')
    op.drop_index(op.f('ix_pedidos_id_empresa'), table_name='pedidos')
    op.drop_table('pedidos')
