from backend.InvitacionesLaborales.tabla import InvitacionesLaborales, SucursalesInvitacion
from backend.VinculosLaborales.tabla import VinculosLaborales, AsignacionesSucursales
from backend.Empresas.tabla import Empresas
from backend.Sucursales.tabla import Sucursales
from backend.Usuarios.tabla import Usuarios


class InvitacionLaboralRepository():

    @staticmethod
    def bloquear_empresa(db, id_empresa):
        return db.query(Empresas).filter(Empresas.id == id_empresa).with_for_update().first()

    @staticmethod
    def buscar_invitacion(db, id, id_empresa):
        return db.query(InvitacionesLaborales).filter(
            InvitacionesLaborales.id == id, InvitacionesLaborales.id_empresa == id_empresa
        ).first()

    @staticmethod
    def buscar_por_codigo(db, codigo_protegido):
        return db.query(InvitacionesLaborales).filter(
            InvitacionesLaborales.codigo_protegido == codigo_protegido
        ).first()

    @staticmethod
    def listar_invitaciones(db, id_empresa, pagina_actual, limite):
        consulta = db.query(InvitacionesLaborales).filter(InvitacionesLaborales.id_empresa == id_empresa)
        return consulta.count(), consulta.order_by(InvitacionesLaborales.id).offset((pagina_actual - 1) * limite).limit(limite).all()

    @staticmethod
    def sucursales_invitacion(db, id):
        return [fila.id_sucursal for fila in db.query(SucursalesInvitacion).filter(SucursalesInvitacion.id_invitacion == id).all()]

    @staticmethod
    def buscar_sucursal(db, id, id_empresa):
        return db.query(Sucursales).filter(
            Sucursales.id == id, Sucursales.id_empresa == id_empresa, Sucursales.activo.is_(True)
        ).first()

    @staticmethod
    def buscar_vinculo(db, id_usuario, id_empresa):
        return db.query(VinculosLaborales).filter(
            VinculosLaborales.id_usuario == id_usuario, VinculosLaborales.id_empresa == id_empresa
        ).first()

    @staticmethod
    def buscar_usuario(db, correo):
        return db.query(Usuarios).filter(Usuarios.correo == correo).first()

    @staticmethod
    def buscar_otra_empresa(db, id_usuario, id_empresa=None):
        db.query(Usuarios).filter(Usuarios.id == id_usuario).with_for_update().first()
        consulta = db.query(VinculosLaborales).filter(VinculosLaborales.id_usuario == id_usuario)
        if id_empresa is not None:
            consulta = consulta.filter(VinculosLaborales.id_empresa != id_empresa)
        return consulta.first()

    @staticmethod
    def revocar_anteriores(db, correo, id_empresa, ahora):
        db.query(InvitacionesLaborales).filter(
            InvitacionesLaborales.correo == correo, InvitacionesLaborales.id_empresa == id_empresa,
            InvitacionesLaborales.fecha_aceptacion.is_(None), InvitacionesLaborales.fecha_revocacion.is_(None)
        ).update({"fecha_revocacion": ahora}, synchronize_session="fetch")

    @staticmethod
    def reemplazar_asignaciones(db, id_vinculo, sucursales):
        db.query(AsignacionesSucursales).filter(AsignacionesSucursales.id_vinculo_laboral == id_vinculo).delete(synchronize_session="fetch")
        for id_sucursal in sucursales:
            db.add(AsignacionesSucursales(id_vinculo_laboral=id_vinculo, id_sucursal=id_sucursal))

    @staticmethod
    def buscar_invitante_activo(db, id_usuario, id_empresa):
        return db.query(VinculosLaborales).join(Usuarios, Usuarios.id == VinculosLaborales.id_usuario).filter(
            VinculosLaborales.id_usuario == id_usuario, VinculosLaborales.id_empresa == id_empresa,
            VinculosLaborales.rol == "Gerente", VinculosLaborales.activo.is_(True),
            Usuarios.estado.is_(True), Usuarios.rol_plataforma == "Usuario"
        ).first()
