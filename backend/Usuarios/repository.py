from core.listados import pagina_listado
from sqlalchemy.orm import Session
from backend.Usuarios.tabla import Usuarios


class UsuarioRepository:

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

    @staticmethod
    def invalidar_cambios_correo(db, id_usuario, ahora):
        from backend.Usuarios.cambios_correo import CambiosCorreo

        db.query(CambiosCorreo).filter(
            CambiosCorreo.id_usuario == id_usuario,
            CambiosCorreo.fecha_uso.is_(None),
        ).update({"fecha_uso": ahora}, synchronize_session="fetch")

    @staticmethod
    def reemplazar_codigos_mfa(db, id_usuario, hashes):
        from backend.Usuarios.codigos_mfa import CodigosRecuperacionMfa

        db.query(CodigosRecuperacionMfa).filter_by(id_usuario=id_usuario).delete()
        db.add_all(
            [
                CodigosRecuperacionMfa(id_usuario=id_usuario, codigo_protegido=valor)
                for valor in hashes
            ]
        )

    @staticmethod
    def consumir_codigo_mfa(db, id_usuario, codigo_protegido, ahora):
        from backend.Usuarios.codigos_mfa import CodigosRecuperacionMfa

        return (
            db.query(CodigosRecuperacionMfa)
            .filter(
                CodigosRecuperacionMfa.id_usuario == id_usuario,
                CodigosRecuperacionMfa.codigo_protegido == codigo_protegido,
                CodigosRecuperacionMfa.fecha_uso.is_(None),
            )
            .update({"fecha_uso": ahora}, synchronize_session="fetch")
        )
