"""cajas y suscripciones"""
from alembic import op
import sqlalchemy as sa

revision = "102b80fc4ead"
down_revision = "b10f2ca2c533"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('suscripciones', sa.Column('id', sa.Integer(), nullable=False), sa.Column('id_empresa', sa.Integer(), nullable=False), sa.Column('finanzas_habilitadas', sa.Boolean(), nullable=False), sa.Column('estado', sa.String(length=20), nullable=False), sa.Column('inicio_prueba', sa.DateTime(), nullable=False), sa.Column('fin_prueba', sa.DateTime(), nullable=False), sa.Column('id_cliente_paddle', sa.String(length=100), nullable=True), sa.Column('id_suscripcion_paddle', sa.String(length=100), nullable=True), sa.Column('proximo_cobro', sa.DateTime(), nullable=True), sa.ForeignKeyConstraint(['id_empresa'], ['empresas.id']), sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('id_cliente_paddle'), sa.UniqueConstraint('id_empresa'), sa.UniqueConstraint('id_suscripcion_paddle'))
    op.create_table('cajas', sa.Column('id', sa.Integer(), nullable=False), sa.Column('id_empresa', sa.Integer(), nullable=False), sa.Column('id_sucursal', sa.Integer(), nullable=False), sa.Column('id_usuario', sa.Integer(), nullable=False), sa.Column('fecha_apertura', sa.DateTime(), nullable=False), sa.Column('fecha_cierre', sa.DateTime(), nullable=True), sa.Column('monto_inicial', sa.Numeric(precision=12, scale=2), nullable=False), sa.Column('efectivo_esperado', sa.Numeric(precision=12, scale=2), nullable=True), sa.Column('efectivo_contado', sa.Numeric(precision=12, scale=2), nullable=True), sa.Column('diferencia', sa.Numeric(precision=12, scale=2), nullable=True), sa.Column('nota', sa.String(length=500), nullable=True), sa.CheckConstraint('monto_inicial >= 0', name='ck_caja_monto_inicial'), sa.ForeignKeyConstraint(['id_empresa'], ['empresas.id']), sa.ForeignKeyConstraint(['id_sucursal'], ['sucursales.id']), sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id']), sa.PrimaryKeyConstraint('id'))
    op.create_index(op.f('ix_cajas_id_empresa'), 'cajas', ['id_empresa'], unique=False)
    op.create_index(op.f('ix_cajas_id_sucursal'), 'cajas', ['id_sucursal'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_cajas_id_sucursal'), table_name='cajas')
    op.drop_index(op.f('ix_cajas_id_empresa'), table_name='cajas')
    op.drop_table('cajas')
    op.drop_table('suscripciones')
