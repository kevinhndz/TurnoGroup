from backend.Pedidos.tabla import Pedidos
from backend.Empresas.tabla import Empresas


class FinanzasRepository:
    @staticmethod
    def empresa(db, id_empresa):
        return db.get(Empresas, id_empresa)

    @staticmethod
    def ventas(db, id_empresa, inicio, fin, id_sucursal):
        consulta = db.query(Pedidos).filter(
            Pedidos.id_empresa == id_empresa,
            Pedidos.fecha_pago >= inicio,
            Pedidos.fecha_pago < fin,
            Pedidos.estado != "Cancelado",
        )
        if id_sucursal:
            consulta = consulta.filter(Pedidos.id_sucursal == id_sucursal)
        return consulta.order_by(Pedidos.fecha_pago).all()
