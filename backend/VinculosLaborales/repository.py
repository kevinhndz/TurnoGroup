from core.listados import pagina_listado
from backend.Usuarios.tabla import Usuarios
from sqlalchemy.orm import Session
from backend.VinculosLaborales.tabla import AsignacionesSucursales, VinculosLaborales


class VinculoLaboralRepository():

    @staticmethod
    def buscar_vinculo_usuario_empresa(db: Session, id_usuario: int, id_empresa: int) -> VinculosLaborales | None:
        return db.query(VinculosLaborales).filter(
            VinculosLaborales.id_usuario == id_usuario,
            VinculosLaborales.id_empresa == id_empresa
        ).first()

    @staticmethod
    def guardar_nuevo_vinculo(db: Session, nuevo_vinculo: VinculosLaborales) -> VinculosLaborales:
        db.add(nuevo_vinculo)
        db.commit()
        db.refresh(nuevo_vinculo)
        return nuevo_vinculo

    @staticmethod
    def listar_vinculos_laborales(db: Session, id_empresa: int, pagina_actual: int, limite: int, filtros=None):
        consulta = db.query(VinculosLaborales).filter(VinculosLaborales.id_empresa == id_empresa)
        consulta = consulta.join(Usuarios, Usuarios.id == VinculosLaborales.id_usuario)
        return pagina_listado(consulta, VinculosLaborales, pagina_actual, limite, filtros, columnas=[Usuarios.nombre, Usuarios.correo])

    @staticmethod
    def buscar_vinculo_por_id(db: Session, id: int, id_empresa: int) -> VinculosLaborales | None:
        return db.query(VinculosLaborales).filter(
            VinculosLaborales.id == id,
            VinculosLaborales.id_empresa == id_empresa
        ).first()

    @staticmethod
    def buscar_vinculo_por_id_sin_empresa(db: Session, id: int) -> VinculosLaborales | None:
        return db.query(VinculosLaborales).filter(VinculosLaborales.id == id).first()

    @staticmethod
    def listar_asignaciones_sucursales(db: Session, id_vinculo_laboral: int):
        return db.query(AsignacionesSucursales).filter(
            AsignacionesSucursales.id_vinculo_laboral == id_vinculo_laboral
        ).all()

    @staticmethod
    def buscar_asignacion_sucursal(db: Session, id_vinculo_laboral: int, id_sucursal: int) -> AsignacionesSucursales | None:
        return db.query(AsignacionesSucursales).filter(
            AsignacionesSucursales.id_vinculo_laboral == id_vinculo_laboral,
            AsignacionesSucursales.id_sucursal == id_sucursal
        ).first()

    @staticmethod
    def guardar_asignacion_sucursal(db: Session, nueva_asignacion: AsignacionesSucursales) -> AsignacionesSucursales:
        db.add(nueva_asignacion)
        db.commit()
        db.refresh(nueva_asignacion)
        return nueva_asignacion

    @staticmethod
    def quitar_asignacion_sucursal(db: Session, asignacion: AsignacionesSucursales):
        db.delete(asignacion)
        db.commit()

    @staticmethod
    def listar_asignaciones_sucursales_paginadas(db: Session, id_vinculo_laboral: int, pagina_actual: int, limite: int):
        salto = (pagina_actual - 1) * limite
        consulta = db.query(AsignacionesSucursales).filter(
            AsignacionesSucursales.id_vinculo_laboral == id_vinculo_laboral
        )
        total = consulta.count()
        asignaciones = consulta.order_by(AsignacionesSucursales.id).offset(salto).limit(limite).all()
        return total, asignaciones
