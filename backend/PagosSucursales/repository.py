from sqlalchemy.orm import Session
from backend.PagosSucursales.tabla import PagosSucursales
from backend.MetodosPago.tabla import MetodosPago


class PagoSucursalRepository():

    @staticmethod
    def buscar_pago_sucursal(db: Session, id_sucursal: int, id_metodo_pago: int) -> PagosSucursales | None:
        return db.query(PagosSucursales).filter(
            PagosSucursales.id_sucursal == id_sucursal,
            PagosSucursales.id_metodo_pago == id_metodo_pago
        ).first()

    @staticmethod
    def guardar_nuevo_pago_sucursal(db: Session, nuevo_pago_sucursal: PagosSucursales) -> PagosSucursales:
        db.add(nuevo_pago_sucursal)
        db.commit()
        db.refresh(nuevo_pago_sucursal)
        return nuevo_pago_sucursal

    @staticmethod
    def listar_pagos_sucursales(
        db: Session, id_sucursal: int, solo_habilitados: bool, pagina_actual: int, limite: int
    ):
        salto = (pagina_actual - 1) * limite
        consulta = db.query(PagosSucursales).join(
            MetodosPago, PagosSucursales.id_metodo_pago == MetodosPago.id
        ).filter(PagosSucursales.id_sucursal == id_sucursal)
        if solo_habilitados:
            consulta = consulta.filter(
                PagosSucursales.habilitado.is_(True),
                MetodosPago.activo.is_(True)
            )
        total = consulta.count()
        lista_pagos_sucursales = consulta.order_by(
            PagosSucursales.id_metodo_pago
        ).offset(salto).limit(limite).all()
        return total, lista_pagos_sucursales
