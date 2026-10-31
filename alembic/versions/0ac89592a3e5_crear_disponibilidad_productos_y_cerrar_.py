"""crear disponibilidad productos y cerrar contratos

Revision ID: 0ac89592a3e5
Revises: a0ff5fcb8c17
Create Date: 2026-10-30 23:22:56.358991

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0ac89592a3e5'
down_revision: Union[str, Sequence[str], None] = 'a0ff5fcb8c17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crea disponibilidad y evita nombres duplicados por empresa."""
    op.create_table('disponibilidad_productos',
    sa.Column('id_producto', sa.Integer(), nullable=False),
    sa.Column('id_sucursal', sa.Integer(), nullable=False),
    sa.Column('disponible', sa.Boolean(), nullable=False),
    sa.Column('precio_especial', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.CheckConstraint('precio_especial >= 0', name='ck_disponibilidad_precio_especial'),
    sa.ForeignKeyConstraint(['id_producto'], ['productos.id'], ),
    sa.ForeignKeyConstraint(['id_sucursal'], ['sucursales.id'], ),
    sa.PrimaryKeyConstraint('id_producto', 'id_sucursal')
    )
    op.create_unique_constraint('uq_categorias_empresa_nombre', 'categorias', ['id_empresa', 'nombre'])
    op.create_unique_constraint('uq_productos_empresa_nombre', 'productos', ['id_empresa', 'nombre'])


def downgrade() -> None:
    """Revierte las tablas y restricciones de esta revision."""
    op.drop_constraint('uq_productos_empresa_nombre', 'productos', type_='unique')
    op.drop_constraint('uq_categorias_empresa_nombre', 'categorias', type_='unique')
    op.drop_table('disponibilidad_productos')
