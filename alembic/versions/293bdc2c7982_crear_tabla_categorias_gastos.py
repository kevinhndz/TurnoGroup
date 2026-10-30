"""crear tabla categorias gastos

Revision ID: 293bdc2c7982
Revises: e70f32512013
Create Date: 2026-10-30 15:35:38.729067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '293bdc2c7982'
down_revision: Union[str, Sequence[str], None] = 'e70f32512013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crea la tabla de categorias de gastos."""
    op.create_table('categorias_gastos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_empresa', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('activo', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['id_empresa'], ['empresas.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id_empresa', 'nombre', name='uq_categoria_gasto_empresa_nombre')
    )


def downgrade() -> None:
    """Elimina la tabla de esta revision."""
    op.drop_table('categorias_gastos')
