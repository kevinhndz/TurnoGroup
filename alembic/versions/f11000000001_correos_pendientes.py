"""Bandeja de correo cifrada con reintentos."""

from alembic import op
import sqlalchemy as sa

revision = "f11000000001"
down_revision = "c4a0e4010001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "correos_pendientes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("contenido_cifrado", sa.Text()),
        sa.Column("estado", sa.String(20), nullable=False),
        sa.Column("intentos", sa.Integer(), nullable=False),
        sa.Column("proximo_intento", sa.DateTime(), nullable=False),
        sa.Column("vencimiento", sa.DateTime(), nullable=False),
        sa.Column("fecha_envio", sa.DateTime()),
    )
    op.create_index(
        "ix_correos_pendientes_proximo_intento",
        "correos_pendientes",
        ["proximo_intento"],
    )


def downgrade():
    op.drop_table("correos_pendientes")
