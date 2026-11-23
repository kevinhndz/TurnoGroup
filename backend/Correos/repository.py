from sqlalchemy import select

from backend.Correos.tabla import CorreosPendientes


class CorreoRepository:
    @staticmethod
    def agregar(db, registro):
        db.add(registro)

        return registro

    @staticmethod
    def guardar_cambios(db):
        db.flush()

    @staticmethod
    def buscar_mensaje_pendiente(db, id):
        return db.execute(
            select(CorreosPendientes)
            .where(CorreosPendientes.id == id, CorreosPendientes.estado == "pendiente")
            .with_for_update(skip_locked=True)
        ).scalar_one_or_none()
