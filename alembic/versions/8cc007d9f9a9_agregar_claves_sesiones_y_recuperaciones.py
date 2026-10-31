"""agregar claves sesiones y recuperaciones

Revision ID: 8cc007d9f9a9
Revises: 0ac89592a3e5
Create Date: 2026-10-31 13:40:42.657981

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Identificadores de esta migracion.
revision: str = '8cc007d9f9a9'
down_revision: Union[str, Sequence[str], None] = '0ac89592a3e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agrega claves protegidas, sesiones y recuperaciones."""
    op.create_table('recuperaciones_clave',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=False),
    sa.Column('codigo_protegido', sa.String(length=64), nullable=False),
    sa.Column('fecha_inicio', sa.DateTime(), nullable=False),
    sa.Column('vencimiento', sa.DateTime(), nullable=False),
    sa.Column('fecha_uso', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('codigo_protegido')
    )
    op.create_index(op.f('ix_recuperaciones_clave_id_usuario'), 'recuperaciones_clave', ['id_usuario'], unique=False)
    op.create_table('sesiones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=False),
    sa.Column('token_protegido', sa.String(length=64), nullable=False),
    sa.Column('fecha_inicio', sa.DateTime(), nullable=False),
    sa.Column('vencimiento', sa.DateTime(), nullable=False),
    sa.Column('fecha_revocacion', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token_protegido')
    )
    op.create_index(op.f('ix_sesiones_id_usuario'), 'sesiones', ['id_usuario'], unique=False)
    op.add_column('usuarios', sa.Column('clave_protegida', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Retira las tablas y la columna de esta etapa."""
    op.drop_column('usuarios', 'clave_protegida')
    op.drop_index(op.f('ix_sesiones_id_usuario'), table_name='sesiones')
    op.drop_table('sesiones')
    op.drop_index(op.f('ix_recuperaciones_clave_id_usuario'), table_name='recuperaciones_clave')
    op.drop_table('recuperaciones_clave')
