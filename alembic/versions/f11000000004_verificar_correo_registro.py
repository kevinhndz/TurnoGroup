"""Verificacion del correo antes de registrar un negocio."""

from alembic import op
import sqlalchemy as sa

revision = "f11000000004"
down_revision = "f11000000003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "verificaciones_correo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("correo", sa.String(255), nullable=False),
        sa.Column("codigo_protegido", sa.String(64), nullable=False, unique=True),
        sa.Column("comprobante_protegido", sa.String(64), unique=True),
        sa.Column("vencimiento", sa.DateTime(), nullable=False),
        sa.Column("fecha_confirmacion", sa.DateTime()),
        sa.Column("fecha_uso", sa.DateTime()),
    )
    op.create_index(
        "ix_verificaciones_correo_correo", "verificaciones_correo", ["correo"]
    )


def downgrade():
    op.drop_table("verificaciones_correo")
