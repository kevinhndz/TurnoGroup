"""cerrar permisos de la data api

Revision ID: c4a0e4010001
Revises: e7a5fb60330d
"""

from alembic import op

revision = "c4a0e4010001"
down_revision = "e7a5fb60330d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Quito los permisos que exponen las tablas aunque la API siga encendida.
    # La aplicacion entra con su usuario PostgreSQL, no con estos roles de API.
    op.execute("""
        DO $$
        DECLARE nombre_rol text;
        BEGIN
            FOREACH nombre_rol IN ARRAY ARRAY['anon', 'authenticated', 'service_role']
            LOOP
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = nombre_rol) THEN
                    EXECUTE format(
                        'REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM %I',
                        nombre_rol
                    );
                    EXECUTE format(
                        'REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM %I',
                        nombre_rol
                    );
                    EXECUTE format(
                        'ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM %I',
                        nombre_rol
                    );
                    EXECUTE format(
                        'ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM %I',
                        nombre_rol
                    );
                    EXECUTE format(
                        'ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON FUNCTIONS FROM %I',
                        nombre_rol
                    );
                END IF;
            END LOOP;
            -- Quito tambien el EXECUTE global que PostgreSQL da a PUBLIC.
            EXECUTE 'ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC';
        END $$;
        """)


def downgrade() -> None:
    # No restauro permisos amplios al retroceder: volverian a exponer datos.
    pass
