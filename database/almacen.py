from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import create_engine
from core.config import revision as traer

UBICACION_ALMACEN = traer.DATABASE_URL


motor = create_engine(UBICACION_ALMACEN)
llaves = sessionmaker(bind = motor)

class miclaseBase (DeclarativeBase):
    pass


def abrir_puerta_bd():

    db = llaves()
    try:
        yield db
    finally:
        db.close()


