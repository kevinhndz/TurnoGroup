from backend.Pedidos.tabla import Pedidos
from backend.Empresas.tabla import Empresas


class FinanzasRepository:
    @staticmethod
    def totales_periodos(db, id_empresa, id_sucursal, periodos):
        from sqlalchemy import case, and_, func
        columnas = [func.coalesce(func.sum(case((and_(Pedidos.fecha_pago >= inicio, Pedidos.fecha_pago < fin), Pedidos.total), else_=0)), 0).label(clave) for clave, (inicio, fin) in periodos.items()]
        consulta = db.query(*columnas).filter(Pedidos.id_empresa == id_empresa, Pedidos.estado != "Cancelado", Pedidos.fecha_pago.is_not(None))
        if id_sucursal:
            consulta = consulta.filter(Pedidos.id_sucursal == id_sucursal)
        return dict(consulta.one()._mapping)

    @staticmethod
    def detalles_ventas(db, id_empresa, inicio, fin, id_sucursal):
        from backend.Pedidos.tabla import DetallesPedidos
        from backend.Productos.tabla import Productos
        from backend.Categorias.tabla import Categorias
        consulta = db.query(DetallesPedidos, Categorias.nombre).join(Pedidos, Pedidos.id == DetallesPedidos.id_pedido).join(Productos, Productos.id == DetallesPedidos.id_producto).outerjoin(Categorias, Categorias.id == Productos.id_categoria).filter(Pedidos.id_empresa == id_empresa, Productos.id_empresa == id_empresa, Pedidos.fecha_pago >= inicio, Pedidos.fecha_pago < fin, Pedidos.estado != "Cancelado")
        if id_sucursal:
            consulta = consulta.filter(Pedidos.id_sucursal == id_sucursal)
        return consulta.order_by(DetallesPedidos.id).all()

    @staticmethod
    def sucursales(db, id_empresa):
        from backend.Sucursales.tabla import Sucursales
        return db.query(Sucursales).filter(Sucursales.id_empresa == id_empresa).all()

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
