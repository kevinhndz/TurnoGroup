from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.PagosSucursales.repository import PagoSucursalRepository as repo
from backend.PagosSucursales.schema import (
    Revisar_Json_Crear_Pago_Sucursal,
    Revisar_Json_Editar_Pago_Sucursal,
)
from backend.PagosSucursales.tabla import PagosSucursales
from backend.MetodosPago.repository import MetodoPagoRepository as repo_opcion
from backend.Sucursales.repository import SucursalRespository as repo_sucursal
from core.exceptions import RecursoDuplicadoError, RecursoNoEncontradoError


class PagoSucursalService():

    @staticmethod
    def crear_pago_sucursal_service(json: Revisar_Json_Crear_Pago_Sucursal, id_empresa: int, db: Session, id_sucursal: int):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)
        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal de esta empresa")

        opcion = repo_opcion.buscar_metodo_pago_por_id(db, json.id_metodo_pago)
        if opcion is None:
            raise RecursoNoEncontradoError("No se encontro la opcion del sistema")

        look_up = repo.buscar_pago_sucursal(db, id_sucursal, json.id_metodo_pago)
        if look_up is not None:
            raise RecursoDuplicadoError("La opcion ya esta configurada en esta sucursal")

        nuevo_pago_sucursal = PagosSucursales(
            id_sucursal=id_sucursal,
            id_metodo_pago=json.id_metodo_pago,
            habilitado=json.habilitado,
        )
        return repo.guardar_nuevo_pago_sucursal(db, nuevo_pago_sucursal)

    @staticmethod
    def listar_pagos_sucursales_service(
        id_sucursal: int, id_empresa: int, solo_habilitados: bool,
        pagina_actual: int, limite: int, db: Session
    ):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)
        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal de esta empresa")

        total, lista_pagos_sucursales = repo.listar_pagos_sucursales(
            db, id_sucursal, solo_habilitados, pagina_actual, limite
        )
        total_paginas = (total + limite - 1) // limite
        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_pagos_sucursales
        }

    @staticmethod
    def ver_pago_sucursal_service(id_sucursal: int, id_metodo_pago: int, id_empresa: int, db: Session):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)
        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal de esta empresa")

        look_up = repo.buscar_pago_sucursal(db, id_sucursal, id_metodo_pago)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la configuracion de esta sucursal")

        return look_up

    @staticmethod
    def editar_pago_sucursal_service(
        json: Revisar_Json_Editar_Pago_Sucursal, id_sucursal: int,
        id_metodo_pago: int, id_empresa: int, db: Session
    ):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)
        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal de esta empresa")

        look_up = repo.buscar_pago_sucursal(db, id_sucursal, id_metodo_pago)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la configuracion de esta sucursal")

        cambios = json.model_dump(exclude_unset=True)
        if not cambios:
            raise HTTPException(status_code=422, detail="Debes enviar al menos un campo para editar")
        for campo, valor in cambios.items():
            if valor is None:
                raise HTTPException(status_code=422, detail="El campo " + campo + " no acepta null")
        opcion = repo_opcion.buscar_metodo_pago_por_id(db, id_metodo_pago)
        if opcion is None:
            raise RecursoNoEncontradoError("No se encontro la opcion del sistema")

        for campo, valor in cambios.items():
            setattr(look_up, campo, valor)

        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def desactivar_pago_sucursal_service(id_sucursal: int, id_metodo_pago: int, id_empresa: int, db: Session):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)
        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal de esta empresa")

        look_up = repo.buscar_pago_sucursal(db, id_sucursal, id_metodo_pago)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la configuracion de esta sucursal")

        look_up.habilitado = False
        db.commit()
        db.refresh(look_up)
        return look_up
