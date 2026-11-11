from core.listados import pagina_listado
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.Empresas.tabla import Empresas


class EmpresaRepository():


    @staticmethod
    def buscar_empresa(db: Session, nombre: str) -> Empresas | None:
        return db.query(Empresas).filter(Empresas.nombre == nombre).first()

    @staticmethod
    def guardar_nueva_empresa(db: Session, nueva_empresa: Empresas) -> Empresas:
        try:
            db.add(nueva_empresa)
            # Primero se guarda; refresh necesita un objeto ya persistido.
            db.commit()
            db.refresh(nueva_empresa)
        except SQLAlchemyError:
            # Una escritura fallida no debe dejar la sesión inutilizable.
            db.rollback()
            raise
        return nueva_empresa

    @staticmethod
    def listar_empresas(db: Session, pagina_actual: int, limite: int, id_empresa=None, filtros=None):
        consulta = db.query(Empresas)
        if id_empresa is not None:
            consulta = consulta.filter(Empresas.id == id_empresa)
        return pagina_listado(consulta, Empresas, pagina_actual, limite, filtros)

    @staticmethod
    def buscar_empresa_por_id(db: Session, id: int) -> Empresas | None:
        return db.query(Empresas).filter(Empresas.id == id).first()

    
