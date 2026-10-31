from backend.Reservas.tabla import Reservas
from backend.Mesas.tabla import Mesas
from backend.ServiciosSucursales.tabla import ServiciosSucursales
from backend.TiposServicio.tabla import TiposServicio


class ReservaRepository:
    @staticmethod
    def habilitado(db, id_sucursal):
        return (
            db.query(ServiciosSucursales)
            .join(
                TiposServicio, TiposServicio.id == ServiciosSucursales.id_tipo_servicio
            )
            .filter(
                ServiciosSucursales.id_sucursal == id_sucursal,
                ServiciosSucursales.habilitado.is_(True),
                ServiciosSucursales.mesas_habilitadas.is_(True),
                ServiciosSucursales.reservas_habilitadas.is_(True),
                TiposServicio.clave_concepto == "comer_aqui",
            )
            .first()
        )

    @staticmethod
    def mesa(db, id, id_sucursal):
        return (
            db.query(Mesas)
            .filter(
                Mesas.id == id, Mesas.id_sucursal == id_sucursal, Mesas.activo.is_(True)
            )
            .with_for_update()
            .first()
        )

    @staticmethod
    def cruces(db, id_mesa, inicio, fin, excluir=None):
        consulta = db.query(Reservas.id).filter(
            Reservas.id_mesa == id_mesa,
            Reservas.estado == "Confirmada",
            Reservas.inicio < fin,
            Reservas.fin > inicio,
        )
        if excluir:
            consulta = consulta.filter(Reservas.id != excluir)
        return consulta.first()

    @staticmethod
    def buscar(db, id, id_empresa, id_sucursal):
        return (
            db.query(Reservas)
            .filter(
                Reservas.id == id,
                Reservas.id_empresa == id_empresa,
                Reservas.id_sucursal == id_sucursal,
            )
            .with_for_update()
            .first()
        )

    @staticmethod
    def listar(db, id_empresa, id_sucursal, estado):
        consulta = db.query(Reservas).filter(
            Reservas.id_empresa == id_empresa, Reservas.id_sucursal == id_sucursal
        )
        if estado:
            consulta = consulta.filter(Reservas.estado == estado)
        return consulta.order_by(Reservas.inicio.desc(), Reservas.id.desc())
