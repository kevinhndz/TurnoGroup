from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.ConfiguracionImpuestos.repository import ConfiguracionImpuestosRepository as repo
from backend.ConfiguracionImpuestos.schema import (
    Revisar_Json_Crear_Configuracion_Impuestos,
    Revisar_Json_Editar_Configuracion_Impuestos,
)
from backend.ConfiguracionImpuestos.tabla import ConfiguracionImpuestos
from backend.Empresas.repository import EmpresaRepository as repo_empresa
from core.exceptions import RecursoDuplicadoError, RecursoNoEncontradoError


class ConfiguracionImpuestosService():

    @staticmethod
    def crear_configuracion_impuestos_service(json: Revisar_Json_Crear_Configuracion_Impuestos, db: Session, id_empresa: int):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_configuracion_impuestos_por_empresa(db, id_empresa)
        if look_up is not None:
            raise RecursoDuplicadoError("La empresa ya tiene una configuracion de impuestos")

        nueva_configuracion_impuestos = ConfiguracionImpuestos(
            id_empresa=id_empresa,
            nombre=json.nombre,
            porcentaje=json.porcentaje,
            precios_incluyen_impuesto=json.precios_incluyen_impuesto
        )
        return repo.guardar_nueva_configuracion_impuestos(db, nueva_configuracion_impuestos)

    @staticmethod
    def listar_configuracion_impuestos_service(id_empresa: int, pagina_actual: int, limite: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        total, lista_configuracion_impuestos = repo.listar_configuracion_impuestos(db, id_empresa, pagina_actual, limite)
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_configuracion_impuestos
        }

    @staticmethod
    def ver_configuracion_impuestos_service(id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_configuracion_impuestos_por_id(db, id, id_empresa)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la configuracion de impuestos")

        return look_up

    @staticmethod
    def editar_configuracion_impuestos_service(json: Revisar_Json_Editar_Configuracion_Impuestos, id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_configuracion_impuestos_por_id(db, id, id_empresa)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la configuracion de impuestos")

        cambios = json.model_dump(exclude_unset=True)
        if not cambios:
            raise HTTPException(status_code=422, detail="Debes enviar al menos un campo para editar")
        for campo, valor in cambios.items():
            if valor is None and campo not in ('nombre',):
                raise HTTPException(status_code=422, detail="El campo " + campo + " no acepta null")

        for campo, valor in cambios.items():
            if valor is not None or campo == "nombre":
                setattr(look_up, campo, valor)

        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def desactivar_configuracion_impuestos_service(id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_configuracion_impuestos_por_id(db, id, id_empresa)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la configuracion de impuestos")

        look_up.activo = False
        db.commit()
        db.refresh(look_up)
        return look_up
