"""crear tabla mesas

Revision ID: 1dc9a91baae3
Revises: b5c69c5210ea
Create Date: 2026-10-29 20:34:40.088659

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1dc9a91baae3'
down_revision: Union[str, Sequence[str], None] = 'b5c69c5210ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'mesas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_sucursal', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=60), nullable=False),
        sa.Column('capacidad', sa.Integer(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['id_sucursal'], ['sucursales.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id_sucursal', 'nombre', name='uq_mesa_sucursal_nombre')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('mesas')
