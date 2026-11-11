from backend.Cajas.tabla import Cajas
from backend.Pedidos.tabla import Pedidos
from backend.MetodosPago.tabla import MetodosPago
from backend.Sucursales.tabla import Sucursales


class CajaRepository:
    @staticmethod
    def bloquear_sucursal(db, id_empresa, id_sucursal):
        return (
            db.query(Sucursales)
            .filter(
                Sucursales.id == id_sucursal,
                Sucursales.id_empresa == id_empresa,
                Sucursales.activo.is_(True),
            )
            .with_for_update()
            .first()
        )

    @staticmethod
    def buscar_abierta(db, id_empresa, id_sucursal):
        return (
            db.query(Cajas)
            .filter(
                Cajas.id_empresa == id_empresa,
                Cajas.id_sucursal == id_sucursal,
                Cajas.fecha_cierre.is_(None),
            )
            .with_for_update()
            .first()
        )

    @staticmethod
    def buscar_caja(db, id, id_empresa, id_sucursal):
        return (
            db.query(Cajas)
            .filter(
                Cajas.id == id,
                Cajas.id_empresa == id_empresa,
                Cajas.id_sucursal == id_sucursal,
            )
            .with_for_update()
            .first()
        )

    @staticmethod
    def listar(db, id_empresa, id_sucursal):
        return (
            db.query(Cajas)
            .filter(Cajas.id_empresa == id_empresa, Cajas.id_sucursal == id_sucursal)
            .order_by(Cajas.id.desc())
        )

    @staticmethod
    def pagos(db, id_caja):
        return (
            db.query(Pedidos, MetodosPago.clave_concepto)
            .join(MetodosPago, MetodosPago.id == Pedidos.id_metodo_pago)
            .filter(
                Pedidos.id_caja == id_caja,
                Pedidos.fecha_pago.is_not(None),
                Pedidos.estado != "Cancelado",
            )
            .all()
        )
