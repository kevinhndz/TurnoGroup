from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import create_engine, event
from core.config import revision as traer
from database.conexion import preparar_url_bd

# Uso la misma politica TLS en la aplicacion y en las migraciones.
UBICACION_ALMACEN = preparar_url_bd(traer.DATABASE_URL, traer.DATABASE_SSL_ROOT_CERT)


opciones = {"pool_pre_ping": True}
if UBICACION_ALMACEN.get_backend_name() == "postgresql":
    opciones["connect_args"] = {"connect_timeout": 10}
motor = create_engine(UBICACION_ALMACEN, **opciones)


@event.listens_for(motor, "connect")
def revisar_usuario_produccion(conexion, registro):
    if traer.ENTORNO != "produccion":
        return
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT rolsuper, rolcreatedb, rolcreaterole, rolbypassrls FROM pg_roles WHERE rolname=current_user"
        )
        if any(cursor.fetchone()):
            raise RuntimeError(
                "Produccion requiere un usuario PostgreSQL sin privilegios de administracion"
            )
        cursor.execute("SELECT has_schema_privilege(current_user, 'public', 'CREATE')")
        if cursor.fetchone()[0]:
            raise RuntimeError("El usuario de aplicacion no debe crear tablas")
    conexion.rollback()


llaves = sessionmaker(bind=motor)


class miclaseBase(DeclarativeBase):
    pass


def abrir_puerta_bd():

    db = llaves()
    try:
        yield db
    finally:
        db.close()
