from core.listados import pagina_listado
from sqlalchemy.orm import Session
from backend.Usuarios.tabla import Usuarios


class UsuarioRepository():

    @staticmethod
    def buscar_usuario_por_correo(db: Session, correo: str) -> Usuarios | None:
        return db.query(Usuarios).filter(Usuarios.correo == correo).first()

    @staticmethod
    def guardar_nuevo_usuario(db: Session, nuevo_usuario: Usuarios) -> Usuarios:
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario

    @staticmethod
    def listar_usuarios(db: Session, pagina_actual: int, limite: int, filtros=None):
        consulta = db.query(Usuarios)
        return pagina_listado(consulta, Usuarios, pagina_actual, limite, filtros)

    @staticmethod
    def buscar_usuario_por_id(db: Session, id: int) -> Usuarios | None:
        return db.query(Usuarios).filter(Usuarios.id == id).first()
