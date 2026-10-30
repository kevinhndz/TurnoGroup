from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.Descuentos.repository import DescuentoRepository as repo
from backend.Descuentos.schema import (
    Revisar_Json_Crear_Descuento,
    Revisar_Json_Editar_Descuento,
)
from backend.Descuentos.tabla import Descuentos
from backend.Empresas.repository import EmpresaRepository as repo_empresa
from core.exceptions import RecursoDuplicadoError, RecursoNoEncontradoError


class DescuentoService():

    @staticmethod
    def crear_descuento_service(json: Revisar_Json_Crear_Descuento, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, json.id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_descuento_por_nombre(db, json.id_empresa, json.nombre)
        if look_up is not None:
            raise RecursoDuplicadoError("Ya existe un descuento con ese nombre en la empresa")

        if json.tipo_descuento == "Porcentaje" and json.valor > 100:
            raise HTTPException(status_code=422, detail="El porcentaje del descuento debe estar entre 0 y 100")

        nuevo_descuento = Descuentos(
            id_empresa=json.id_empresa,
            nombre=json.nombre,
            tipo_descuento=json.tipo_descuento,
            valor=json.valor
        )
        return repo.guardar_nuevo_descuento(db, nuevo_descuento)

    @staticmethod
    def listar_descuentos_service(id_empresa: int, pagina_actual: int, limite: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        total, lista_descuentos = repo.listar_descuentos(db, id_empresa, pagina_actual, limite)
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_descuentos
        }

    @staticmethod
    def ver_descuento_service(id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_descuento_por_id(db, id, id_empresa)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el descuento")

        return look_up

    @staticmethod
    def editar_descuento_service(json: Revisar_Json_Editar_Descuento, id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_descuento_por_id(db, id, id_empresa)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el descuento")

        cambios = json.model_dump(exclude_unset=True, exclude_none=True)

        if "nombre" in cambios and cambios["nombre"] != look_up.nombre:
            descuento_existente = repo.buscar_descuento_por_nombre(
                db, id_empresa, cambios["nombre"]
            )
            if descuento_existente is not None:
                raise RecursoDuplicadoError("Ya existe un descuento con ese nombre en la empresa")

        tipo_descuento = cambios.get("tipo_descuento", look_up.tipo_descuento)
        valor = cambios.get("valor", look_up.valor)

        if tipo_descuento == "Porcentaje" and valor > 100:
            raise HTTPException(status_code=422, detail="El porcentaje del descuento debe estar entre 0 y 100")

        for campo, valor in cambios.items():
            setattr(look_up, campo, valor)

        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def desactivar_descuento_service(id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_descuento_por_id(db, id, id_empresa)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el descuento")

        look_up.activo = False
        db.commit()
        db.refresh(look_up)
        return look_up
