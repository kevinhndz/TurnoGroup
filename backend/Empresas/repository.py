from sqlalchemy.orm import Session

from backend.Empresas.tabla import Empresas
from core.listados import pagina_listado


class EmpresaRepository:
    @staticmethod
    def buscar_empresa(db: Session, nombre: str) -> Empresas | None:
        return db.query(Empresas).filter(Empresas.nombre == nombre).first()

    @staticmethod
    def guardar_nueva_empresa(db: Session, nueva_empresa: Empresas) -> Empresas:
        db.add(nueva_empresa)
        db.flush()

        return nueva_empresa

    @staticmethod
    def listar_empresas(
        db: Session, pagina_actual: int, limite: int, id_empresa=None, filtros=None
    ):
        consulta = db.query(Empresas)

        if id_empresa is not None:
            consulta = consulta.filter(Empresas.id == id_empresa)

        return pagina_listado(consulta, Empresas, pagina_actual, limite, filtros)

    @staticmethod
    def buscar_empresa_por_id(db: Session, id: int) -> Empresas | None:
        return db.query(Empresas).filter(Empresas.id == id).first()

    @staticmethod
    def agregar(db, registro):
        db.add(registro)

        return registro

    @staticmethod
    def guardar_cambios(db):
        db.flush()

    @staticmethod
    def actualizar(db, registro):
        db.refresh(registro)

        return registro
