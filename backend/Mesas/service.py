from sqlalchemy.orm import Session
from backend.Mesas.repository import MesaRepository as repo
from backend.Mesas.schema import Revisar_Json_Crear_Mesa, Revisar_Json_Editar_Mesa
from backend.Mesas.tabla import Mesas
from backend.Sucursales.repository import SucursalRespository as repo_sucursal
from core.exceptions import RecursoDuplicadoError, RecursoNoEncontradoError


class MesaService():

    @staticmethod
    def crear_mesa_service(json: Revisar_Json_Crear_Mesa, db: Session):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, json.id_sucursal, json.id_sucursal)

        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal")

        look_up = repo.buscar_mesa_por_nombre(db, json.id_sucursal, json.nombre)
        if look_up is not None:
            raise RecursoDuplicadoError("Ya existe una mesa con ese nombre en la sucursal")

        nueva_mesa = Mesas(
            id_sucursal=json.id_sucursal,
            nombre=json.nombre,
            capacidad=json.capacidad
        )
        return repo.guardar_nueva_mesa(db, nueva_mesa)

    @staticmethod
    def listar_mesas_service(id_sucursal: int, pagina_actual: int, limite: int, db: Session):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_sucursal)

        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal")

        total, lista_mesas = repo.listar_mesas(db, id_sucursal, pagina_actual, limite)
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_mesas
        }

    @staticmethod
    def ver_mesa_service(id: int, id_sucursal: int, db: Session):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_sucursal)

        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal")

        look_up = repo.buscar_mesa_por_id(db, id, id_sucursal)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la mesa")

        return look_up

    @staticmethod
    def editar_mesa_service(json: Revisar_Json_Editar_Mesa, id: int, id_sucursal: int, db: Session):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_sucursal)

        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal")

        look_up = repo.buscar_mesa_por_id(db, id, id_sucursal)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la mesa")

        cambios = json.model_dump(exclude_unset=True, exclude_none=True)

        if "nombre" in cambios and cambios["nombre"] != look_up.nombre:
            mesa_existente = repo.buscar_mesa_por_nombre(
                db, id_sucursal, cambios["nombre"]
            )
            if mesa_existente is not None:
                raise RecursoDuplicadoError("Ya existe una mesa con ese nombre en la sucursal")

        for campo, valor in cambios.items():
            setattr(look_up, campo, valor)

        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def desactivar_mesa_service(id: int, id_sucursal: int, db: Session):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_sucursal)

        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal")

        look_up = repo.buscar_mesa_por_id(db, id, id_sucursal)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la mesa")

        look_up.activo = False
        db.commit()
        db.refresh(look_up)
        return look_up
