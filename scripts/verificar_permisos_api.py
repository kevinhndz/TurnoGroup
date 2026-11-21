"""Busca permisos de Data API que expongan tablas de TurnoGroup."""

from sqlalchemy import create_engine, text

from core.config import revision
from database.conexion import preparar_url_bd

CONSULTA_TABLAS = text("""
    SELECT rol.rolname, tabla.relname,
           has_table_privilege(rol.oid, tabla.oid, 'SELECT') AS lectura,
           has_table_privilege(rol.oid, tabla.oid, 'INSERT') AS insercion,
           has_table_privilege(rol.oid, tabla.oid, 'UPDATE') AS edicion,
           has_table_privilege(rol.oid, tabla.oid, 'DELETE') AS borrado
    FROM pg_roles AS rol
    CROSS JOIN pg_class AS tabla
    JOIN pg_namespace AS esquema ON esquema.oid = tabla.relnamespace
    WHERE rol.rolname IN ('anon', 'authenticated', 'service_role')
      AND esquema.nspname = 'public'
      AND tabla.relkind IN ('r', 'p', 'v', 'm')
    ORDER BY rol.rolname, tabla.relname
    """)

CONSULTA_SECUENCIAS = text("""
    SELECT rol.rolname, secuencia.relname,
           has_sequence_privilege(rol.oid, secuencia.oid, 'USAGE') AS uso,
           has_sequence_privilege(rol.oid, secuencia.oid, 'SELECT') AS lectura,
           has_sequence_privilege(rol.oid, secuencia.oid, 'UPDATE') AS edicion
    FROM pg_roles AS rol
    CROSS JOIN pg_class AS secuencia
    JOIN pg_namespace AS esquema ON esquema.oid = secuencia.relnamespace
    WHERE rol.rolname IN ('anon', 'authenticated', 'service_role')
      AND esquema.nspname = 'public' AND secuencia.relkind = 'S'
    ORDER BY rol.rolname, secuencia.relname
    """)

CONSULTA_FUNCIONES = text("""
    SELECT rol.rolname, funcion.proname,
           has_function_privilege(rol.oid, funcion.oid, 'EXECUTE') AS ejecucion
    FROM pg_roles AS rol
    CROSS JOIN pg_proc AS funcion
    JOIN pg_namespace AS esquema ON esquema.oid = funcion.pronamespace
    WHERE rol.rolname IN ('anon', 'authenticated', 'service_role')
      AND esquema.nspname = 'public'
    ORDER BY rol.rolname, funcion.proname
    """)


def main() -> int:
    url = preparar_url_bd(revision.DATABASE_URL, revision.DATABASE_SSL_ROOT_CERT)
    if url.get_backend_name() != "postgresql":
        print("Esta comprobacion requiere PostgreSQL")
        return 1
    motor = create_engine(url, connect_args={"connect_timeout": 5})
    try:
        with motor.connect() as conexion:
            filas = conexion.execute(CONSULTA_TABLAS).all()
            secuencias = conexion.execute(CONSULTA_SECUENCIAS).all()
            funciones = conexion.execute(CONSULTA_FUNCIONES).all()
        expuestas = [
            (fila.rolname, fila.relname)
            for fila in filas
            if any((fila.lectura, fila.insercion, fila.edicion, fila.borrado))
        ]
        expuestas += [
            (fila.rolname, fila.relname)
            for fila in secuencias
            if any((fila.uso, fila.lectura, fila.edicion))
        ]
        expuestas += [
            (fila.rolname, fila.proname) for fila in funciones if fila.ejecucion
        ]
        if expuestas:
            for rol, objeto in expuestas:
                print(f"Permiso de Data API: {rol} puede usar public.{objeto}")
            return 1
        print(
            f"Sin permisos de Data API en {len(filas) + len(secuencias) + len(funciones)} objetos revisados"
        )
        return 0
    except Exception as error:
        # No imprimo la URL ni la excepcion porque pueden incluir la clave.
        print(f"No se pudo revisar PostgreSQL ({type(error).__name__})")
        return 1
    finally:
        motor.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
