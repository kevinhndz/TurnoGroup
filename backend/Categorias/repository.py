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
    def listar_categorias(db: Session, id_empresa: int, pagina_actual: int, limite: int):
        salto = (pagina_actual - 1) * limite
        total = db.query(Categorias).filter(
            Categorias.id_empresa == id_empresa,
        ).count()
        lista_categorias = db.query(Categorias).filter(
            Categorias.id_empresa == id_empresa,
        ).order_by(Categorias.id).offset(salto).limit(limite).all()
        return total, lista_categorias

    @staticmethod
    def buscar_categoria_por_id(db: Session, id: int, id_empresa: int) -> Categorias | None:
        return db.query(Categorias).filter(
            Categorias.id == id,
            Categorias.id_empresa == id_empresa,
        ).first()
