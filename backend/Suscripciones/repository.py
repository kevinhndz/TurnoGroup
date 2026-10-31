from backend.Suscripciones.tabla import Suscripciones
from backend.Sucursales.tabla import Sucursales


class SuscripcionRepository:
    @staticmethod
    def buscar_suscripcion(db, id_empresa, bloquear=False):
        consulta = db.query(Suscripciones).filter(
            Suscripciones.id_empresa == id_empresa
        )
        return (consulta.with_for_update() if bloquear else consulta).first()

    @staticmethod
    def contar_sucursales(db, id_empresa):
        return (
            db.query(Sucursales)
            .filter(Sucursales.id_empresa == id_empresa, Sucursales.activo.is_(True))
            .count()
        )
