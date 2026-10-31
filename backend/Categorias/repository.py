from sqlalchemy.orm import Session
from backend.Categorias.tabla import Categorias


class CategoriaRepository():

    @staticmethod
    def buscar_categoria_por_nombre(db: Session, id_empresa: int, nombre: str) -> Categorias | None:
        return db.query(Categorias).filter(
            Categorias.id_empresa == id_empresa,
            Categorias.nombre == nombre,
        ).first()

    @staticmethod
    def guardar_nueva_categoria(db: Session, nueva_categoria: Categorias) -> Categorias:
        db.add(nueva_categoria)
        db.commit()
        db.refresh(nueva_categoria)
        return nueva_categoria

    @staticmethod
    def listar_categorias(db: Session, id_empresa: int, pagina_actual: int, limite: int, id_sucursal=None):
        consulta = CategoriaRepository.consulta_catalogo(db, id_empresa, id_sucursal)
        salto = (pagina_actual - 1) * limite
        return consulta.count(), consulta.order_by(Categorias.id).offset(salto).limit(limite).all()

    @staticmethod
    def buscar_categoria_por_id(db: Session, id: int, id_empresa: int, id_sucursal=None) -> Categorias | None:
        return CategoriaRepository.consulta_catalogo(db, id_empresa, id_sucursal).filter(Categorias.id == id).first()

    @staticmethod
    def consulta_catalogo(db, id_empresa, id_sucursal=None):
        from backend.DisponibilidadProductos.tabla import DisponibilidadProductos
        from backend.Productos.tabla import Productos
        consulta = db.query(Categorias).filter(Categorias.id_empresa == id_empresa)
        if id_sucursal is not None:
            categorias = db.query(Productos.id_categoria).join(
                DisponibilidadProductos, DisponibilidadProductos.id_producto == Productos.id
            ).filter(Productos.id_empresa == id_empresa, Productos.disponible.is_(True),
                     DisponibilidadProductos.id_sucursal == id_sucursal, DisponibilidadProductos.disponible.is_(True))
            consulta = consulta.filter(Categorias.id.in_(categorias), Categorias.activo.is_(True))
        return consulta
