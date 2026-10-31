from backend.RecuperacionesClave.tabla import RecuperacionesClave
from backend.Usuarios.tabla import Usuarios


class RecuperacionClaveRepository():

    @staticmethod
    def buscar_usuario_para_recuperacion(db, correo):
        return db.query(Usuarios).filter(Usuarios.correo == correo).with_for_update().first()

    @staticmethod
    def buscar_usuario_por_id(db, id_usuario):
        return db.query(Usuarios).filter(Usuarios.id == id_usuario).with_for_update().first()

    @staticmethod
    def buscar_recuperacion(db, codigo_protegido, ahora):
        return db.query(RecuperacionesClave).filter(
            RecuperacionesClave.codigo_protegido == codigo_protegido,
            RecuperacionesClave.fecha_uso.is_(None),
            RecuperacionesClave.vencimiento > ahora
        ).first()

    @staticmethod
    def invalidar_codigos(db, id_usuario, ahora):
        db.query(RecuperacionesClave).filter(
            RecuperacionesClave.id_usuario == id_usuario,
            RecuperacionesClave.fecha_uso.is_(None)
        ).update({"fecha_uso": ahora}, synchronize_session="fetch")

    @staticmethod
    def guardar_recuperacion(db, recuperacion):
        db.add(recuperacion)
        db.commit()
