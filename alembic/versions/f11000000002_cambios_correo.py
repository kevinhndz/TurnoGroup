"""Confirmar correo nuevo antes de sustituir el actual."""

from alembic import op
import sqlalchemy as sa

revision = "f11000000002"
down_revision = "f11000000001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cambios_correo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "id_usuario", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False
        ),
        sa.Column("correo_anterior", sa.String(255), nullable=False),
        sa.Column("correo_nuevo", sa.String(255), nullable=False),
        sa.Column("codigo_protegido", sa.String(64), nullable=False, unique=True),
        sa.Column("vencimiento", sa.DateTime(), nullable=False),
        sa.Column("fecha_uso", sa.DateTime()),
    )
    op.create_index("ix_cambios_correo_id_usuario", "cambios_correo", ["id_usuario"])


def downgrade():
    op.drop_table("cambios_correo")
