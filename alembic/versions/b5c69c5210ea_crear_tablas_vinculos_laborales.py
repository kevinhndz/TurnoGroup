"""crear tablas vinculos laborales

Revision ID: b5c69c5210ea
Revises: 7cf13b5f224a
Create Date: 2026-10-29 20:02:11.038428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5c69c5210ea'
down_revision: Union[str, Sequence[str], None] = '7cf13b5f224a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'vinculos_laborales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('id_empresa', sa.Integer(), nullable=False),
        sa.Column('rol', sa.String(length=40), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['id_empresa'], ['empresas.id']),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id_usuario', 'id_empresa', name='uq_vinculo_usuario_empresa')
    )
    op.create_table(
        'asignaciones_sucursales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_vinculo_laboral', sa.Integer(), nullable=False),
        sa.Column('id_sucursal', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id_sucursal'], ['sucursales.id']),
        sa.ForeignKeyConstraint(['id_vinculo_laboral'], ['vinculos_laborales.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'id_vinculo_laboral',
            'id_sucursal',
            name='uq_asignacion_vinculo_sucursal'
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('asignaciones_sucursales')
    op.drop_table('vinculos_laborales')
