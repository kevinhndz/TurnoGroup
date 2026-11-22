"""Ejecutar cada minuto: python -m scripts.procesar_correos."""

from datetime import datetime
from sqlalchemy import select
from database.almacen import llaves
from backend.Correos.tabla import CorreosPendientes
from backend.Correos.service import procesar_correo


def main():
    with llaves() as db:
        ids = db.scalars(
            select(CorreosPendientes.id)
            .where(
                CorreosPendientes.estado == "pendiente",
                CorreosPendientes.proximo_intento <= datetime.utcnow(),
            )
            .order_by(CorreosPendientes.proximo_intento)
            .limit(100)
        ).all()
        db.rollback()
        for id in ids:
            procesar_correo(db, id)


if __name__ == "__main__":
    main()
