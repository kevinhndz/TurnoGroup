"""crear configuracion impuestos y descuentos

Revision ID: e70f32512013
Revises: 1dc9a91baae3
Create Date: 2026-10-30 13:05:38.107827

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e70f32512013'
down_revision: Union[str, Sequence[str], None] = '1dc9a91baae3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crea las tablas de impuestos y descuentos."""
    op.create_table('configuracion_impuestos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_empresa', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=80), nullable=True),
    sa.Column('porcentaje', sa.Numeric(precision=6, scale=3), nullable=False),
    sa.Column('precios_incluyen_impuesto', sa.Boolean(), nullable=False),
    sa.Column('activo', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.CheckConstraint('porcentaje >= 0 AND porcentaje <= 100', name='ck_impuestos_porcentaje'),
    sa.ForeignKeyConstraint(['id_empresa'], ['empresas.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id_empresa', name='uq_configuracion_impuestos_empresa')
    )
    op.create_table('descuentos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_empresa', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('tipo_descuento', sa.String(length=12), nullable=False),
    sa.Column('valor', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('activo', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.CheckConstraint("tipo_descuento != 'Porcentaje' OR valor <= 100", name='ck_descuentos_porcentaje'),
    sa.CheckConstraint("tipo_descuento IN ('Porcentaje', 'CantidadFija')", name='ck_descuentos_tipo'),
    sa.CheckConstraint('valor >= 0', name='ck_descuentos_valor'),
    sa.ForeignKeyConstraint(['id_empresa'], ['empresas.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id_empresa', 'nombre', name='uq_descuento_empresa_nombre')
    )


def downgrade() -> None:
    """Elimina las tablas de esta revision."""
    op.drop_table('descuentos')
    op.drop_table('configuracion_impuestos')
