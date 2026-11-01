from backend.Suscripciones.tabla import Suscripciones, TarjetasSuscripcion, ComprobantesSuscripcion
from backend.Sucursales.tabla import Sucursales


class SuscripcionRepository:
    @staticmethod
    def tarjetas(db, id_empresa):
        return db.query(TarjetasSuscripcion).filter_by(id_empresa=id_empresa, activo=True).order_by(TarjetasSuscripcion.id).all()

    @staticmethod
    def buscar_tarjeta(db, id_empresa, id):
        return db.query(TarjetasSuscripcion).filter_by(id=id, id_empresa=id_empresa, activo=True).first()

    @staticmethod
    def comprobantes(db, id_empresa):
        return db.query(ComprobantesSuscripcion).filter_by(id_empresa=id_empresa).order_by(ComprobantesSuscripcion.fecha.desc(), ComprobantesSuscripcion.id.desc()).all()

    @staticmethod
    def buscar_comprobante(db, id_empresa, id):
        return db.query(ComprobantesSuscripcion).filter_by(id=id, id_empresa=id_empresa).first()

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
