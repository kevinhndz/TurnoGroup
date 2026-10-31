"""asignar plan a empresas existentes

Revision ID: 32c0a1110003
Revises: 32c0a1110002
"""
from alembic import op
import sqlalchemy as sa

revision = '32c0a1110003'
down_revision = '32c0a1110002'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(sa.text("""
        INSERT INTO suscripciones (id_empresa, finanzas_habilitadas, estado, inicio_prueba, fin_prueba)
        SELECT id, false, 'Prueba', timezone('UTC', now()), timezone('UTC', now()) + interval '30 days'
        FROM empresas
        WHERE NOT EXISTS (SELECT 1 FROM suscripciones WHERE suscripciones.id_empresa = empresas.id)
    """))


def downgrade():
    # Conserva los planes: bajar una version no debe borrar suscripciones vigentes.
    pass
