"""Separa las credenciales de migracion de las de uso diario, sin imprimirlas."""

import os
from pathlib import Path
from secrets import token_urlsafe
from sqlalchemy import create_engine, text
from psycopg import sql
from dotenv import dotenv_values, set_key
from database.conexion import preparar_url_bd


def main():
    raiz = Path(__file__).resolve().parents[1]
    archivo = raiz / ".env"
    migraciones = raiz / ".env.migraciones"
    if migraciones.exists():
        raise SystemExit("Ya existe .env.migraciones; no se reemplazaron credenciales")
    valores = dotenv_values(archivo)
    url = preparar_url_bd(
        valores["DATABASE_URL"], valores.get("DATABASE_SSL_ROOT_CERT", "")
    )
    if url.get_backend_name() != "postgresql":
        raise SystemExit("Esta operacion requiere PostgreSQL")
    motor = create_engine(url, connect_args={"connect_timeout": 10})
    clave = token_urlsafe(48)
    nombre = "turnogroup_app"
    with motor.begin() as conexion:
        existe = conexion.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname=:rol"), {"rol": nombre}
        ).scalar()
        if existe:
            raise SystemExit("El rol ya existe; no se cambio su contrasena")
        # La sentencia compuesta cita identificadores y contrasena correctamente.
        dbapi = conexion.connection.driver_connection
        with dbapi.cursor() as cursor:
            cursor.execute(
                sql.SQL(
                    "CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT"
                ).format(sql.Identifier(nombre), sql.Literal(clave))
            )
            cursor.execute(
                sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                    sql.Identifier(url.database), sql.Identifier(nombre)
                )
            )
            cursor.execute(
                sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(
                    sql.Identifier(nombre)
                )
            )
            cursor.execute(
                sql.SQL(
                    "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {}"
                ).format(sql.Identifier(nombre))
            )
            cursor.execute(
                sql.SQL(
                    "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {}"
                ).format(sql.Identifier(nombre))
            )
            cursor.execute(
                sql.SQL("REVOKE ALL ON TABLE public.alembic_version FROM {}").format(
                    sql.Identifier(nombre)
                )
            )
            cursor.execute(
                sql.SQL(
                    "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {}"
                ).format(sql.Identifier(nombre))
            )
            cursor.execute(
                sql.SQL(
                    "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO {}"
                ).format(sql.Identifier(nombre))
            )
    usuario = nombre
    if "." in (url.username or ""):
        usuario += "." + url.username.split(".", 1)[1]
    destino = url.set(username=usuario, password=clave)
    comprobacion = create_engine(destino, connect_args={"connect_timeout": 10})
    with comprobacion.connect() as conexion:
        fila = conexion.execute(
            text(
                "SELECT rolsuper, rolcreatedb, rolcreaterole, rolbypassrls FROM pg_roles WHERE rolname=current_user"
            )
        ).one()
        if any(fila):
            raise SystemExit(
                "El rol conserva privilegios elevados; no se modifico .env"
            )
        conexion.execute(text("SELECT id FROM public.usuarios LIMIT 1"))
    descriptor = os.open(migraciones, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as salida:
        salida.write(archivo.read_text())
    os.chmod(archivo, 0o600)
    set_key(str(archivo), "DATABASE_URL", destino.render_as_string(hide_password=False))
    print(
        "Usuario de aplicacion separado y conexion comprobada. Credenciales anteriores en .env.migraciones (0600)."
    )
    print(
        "Migraciones: TURNO_ENV=.env.migraciones ./venv/bin/python -m alembic upgrade head"
    )


if __name__ == "__main__":
    main()
