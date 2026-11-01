from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.Sucursales.repository import SucursalRespository as repo
from backend.Sucursales.schema import Revisar_Json_Crear_Sucursal, Revisar_Json_Editar_Sucursal
from backend.Sucursales.tabla import Sucursales
from backend.Empresas.repository import EmpresaRepository as repo_empresa
from core.exceptions import RecursoNoEncontradoError, RecursoDuplicadoError


class SucursalService():

    @staticmethod
    def crear_sucursal_service(json: Revisar_Json_Crear_Sucursal, db: Session, id_empresa: int):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_sucursal(db, id_empresa, json.nombre, json.direccion)

        if look_up is not None:
            raise RecursoDuplicadoError("Ya existe una sucursal con ese nombre y direccion")

        if json.es_principal is True:
            sucursal_principal = repo.buscar_sucursal_principal(db, id_empresa)
            if sucursal_principal is not None:
                raise RecursoDuplicadoError("La empresa ya tiene una sucursal principal")

        nueva_sucursal = Sucursales(
            id_empresa=id_empresa,
            nombre=json.nombre,
            direccion=json.direccion,
            telefono=json.telefono,
            es_principal=json.es_principal
        )

        return repo.guardar_nueva_sucursal(db, nueva_sucursal)

    @staticmethod
    def listar_sucursales_service(id_empresa: int, pagina_actual: int, limite: int, db: Session, id_sucursal=None, filtros=None):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        total, lista_sucursales = repo.listar_sucursales(
            db, id_empresa, pagina_actual, limite, id_sucursal, filtros=filtros)
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_sucursales
        }

    @staticmethod
    def ver_sucursal_service(id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_sucursal_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal")

        return look_up

    @staticmethod
    def editar_sucursal_service(json: Revisar_Json_Editar_Sucursal, id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_sucursal_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal")

        cambios = json.model_dump(exclude_unset=True)
        if not cambios:
            raise HTTPException(status_code=422, detail="Debes enviar al menos un campo para editar")
        for campo, valor in cambios.items():
            if valor is None and campo not in ('telefono',):
                raise HTTPException(status_code=422, detail="El campo " + campo + " no acepta null")

        if "nombre" in cambios or "direccion" in cambios:
            sucursal_existente = repo.buscar_sucursal(db, id_empresa, cambios.get("nombre", look_up.nombre), cambios.get("direccion", look_up.direccion))
            if sucursal_existente is not None and sucursal_existente.id != look_up.id:
                raise RecursoDuplicadoError("Ya existe una sucursal con ese nombre y direccion")

        es_principal = cambios.get("es_principal", look_up.es_principal)
        activo = cambios.get("activo", look_up.activo)
        if es_principal and activo:
            sucursal_principal = repo.buscar_sucursal_principal(db, id_empresa)
            if sucursal_principal is not None and sucursal_principal.id != look_up.id:
                raise RecursoDuplicadoError("La empresa ya tiene una sucursal principal")

        for campo, valor in cambios.items():
            setattr(look_up, campo, valor)

        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def desactivar_sucursal_service(id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_sucursal_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal")

        look_up.activo = False
        db.commit()
        db.refresh(look_up)
        return look_up
