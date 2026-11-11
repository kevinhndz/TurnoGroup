from backend.Sesiones.tabla import Sesiones
from backend.Usuarios.tabla import Usuarios


class SesionRepository():

    @staticmethod
    def buscar_usuario_para_sesion(db, correo):
        return db.query(Usuarios).filter(Usuarios.correo == correo).with_for_update().first()

    @staticmethod
    def buscar_sesion(db, token_protegido):
        return db.query(Sesiones).filter(Sesiones.token_protegido == token_protegido).first()

    @staticmethod
    def buscar_sesion_con_usuario(db, token_protegido):
        return db.query(Sesiones, Usuarios).join(Usuarios, Usuarios.id == Sesiones.id_usuario).filter(Sesiones.token_protegido == token_protegido).first()

    @staticmethod
    def guardar_nueva_sesion(db, nueva_sesion):
        db.add(nueva_sesion)
        db.commit()
        db.refresh(nueva_sesion)
        return nueva_sesion

    @staticmethod
    def renovar_sesion(db, id, token_anterior, token_nuevo, ahora):
        return db.query(Sesiones).filter(
            Sesiones.id == id,
            Sesiones.token_protegido == token_anterior,
            Sesiones.fecha_revocacion.is_(None),
            Sesiones.vencimiento > ahora
        ).update({"token_protegido": token_nuevo}, synchronize_session="fetch")

    @staticmethod
    def revocar_sesiones(db, id_usuario, ahora):
        db.query(Sesiones).filter(
            Sesiones.id_usuario == id_usuario,
            Sesiones.fecha_revocacion.is_(None)
        ).update({"fecha_revocacion": ahora}, synchronize_session="fetch")

    @staticmethod
    def buscar_vinculo_autorizado(db, id_usuario, id_vinculo=None):
        from backend.VinculosLaborales.tabla import VinculosLaborales
        from backend.Empresas.tabla import Empresas
        consulta = db.query(VinculosLaborales).join(Empresas, Empresas.id == VinculosLaborales.id_empresa).filter(
            VinculosLaborales.id_usuario == id_usuario,
            VinculosLaborales.activo.is_(True), Empresas.estado.in_(["En Prueba", "Activa"])
        )
        if id_vinculo is not None:
            consulta = consulta.filter(VinculosLaborales.id == id_vinculo)
        return consulta.order_by(VinculosLaborales.id).first()

    @staticmethod
    def buscar_sucursal_autorizada(db, vinculo, id_sucursal=None):
        from backend.Sucursales.tabla import Sucursales
        from backend.VinculosLaborales.tabla import AsignacionesSucursales
        consulta = db.query(Sucursales).filter(
            Sucursales.id_empresa == vinculo.id_empresa, Sucursales.activo.is_(True)
        )
        if vinculo.rol != "Gerente":
            consulta = consulta.join(AsignacionesSucursales, AsignacionesSucursales.id_sucursal == Sucursales.id).filter(
                AsignacionesSucursales.id_vinculo_laboral == vinculo.id
            )
        if id_sucursal is not None:
            consulta = consulta.filter(Sucursales.id == id_sucursal)
        return consulta.order_by(Sucursales.id).first()

    @staticmethod
    def listar_vinculos_usuario(db, id_usuario):
        from backend.VinculosLaborales.tabla import VinculosLaborales
        return db.query(VinculosLaborales).filter(
            VinculosLaborales.id_usuario == id_usuario, VinculosLaborales.activo.is_(True)
        ).order_by(VinculosLaborales.id).all()


    @staticmethod
    def listar_sucursales_autorizadas(db, vinculo):
        from backend.Sucursales.tabla import Sucursales
        from backend.VinculosLaborales.tabla import AsignacionesSucursales
        consulta = db.query(Sucursales).filter(
            Sucursales.id_empresa == vinculo.id_empresa, Sucursales.activo.is_(True)
        )
        if vinculo.rol != "Gerente":
            consulta = consulta.join(AsignacionesSucursales, AsignacionesSucursales.id_sucursal == Sucursales.id).filter(
                AsignacionesSucursales.id_vinculo_laboral == vinculo.id
            )
        return consulta.order_by(Sucursales.id).all()
