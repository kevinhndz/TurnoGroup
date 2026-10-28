from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.Empresas.tabla import Empresas
from backend.Empresas.schema import Revisar_Json_Nueva_Empresa


class EmpresaRepository():


    @staticmethod
    def buscar_empresa(db: Session, json: Revisar_Json_Nueva_Empresa) -> Empresas | None:
        return db.query(Empresas).filter(Empresas.nombre == json.nombre).first()

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
    def listar_empresas(db: Session, pagina_actual: int, limite: int):
        salto = (pagina_actual - 1) * limite
        total = db.query(Empresas).count()
        lista_empresas = db.query(Empresas).offset(salto).limit(limite).all()
        return total, lista_empresas

    
