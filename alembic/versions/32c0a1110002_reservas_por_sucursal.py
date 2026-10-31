"""reservas por sucursal"""
from alembic import op
import sqlalchemy as sa

revision = "32c0a1110002"
down_revision = "32c0a1110001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('reservas', sa.Column('id', sa.Integer(), nullable=False), sa.Column('id_empresa', sa.Integer(), nullable=False), sa.Column('id_sucursal', sa.Integer(), nullable=False), sa.Column('id_mesa', sa.Integer(), nullable=False), sa.Column('id_usuario', sa.Integer(), nullable=False), sa.Column('cliente', sa.String(length=100), nullable=False), sa.Column('telefono', sa.String(length=30), nullable=True), sa.Column('personas', sa.Integer(), nullable=False), sa.Column('inicio', sa.DateTime(), nullable=False), sa.Column('fin', sa.DateTime(), nullable=False), sa.Column('estado', sa.String(length=15), nullable=False), sa.Column('nota', sa.String(length=500), nullable=True), sa.CheckConstraint("estado IN ('Confirmada','Atendida','Cancelada')", name='ck_reserva_estado'), sa.CheckConstraint('fin > inicio AND personas > 0', name='ck_reserva_horario'), sa.ForeignKeyConstraint(['id_empresa'], ['empresas.id']), sa.ForeignKeyConstraint(['id_mesa'], ['mesas.id']), sa.ForeignKeyConstraint(['id_sucursal'], ['sucursales.id']), sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id']), sa.PrimaryKeyConstraint('id'))
    op.create_index(op.f('ix_reservas_id_empresa'), 'reservas', ['id_empresa'], unique=False)
    op.create_index(op.f('ix_reservas_id_mesa'), 'reservas', ['id_mesa'], unique=False)
    op.create_index(op.f('ix_reservas_id_sucursal'), 'reservas', ['id_sucursal'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_reservas_id_sucursal'), table_name='reservas')
    op.drop_index(op.f('ix_reservas_id_mesa'), table_name='reservas')
    op.drop_index(op.f('ix_reservas_id_empresa'), table_name='reservas')
    op.drop_table('reservas')
