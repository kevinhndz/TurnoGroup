"""Cierra los pedidos que ya tienen un pago registrado."""

from alembic import op

revision = "830ad129b072"
down_revision = "7b4f2c1d9a10"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE pedidos SET estado = 'Cerrado' WHERE fecha_pago IS NOT NULL AND estado = 'Abierto'")


def downgrade():
    op.execute("UPDATE pedidos SET estado = 'Abierto' WHERE estado = 'Cerrado' AND fecha_pago IS NOT NULL AND fecha_entrega IS NULL")
