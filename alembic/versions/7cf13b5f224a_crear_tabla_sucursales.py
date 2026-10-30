"""crear tabla sucursales

Revision ID: 7cf13b5f224a
Revises: 8c9af0c5ee0d
Create Date: 2026-10-29 19:27:30.547140

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cf13b5f224a'
down_revision: Union[str, Sequence[str], None] = '8c9af0c5ee0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'sucursales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_empresa', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('direccion', sa.String(length=255), nullable=False),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('es_principal', sa.Boolean(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['id_empresa'], ['empresas.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id_empresa', 'nombre', name='uq_sucursal_empresa_nombre')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('sucursales')
