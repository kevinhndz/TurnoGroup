from sqlalchemy.orm import Session

from backend.Empresas.tabla import Empresas
from backend.MetodosPago.tabla import MetodosPago
from backend.TiposServicio.tabla import TiposServicio
from backend.Usuarios.cambios_correo import CambiosCorreo
from backend.Usuarios.codigos_mfa import CodigosRecuperacionMfa
from backend.Usuarios.tabla import Usuarios
from backend.Usuarios.verificaciones_correo import VerificacionesCorreo
from core.listados import pagina_listado
from utils.token import proteger_token_sesion


class UsuarioRepository:
    @staticmethod
    def buscar_usuario_por_correo(db: Session, correo: str) -> Usuarios | None:
        return db.query(Usuarios).filter(Usuarios.correo == correo).first()

    @staticmethod
    def guardar_nuevo_usuario(db: Session, nuevo_usuario: Usuarios) -> Usuarios:
        db.add(nuevo_usuario)
        db.flush()

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
        db.query(CambiosCorreo).filter(
            CambiosCorreo.id_usuario == id_usuario,
            CambiosCorreo.fecha_uso.is_(None),
        ).update({"fecha_uso": ahora}, synchronize_session="fetch")

    @staticmethod
    def reemplazar_codigos_mfa(db, id_usuario, hashes):
        db.query(CodigosRecuperacionMfa).filter_by(id_usuario=id_usuario).delete()
        elementos = []

        for valor_actual in hashes:
            elementos.append(
                CodigosRecuperacionMfa(
                    id_usuario=id_usuario, codigo_protegido=valor_actual
                )
            )
        db.add_all(elementos)

    @staticmethod
    def consumir_codigo_mfa(db, id_usuario, codigo_protegido, ahora):
        return (
            db.query(CodigosRecuperacionMfa)
            .filter(
                CodigosRecuperacionMfa.id_usuario == id_usuario,
                CodigosRecuperacionMfa.codigo_protegido == codigo_protegido,
                CodigosRecuperacionMfa.fecha_uso.is_(None),
            )
            .update({"fecha_uso": ahora}, synchronize_session="fetch")
        )

    @staticmethod
    def agregar(db, registro):
        db.add(registro)

        return registro

    @staticmethod
    def agregar_varios(db, registros):
        db.add_all(registros)

    @staticmethod
    def guardar_cambios(db):
        db.flush()

    @staticmethod
    def actualizar(db, registro):
        db.refresh(registro)

        return registro

    @staticmethod
    def buscar_usuario_para_cambio_correo(db, id_usuario):
        return (
            db.query(Usuarios)
            .filter(Usuarios.id == id_usuario)
            .with_for_update()
            .first()
        )

    @staticmethod
    def buscar_correo_nuevo(db, nuevo):
        return db.query(Usuarios.id).filter(Usuarios.correo == nuevo).first()

    @staticmethod
    def invalidar_cambios_pendientes(db, ahora, usuario):
        return (
            db.query(CambiosCorreo)
            .filter(
                CambiosCorreo.id_usuario == usuario.id,
                CambiosCorreo.fecha_uso.is_(None),
            )
            .update({"fecha_uso": ahora})
        )

    @staticmethod
    def buscar_cambio_correo_vigente(db, ahora, usuario, json):
        return (
            db.query(CambiosCorreo)
            .filter(
                CambiosCorreo.id_usuario == usuario.id,
                CambiosCorreo.codigo_protegido
                == proteger_token_sesion(json.codigo.get_secret_value()),
                CambiosCorreo.fecha_uso.is_(None),
                CambiosCorreo.vencimiento > ahora,
            )
            .first()
        )

    @staticmethod
    def listar_superadministradores_activos(db):
        return (
            db.query(Usuarios)
            .filter(
                Usuarios.rol_plataforma == "Superadministrador",
                Usuarios.estado.is_(True),
            )
            .order_by(Usuarios.id)
            .with_for_update()
            .all()
        )

    @staticmethod
    def buscar_id_por_correo(db, correo):
        return db.query(Usuarios.id).filter(Usuarios.correo == correo).first()

    @staticmethod
    def buscar_empresa_para_registro(db, json):
        return (
            db.query(Empresas.id).filter(Empresas.nombre == json.negocio.nombre).first()
        )

    @staticmethod
    def listar_tipos_servicio_activos(db):
        return db.query(TiposServicio).filter(TiposServicio.activo.is_(True)).all()

    @staticmethod
    def listar_metodos_pago_activos(db):
        return db.query(MetodosPago).filter(MetodosPago.activo.is_(True)).all()

    @staticmethod
    def buscar_id_para_verificacion(db, correo):
        return db.query(Usuarios.id).filter_by(correo=correo).first()

    @staticmethod
    def buscar_verificacion_por_codigo(db, json):
        return (
            db.query(VerificacionesCorreo)
            .filter_by(
                correo=str(json.correo).lower(),
                codigo_protegido=proteger_token_sesion(json.codigo.get_secret_value()),
            )
            .with_for_update()
            .first()
        )

    @staticmethod
    def buscar_verificacion_por_comprobante(db, comprobante, correo):
        return (
            db.query(VerificacionesCorreo)
            .filter_by(
                correo=str(correo).lower(),
                comprobante_protegido=proteger_token_sesion(comprobante),
            )
            .with_for_update()
            .first()
        )
