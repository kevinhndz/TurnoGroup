from sqlalchemy.orm import Session
from backend.CategoriasGastos.tabla import CategoriasGastos


class CategoriaGastoRepository():

    @staticmethod
    def buscar_categoria_gasto_por_nombre(db: Session, id_empresa: int, nombre: str) -> CategoriasGastos | None:
        return db.query(CategoriasGastos).filter(
            CategoriasGastos.id_empresa == id_empresa,
            CategoriasGastos.nombre == nombre
        ).first()

    @staticmethod
    def guardar_nueva_categoria_gasto(db: Session, nueva_categoria_gasto: CategoriasGastos) -> CategoriasGastos:
        db.add(nueva_categoria_gasto)
        db.commit()
        db.refresh(nueva_categoria_gasto)
        return nueva_categoria_gasto

    @staticmethod
    def listar_categorias_gastos(db: Session, id_empresa: int, pagina_actual: int, limite: int):
        salto = (pagina_actual - 1) * limite
        total = db.query(CategoriasGastos).filter(CategoriasGastos.id_empresa == id_empresa).count()
        lista_categorias_gastos = db.query(CategoriasGastos).filter(
            CategoriasGastos.id_empresa == id_empresa
        ).order_by(CategoriasGastos.id).offset(salto).limit(limite).all()
        return total, lista_categorias_gastos

    @staticmethod
    def buscar_categoria_gasto_por_id(db: Session, id: int, id_empresa: int) -> CategoriasGastos | None:
        return db.query(CategoriasGastos).filter(
            CategoriasGastos.id == id,
            CategoriasGastos.id_empresa == id_empresa
        ).first()
