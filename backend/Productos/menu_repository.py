from backend.Categorias.tabla import Categorias
from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
from backend.Empresas.tabla import Empresas
from backend.Productos.tabla import Productos


class MenuRepository:
    @staticmethod
    def empresa(db, id_empresa, bloquear=False):
        consulta = db.query(Empresas).filter(Empresas.id == id_empresa)
        if bloquear:
            consulta = consulta.with_for_update()
        return consulta.one()

    @staticmethod
    def productos(db, id_empresa):
        return db.query(Productos).filter(Productos.id_empresa == id_empresa).all()

    @staticmethod
    def categorias(db, id_empresa):
        return db.query(Categorias).filter(Categorias.id_empresa == id_empresa).all()

    @staticmethod
    def asignacion(db, id_producto, id_sucursal):
        return (
            db.query(DisponibilidadProductos)
            .filter_by(id_producto=id_producto, id_sucursal=id_sucursal)
            .first()
        )

    @staticmethod
    def agregar(db, registro):
        db.add(registro)
        db.flush()
        return registro
