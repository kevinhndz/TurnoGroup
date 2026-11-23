from sqlalchemy.orm import Session

from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
from backend.Productos.tabla import Productos
from backend.Sucursales.tabla import Sucursales
from core.listados import pagina_listado


class ProductoRepository:
    @staticmethod
    def guardar_nuevo_producto(db: Session, nuevo_producto: Productos) -> Productos:
        db.add(nuevo_producto)
        db.flush()

        return nuevo_producto

    @staticmethod
    def buscar_producto_por_nombre(
        db: Session, id_empresa: int, nombre: str
    ) -> Productos | None:
        return (
            db.query(Productos)
            .filter(Productos.id_empresa == id_empresa, Productos.nombre == nombre)
            .first()
        )

    @staticmethod
    def listar_productos(
        db: Session,
        id_empresa: int,
        pagina_actual: int,
        limite: int,
        id_sucursal=None,
        filtros=None,
    ):
        consulta = ProductoRepository.consulta_catalogo(db, id_empresa, id_sucursal)

        return pagina_listado(consulta, Productos, pagina_actual, limite, filtros)

    @staticmethod
    def buscar_producto_por_id(
        db: Session, id: int, id_empresa: int, id_sucursal=None
    ) -> Productos | None:
        return (
            ProductoRepository.consulta_catalogo(db, id_empresa, id_sucursal)
            .filter(Productos.id == id)
            .first()
        )

    @staticmethod
    def consulta_catalogo(db, id_empresa, id_sucursal=None):
        consulta = db.query(Productos).filter(Productos.id_empresa == id_empresa)

        if id_sucursal is not None:
            consulta = consulta.join(
                DisponibilidadProductos,
                DisponibilidadProductos.id_producto == Productos.id,
            ).filter(
                DisponibilidadProductos.id_sucursal == id_sucursal,
                DisponibilidadProductos.disponible.is_(True),
                Productos.disponible.is_(True),
            )

        return consulta

    @staticmethod
    def agregar_varios(db, registros):
        db.add_all(registros)

    @staticmethod
    def guardar_cambios(db):
        db.flush()

    @staticmethod
    def actualizar(db, registro):
        db.refresh(registro)

        return registro

    @staticmethod
    def listar_nombres_para_importacion(db, id_empresa):
        return (
            db.query(Productos.nombre).filter(Productos.id_empresa == id_empresa).all()
        )

    @staticmethod
    def buscar_sucursal_activa(db, id_sucursal, id_empresa):
        return (
            db.query(Sucursales)
            .filter(
                Sucursales.id == id_sucursal,
                Sucursales.id_empresa == id_empresa,
                Sucursales.activo.is_(True),
            )
            .first()
        )
