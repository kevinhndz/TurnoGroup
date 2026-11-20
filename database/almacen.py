from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import create_engine
from core.config import revision as traer
from database.conexion import preparar_url_bd

# Uso la misma politica TLS en la aplicacion y en las migraciones.
UBICACION_ALMACEN = preparar_url_bd(traer.DATABASE_URL, traer.DATABASE_SSL_ROOT_CERT)


motor = create_engine(UBICACION_ALMACEN)
llaves = sessionmaker(bind=motor)


class miclaseBase(DeclarativeBase):
    pass


def abrir_puerta_bd():

    db = llaves()
    try:
        yield db
    finally:
        db.close()
