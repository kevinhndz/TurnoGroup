from sqlalchemy.orm import Session
from backend.ConfiguracionImpuestos.tabla import ConfiguracionImpuestos


class ConfiguracionImpuestosRepository():

    @staticmethod
    def buscar_configuracion_impuestos_por_empresa(db: Session, id_empresa: int) -> ConfiguracionImpuestos | None:
        return db.query(ConfiguracionImpuestos).filter(ConfiguracionImpuestos.id_empresa == id_empresa).first()

    @staticmethod
    def guardar_nueva_configuracion_impuestos(db: Session, nueva_configuracion_impuestos: ConfiguracionImpuestos) -> ConfiguracionImpuestos:
        db.add(nueva_configuracion_impuestos)
        db.commit()
        db.refresh(nueva_configuracion_impuestos)
        return nueva_configuracion_impuestos

    @staticmethod
    def listar_configuracion_impuestos(db: Session, id_empresa: int, pagina_actual: int, limite: int):
        salto = (pagina_actual - 1) * limite
        total = db.query(ConfiguracionImpuestos).filter(ConfiguracionImpuestos.id_empresa == id_empresa).count()
        lista_configuracion_impuestos = db.query(ConfiguracionImpuestos).filter(
            ConfiguracionImpuestos.id_empresa == id_empresa
        ).order_by(ConfiguracionImpuestos.id).offset(salto).limit(limite).all()
        return total, lista_configuracion_impuestos

    @staticmethod
    def buscar_configuracion_impuestos_por_id(db: Session, id: int, id_empresa: int) -> ConfiguracionImpuestos | None:
        return db.query(ConfiguracionImpuestos).filter(
            ConfiguracionImpuestos.id == id,
            ConfiguracionImpuestos.id_empresa == id_empresa
        ).first()
