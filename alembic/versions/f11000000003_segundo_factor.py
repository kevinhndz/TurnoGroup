"""Segundo factor cifrado para cuentas de plataforma."""

from alembic import op
import sqlalchemy as sa

revision = "f11000000003"
down_revision = "f11000000002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("usuarios", sa.Column("mfa_secreto_cifrado", sa.String(255)))
    op.add_column("usuarios", sa.Column("mfa_ultimo_contador", sa.Integer()))


def downgrade():
    op.drop_column("usuarios", "mfa_ultimo_contador")
    op.drop_column("usuarios", "mfa_secreto_cifrado")
