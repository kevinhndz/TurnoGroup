"""crear tabla categorias

Revision ID: e0fb79e78c58
Revises: 46cb7683d4f9
Create Date: 2026-10-28 13:39:08.376635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e0fb79e78c58'
down_revision: Union[str, Sequence[str], None] = '46cb7683d4f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('categorias',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_empresa', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=60), nullable=False),
    sa.Column('orden_presentacion', sa.Integer(), nullable=False),
    sa.Column('activo', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['id_empresa'], ['empresas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('categorias')
