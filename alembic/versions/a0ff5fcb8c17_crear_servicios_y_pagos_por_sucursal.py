"""crear servicios y pagos por sucursal

Revision ID: a0ff5fcb8c17
Revises: 293bdc2c7982
Create Date: 2026-10-30 23:14:37.185553

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a0ff5fcb8c17'
down_revision: Union[str, Sequence[str], None] = '293bdc2c7982'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crea las tablas y carga las opciones conocidas."""
    op.create_table('metodos_pago',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('clave_concepto', sa.String(length=30), nullable=False),
    sa.Column('nombre_visible', sa.String(length=60), nullable=False),
    sa.Column('activo', sa.Boolean(), nullable=False),
    sa.CheckConstraint("clave_concepto IN ('efectivo', 'transferencia', 'tarjeta')", name='ck_metodos_pago_clave'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('clave_concepto')
    )
    op.create_table('tipos_servicio',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('clave_concepto', sa.String(length=30), nullable=False),
    sa.Column('nombre_visible', sa.String(length=60), nullable=False),
    sa.Column('activo', sa.Boolean(), nullable=False),
    sa.CheckConstraint("clave_concepto IN ('comer_aqui', 'para_llevar', 'domicilio')", name='ck_tipos_servicio_clave'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('clave_concepto')
    )
    op.create_table('pagos_sucursales',
    sa.Column('id_sucursal', sa.Integer(), nullable=False),
    sa.Column('id_metodo_pago', sa.Integer(), nullable=False),
    sa.Column('habilitado', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['id_metodo_pago'], ['metodos_pago.id'], ),
    sa.ForeignKeyConstraint(['id_sucursal'], ['sucursales.id'], ),
    sa.PrimaryKeyConstraint('id_sucursal', 'id_metodo_pago')
    )
    op.create_table('servicios_sucursales',
    sa.Column('id_sucursal', sa.Integer(), nullable=False),
    sa.Column('id_tipo_servicio', sa.Integer(), nullable=False),
    sa.Column('habilitado', sa.Boolean(), nullable=False),
    sa.Column('mesas_habilitadas', sa.Boolean(), nullable=False),
    sa.Column('reservas_habilitadas', sa.Boolean(), nullable=False),
    sa.CheckConstraint('NOT mesas_habilitadas OR habilitado', name='ck_servicio_mesas_habilitado'),
    sa.CheckConstraint('NOT reservas_habilitadas OR mesas_habilitadas', name='ck_servicio_reservas_mesas'),
    sa.ForeignKeyConstraint(['id_sucursal'], ['sucursales.id'], ),
    sa.ForeignKeyConstraint(['id_tipo_servicio'], ['tipos_servicio.id'], ),
    sa.PrimaryKeyConstraint('id_sucursal', 'id_tipo_servicio')
    )


    tipos_servicio = sa.table(
        "tipos_servicio",
        sa.column("clave_concepto", sa.String(30)),
        sa.column("nombre_visible", sa.String(60)),
        sa.column("activo", sa.Boolean()),
    )
    op.bulk_insert(tipos_servicio, [
        {"clave_concepto": "comer_aqui", "nombre_visible": "Comer aqui", "activo": True},
        {"clave_concepto": "para_llevar", "nombre_visible": "Para llevar", "activo": True},
        {"clave_concepto": "domicilio", "nombre_visible": "Domicilio", "activo": True},
    ])
    metodos_pago = sa.table(
        "metodos_pago",
        sa.column("clave_concepto", sa.String(30)),
        sa.column("nombre_visible", sa.String(60)),
        sa.column("activo", sa.Boolean()),
    )
    op.bulk_insert(metodos_pago, [
        {"clave_concepto": "efectivo", "nombre_visible": "Efectivo", "activo": True},
        {"clave_concepto": "transferencia", "nombre_visible": "Transferencia", "activo": True},
        {"clave_concepto": "tarjeta", "nombre_visible": "Tarjeta", "activo": True},
    ])


def downgrade() -> None:
    """Elimina las tablas de esta revision."""
    op.drop_table('servicios_sucursales')
    op.drop_table('pagos_sucursales')
    op.drop_table('tipos_servicio')
    op.drop_table('metodos_pago')
