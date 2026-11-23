from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.Cajas.repository import CajaRepository
from backend.Mesas.repository import MesaRepository as repo
from backend.Mesas.schema import Revisar_Json_Crear_Mesa, Revisar_Json_Editar_Mesa
from backend.Mesas.tabla import Mesas
from backend.Sucursales.repository import SucursalRespository as repo_sucursal
from core.exceptions import (
    RecursoDuplicadoError,
    RecursoNoEncontradoError,
    SolicitudError,
)
from core.operaciones import exigir


class MesaService:
    @staticmethod
    def crear_mesa_service(
        json: Revisar_Json_Crear_Mesa, id_empresa: int, db: Session, id_sucursal: int
    ):
        try:
            sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)

            if sucursal is None:
                raise RecursoNoEncontradoError("No se encontro la sucursal")

            look_up = repo.buscar_mesa_por_nombre(db, id_sucursal, json.nombre)

            if look_up is not None:
                raise RecursoDuplicadoError(
                    "Ya existe una mesa con ese nombre en la sucursal"
                )

            nueva_mesa = Mesas(
                id_sucursal=id_sucursal, nombre=json.nombre, capacidad=json.capacidad
            )
            resultado = repo.guardar_nueva_mesa(db, nueva_mesa)
            repo.guardar_cambios(db)
            db.commit()
            repo.actualizar(db, resultado)

            return resultado
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def listar_mesas_service(
        id_sucursal: int,
        pagina_actual: int,
        limite: int,
        id_empresa: int,
        db: Session,
        filtros=None,
    ):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)

        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal")

        total, lista_mesas = repo.listar_mesas(
            db, id_sucursal, pagina_actual, limite, filtros=filtros
        )
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_mesas,
        }

    @staticmethod
    def ver_mesa_service(id: int, id_sucursal: int, id_empresa: int, db: Session):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)

        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal")

        look_up = repo.buscar_mesa_por_id(db, id, id_sucursal)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la mesa")

        return look_up

    @staticmethod
    def editar_mesa_service(
        json: Revisar_Json_Editar_Mesa,
        id: int,
        id_sucursal: int,
        id_empresa: int,
        db: Session,
    ):
        try:
            sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)

            if sucursal is None:
                raise RecursoNoEncontradoError("No se encontro la sucursal")

            look_up = repo.buscar_mesa_por_id(db, id, id_sucursal)

            if look_up is None:
                raise RecursoNoEncontradoError("No se encontro la mesa")

            cambios = json.model_dump(exclude_unset=True)

            if not cambios:
                raise SolicitudError(
                    status_code=422, detail="Debes enviar al menos un campo para editar"
                )

            for campo, valor in cambios.items():
                if valor is None and campo not in ("capacidad",):
                    raise SolicitudError(
                        status_code=422, detail="El campo " + campo + " no acepta null"
                    )

            if "nombre" in cambios and cambios["nombre"] != look_up.nombre:
                mesa_existente = repo.buscar_mesa_por_nombre(
                    db, id_sucursal, cambios["nombre"]
                )

                if mesa_existente is not None:
                    raise RecursoDuplicadoError(
                        "Ya existe una mesa con ese nombre en la sucursal"
                    )

            for campo, valor in cambios.items():
                setattr(look_up, campo, valor)

            repo.guardar_cambios(db)
            db.commit()
            repo.actualizar(db, look_up)

            return look_up
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def desactivar_mesa_service(
        id: int, id_sucursal: int, id_empresa: int, db: Session
    ):
        try:
            sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)

            if sucursal is None:
                raise RecursoNoEncontradoError("No se encontro la sucursal")

            look_up = repo.buscar_mesa_por_id(db, id, id_sucursal)

            if look_up is None:
                raise RecursoNoEncontradoError("No se encontro la mesa")

            look_up.activo = False
            repo.guardar_cambios(db)
            db.commit()
            repo.actualizar(db, look_up)

            return look_up
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def preparar_mesas_service(json, db, id_empresa, id_sucursal):
        try:
            exigir(
                CajaRepository.bloquear_sucursal(db, id_empresa, id_sucursal),
                "No se encontro la sucursal",
                404,
            )
            existentes = repo.listar_mesas_de_sucursal(db, id_sucursal)
            total_calculado = 0

            for mesa_actual in existentes:
                total_calculado += mesa_actual.activo
            faltantes = max(0, json.cantidad - total_calculado)
            nombres = set()

            for mesa_actual_2 in existentes:
                nombres.add(mesa_actual_2.nombre)
            numero = 1

            for _ in range(faltantes):
                while f"Mesa {numero}" in nombres:
                    numero += 1
                repo.agregar(
                    db,
                    Mesas(
                        id_sucursal=id_sucursal,
                        nombre=f"Mesa {numero}",
                        capacidad=json.capacidad,
                    ),
                )
                nombres.add(f"Mesa {numero}")
            repo.guardar_cambios(db)
            db.commit()

            return {"creadas": faltantes}
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise
