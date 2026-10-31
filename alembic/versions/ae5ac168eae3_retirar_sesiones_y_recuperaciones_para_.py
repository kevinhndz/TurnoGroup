"""retirar sesiones y recuperaciones para dejarlas pendientes

Revision ID: ae5ac168eae3
Revises: 8cc007d9f9a9
Create Date: 2026-10-31 13:46:45.108450

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Identificadores de esta migracion.
revision: str = 'ae5ac168eae3'
down_revision: Union[str, Sequence[str], None] = '8cc007d9f9a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Retira las tablas que se implementaran mas adelante."""
    op.drop_index(op.f('ix_recuperaciones_clave_id_usuario'), table_name='recuperaciones_clave')
    op.drop_table('recuperaciones_clave')
    op.drop_index(op.f('ix_sesiones_id_usuario'), table_name='sesiones')
    op.drop_table('sesiones')


def downgrade() -> None:
    """Restaura las tablas de la revision anterior."""
    op.create_table('sesiones',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('id_usuario', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('token_protegido', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.Column('fecha_inicio', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('vencimiento', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('fecha_revocacion', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id'], name=op.f('sesiones_id_usuario_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('sesiones_pkey')),
    sa.UniqueConstraint('token_protegido', name=op.f('sesiones_token_protegido_key'), postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index(op.f('ix_sesiones_id_usuario'), 'sesiones', ['id_usuario'], unique=False)
    op.create_table('recuperaciones_clave',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('id_usuario', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('codigo_protegido', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.Column('fecha_inicio', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('vencimiento', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('fecha_uso', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id'], name=op.f('recuperaciones_clave_id_usuario_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('recuperaciones_clave_pkey')),
    sa.UniqueConstraint('codigo_protegido', name=op.f('recuperaciones_clave_codigo_protegido_key'), postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index(op.f('ix_recuperaciones_clave_id_usuario'), 'recuperaciones_clave', ['id_usuario'], unique=False)
