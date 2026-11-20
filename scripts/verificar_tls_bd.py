"""Comprueba la confianza TLS y el cifrado del tramo final en PostgreSQL."""

import sys

from sqlalchemy import create_engine, text

from core.config import revision
from database.conexion import preparar_url_bd


def main() -> int:
    url = preparar_url_bd(revision.DATABASE_URL, revision.DATABASE_SSL_ROOT_CERT)
    if url.get_backend_name() != "postgresql":
        print("La base configurada no es PostgreSQL", file=sys.stderr)
        return 1

    # El motor valida el certificado y el nombre antes de abrir la sesion.
    motor = create_engine(url, connect_args={"connect_timeout": 5})
    try:
        with motor.connect() as conexion:
            cifrado = conexion.execute(
                text("SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()")
            ).scalar_one()
        if not cifrado:
            print("El tramo hacia PostgreSQL no usa TLS", file=sys.stderr)
            return 1
        print("TLS verificado en la conexion y en PostgreSQL")
        return 0
    except Exception as error:
        # No imprimo la URL ni la excepcion: pueden incluir credenciales.
        print(f"No se pudo verificar TLS ({type(error).__name__})", file=sys.stderr)
        return 1
    finally:
        motor.dispose()


if __name__ == "__main__":
    sys.exit(main())
