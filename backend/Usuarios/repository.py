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
    def listar_usuarios(db: Session, pagina_actual: int, limite: int):
        salto = (pagina_actual - 1) * limite
        total = db.query(Usuarios).count()
        lista_usuarios = db.query(Usuarios).order_by(Usuarios.id).offset(salto).limit(limite).all()
        return total, lista_usuarios

    @staticmethod
    def buscar_usuario_por_id(db: Session, id: int) -> Usuarios | None:
        return db.query(Usuarios).filter(Usuarios.id == id).first()
