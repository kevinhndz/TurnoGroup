"""Unifica cajero y mesero en un solo rol operativo."""

from typing import Sequence, Union

from alembic import op


revision: str = "7b4f2c1d9a10"
down_revision: Union[str, Sequence[str], None] = "462a01307b4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE vinculos_laborales SET rol = 'Mesero' WHERE rol = 'Cajero'")
    op.execute("UPDATE invitaciones_laborales SET rol = 'Mesero' WHERE rol = 'Cajero'")
    op.drop_constraint("ck_vinculo_rol", "vinculos_laborales", type_="check")
    op.drop_constraint("ck_invitacion_rol", "invitaciones_laborales", type_="check")
    op.create_check_constraint(
        "ck_vinculo_rol",
        "vinculos_laborales",
        "rol IN ('Gerente', 'Administrador', 'Mesero')",
    )
    op.create_check_constraint(
        "ck_invitacion_rol",
        "invitaciones_laborales",
        "rol IN ('Gerente', 'Administrador', 'Mesero')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_invitacion_rol", "invitaciones_laborales", type_="check")
    op.drop_constraint("ck_vinculo_rol", "vinculos_laborales", type_="check")
    op.create_check_constraint(
        "ck_vinculo_rol",
        "vinculos_laborales",
        "rol IN ('Gerente', 'Administrador', 'Mesero', 'Cajero')",
    )
    op.create_check_constraint(
        "ck_invitacion_rol",
        "invitaciones_laborales",
        "rol IN ('Gerente', 'Administrador', 'Mesero', 'Cajero')",
    )
