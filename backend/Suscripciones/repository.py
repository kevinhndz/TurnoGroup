from backend.Empresas.tabla import Empresas
from backend.Sucursales.tabla import Sucursales
from backend.Suscripciones.tabla import (
    ComprobantesSuscripcion,
    Suscripciones,
    TarjetasSuscripcion,
)
from backend.Usuarios.tabla import Usuarios
from backend.VinculosLaborales.tabla import VinculosLaborales


class SuscripcionRepository:
    @staticmethod
    def tarjetas(db, id_empresa):
        return (
            db.query(TarjetasSuscripcion)
            .filter_by(id_empresa=id_empresa, activo=True)
            .order_by(TarjetasSuscripcion.id)
            .all()
        )

    @staticmethod
    def buscar_tarjeta(db, id_empresa, id):
        return (
            db.query(TarjetasSuscripcion)
            .filter_by(id=id, id_empresa=id_empresa, activo=True)
            .first()
        )

    @staticmethod
    def comprobantes(db, id_empresa):
        return (
            db.query(ComprobantesSuscripcion)
            .filter_by(id_empresa=id_empresa)
            .order_by(
                ComprobantesSuscripcion.fecha.desc(), ComprobantesSuscripcion.id.desc()
            )
            .all()
        )

    @staticmethod
    def buscar_comprobante(db, id_empresa, id):
        return (
            db.query(ComprobantesSuscripcion)
            .filter_by(id=id, id_empresa=id_empresa)
            .first()
        )

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

    @staticmethod
    def agregar(db, registro):
        db.add(registro)

        return registro

    @staticmethod
    def guardar_cambios(db):
        db.flush()

    @staticmethod
    def buscar_usuario_para_desactivar(db, contexto):
        return (
            db.query(Usuarios)
            .filter_by(id=contexto["usuario"].id)
            .with_for_update()
            .one()
        )

    @staticmethod
    def listar_empresas_del_gerente(db, usuario):
        return (
            db.query(VinculosLaborales)
            .filter_by(id_usuario=usuario.id, rol="Gerente", activo=True)
            .all()
        )

    @staticmethod
    def buscar_empresa(db, id_empresa):
        return db.get(Empresas, id_empresa)
