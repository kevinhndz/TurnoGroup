"""agregar roles contexto de sesion e invitaciones

Revision ID: b10f2ca2c533
Revises: 98e58dd039ac
Create Date: 2026-10-31 14:07:54.759857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Identificadores de esta migracion.
revision: str = 'b10f2ca2c533'
down_revision: Union[str, Sequence[str], None] = '98e58dd039ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agrega roles, contexto autorizado e invitaciones."""
    op.create_table('invitaciones_laborales',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('correo', sa.String(length=255), nullable=False),
    sa.Column('id_empresa', sa.Integer(), nullable=False),
    sa.Column('id_usuario_invitante', sa.Integer(), nullable=False),
    sa.Column('rol', sa.String(length=40), nullable=False),
    sa.Column('codigo_protegido', sa.String(length=64), nullable=False),
    sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
    sa.Column('vencimiento', sa.DateTime(), nullable=False),
    sa.Column('fecha_aceptacion', sa.DateTime(), nullable=True),
    sa.Column('fecha_revocacion', sa.DateTime(), nullable=True),
    sa.CheckConstraint("rol IN ('Gerente', 'Administrador', 'Mesero', 'Cajero')", name='ck_invitacion_rol'),
    sa.ForeignKeyConstraint(['id_empresa'], ['empresas.id'], ),
    sa.ForeignKeyConstraint(['id_usuario_invitante'], ['usuarios.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('codigo_protegido')
    )
    op.create_index(op.f('ix_invitaciones_laborales_id_empresa'), 'invitaciones_laborales', ['id_empresa'], unique=False)
    op.create_table('sucursales_invitacion',
    sa.Column('id_invitacion', sa.Integer(), nullable=False),
    sa.Column('id_sucursal', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_invitacion'], ['invitaciones_laborales.id'], ),
    sa.ForeignKeyConstraint(['id_sucursal'], ['sucursales.id'], ),
    sa.PrimaryKeyConstraint('id_invitacion', 'id_sucursal')
    )
    op.add_column('sesiones', sa.Column('id_vinculo_laboral', sa.Integer(), nullable=True))
    op.add_column('sesiones', sa.Column('id_sucursal', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_sesion_sucursal', 'sesiones', 'sucursales', ['id_sucursal'], ['id'])
    op.create_foreign_key('fk_sesion_vinculo_laboral', 'sesiones', 'vinculos_laborales', ['id_vinculo_laboral'], ['id'])
    op.add_column('usuarios', sa.Column('rol_plataforma', sa.String(length=30), server_default='Usuario', nullable=False))
    op.add_column('vinculos_laborales', sa.Column('activo', sa.Boolean(), server_default='true', nullable=False))
    op.create_check_constraint('ck_usuario_rol_plataforma', 'usuarios', "rol_plataforma IN ('Usuario', 'Superadministrador')")
    op.create_check_constraint('ck_vinculo_rol', 'vinculos_laborales', "rol IN ('Gerente', 'Administrador', 'Mesero', 'Cajero')")


def downgrade() -> None:
    """Retira los cambios de esta etapa."""
    op.drop_constraint('ck_vinculo_rol', 'vinculos_laborales', type_='check')
    op.drop_constraint('ck_usuario_rol_plataforma', 'usuarios', type_='check')
    op.drop_column('vinculos_laborales', 'activo')
    op.drop_column('usuarios', 'rol_plataforma')
    op.drop_constraint('fk_sesion_vinculo_laboral', 'sesiones', type_='foreignkey')
    op.drop_constraint('fk_sesion_sucursal', 'sesiones', type_='foreignkey')
    op.drop_column('sesiones', 'id_sucursal')
    op.drop_column('sesiones', 'id_vinculo_laboral')
    op.drop_table('sucursales_invitacion')
    op.drop_index(op.f('ix_invitaciones_laborales_id_empresa'), table_name='invitaciones_laborales')
    op.drop_table('invitaciones_laborales')
