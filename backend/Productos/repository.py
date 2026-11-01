from core.listados import pagina_listado
from sqlalchemy.orm import Session
from backend.Productos.tabla import Productos


class ProductoRepository():

    @staticmethod
    def guardar_nuevo_producto(db: Session, nuevo_producto: Productos) -> Productos:
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)
        return nuevo_producto

    @staticmethod
    def buscar_producto_por_nombre(db: Session, id_empresa: int, nombre: str) -> Productos | None:
        return db.query(Productos).filter(
            Productos.id_empresa == id_empresa,
            Productos.nombre == nombre
        ).first()

    @staticmethod
    def listar_productos(db: Session, id_empresa: int, pagina_actual: int, limite: int, id_sucursal=None, filtros=None):
        consulta = ProductoRepository.consulta_catalogo(db, id_empresa, id_sucursal)
        return pagina_listado(consulta, Productos, pagina_actual, limite, filtros)

    @staticmethod
    def buscar_producto_por_id(db: Session, id: int, id_empresa: int, id_sucursal=None) -> Productos | None:
        return ProductoRepository.consulta_catalogo(db, id_empresa, id_sucursal).filter(Productos.id == id).first()

    @staticmethod
    def consulta_catalogo(db, id_empresa, id_sucursal=None):
        from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
        from backend.Productos.tabla import Productos
        consulta = db.query(Productos).filter(Productos.id_empresa == id_empresa)
        if id_sucursal is not None:
            consulta = consulta.join(DisponibilidadProductos, DisponibilidadProductos.id_producto == Productos.id).filter(
                DisponibilidadProductos.id_sucursal == id_sucursal,
                DisponibilidadProductos.disponible.is_(True), Productos.disponible.is_(True)
            )
        return consulta
