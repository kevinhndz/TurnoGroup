"""Codigos de respaldo de un solo uso para MFA."""

from alembic import op
import sqlalchemy as sa

revision = "f11000000005"
down_revision = "f11000000004"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "codigos_recuperacion_mfa",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "id_usuario", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False
        ),
        sa.Column("codigo_protegido", sa.String(64), unique=True, nullable=False),
        sa.Column("fecha_uso", sa.DateTime()),
    )
    op.create_index(
        "ix_codigos_recuperacion_mfa_id_usuario",
        "codigos_recuperacion_mfa",
        ["id_usuario"],
    )


def downgrade():
    op.drop_table("codigos_recuperacion_mfa")
