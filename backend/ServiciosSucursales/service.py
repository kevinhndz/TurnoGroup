from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.ServiciosSucursales.repository import ServicioSucursalRepository as repo
from backend.ServiciosSucursales.schema import (
    Revisar_Json_Crear_Servicio_Sucursal,
    Revisar_Json_Editar_Servicio_Sucursal,
)
from backend.ServiciosSucursales.tabla import ServiciosSucursales
from backend.Sucursales.repository import SucursalRespository as repo_sucursal
from backend.TiposServicio.repository import TipoServicioRepository as repo_opcion
from core.exceptions import (
    RecursoDuplicadoError,
    RecursoNoEncontradoError,
    SolicitudError,
)


class ServicioSucursalService:
    @staticmethod
    def crear_servicio_sucursal_service(
        json: Revisar_Json_Crear_Servicio_Sucursal,
        id_empresa: int,
        db: Session,
        id_sucursal: int,
    ):
        try:
            sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)

            if sucursal is None:
                raise RecursoNoEncontradoError(
                    "No se encontro la sucursal de esta empresa"
                )

            opcion = repo_opcion.buscar_tipo_servicio_por_id(db, json.id_tipo_servicio)

            if opcion is None:
                raise RecursoNoEncontradoError("No se encontro la opcion del sistema")

            look_up = repo.buscar_servicio_sucursal(
                db, id_sucursal, json.id_tipo_servicio
            )

            if look_up is not None:
                raise RecursoDuplicadoError(
                    "La opcion ya esta configurada en esta sucursal"
                )

            if opcion.clave_concepto != "comer_aqui" and (
                json.mesas_habilitadas or json.reservas_habilitadas
            ):
                raise SolicitudError(
                    status_code=422, detail="Solo Comer aqui permite mesas y reservas"
                )

            if json.mesas_habilitadas and not json.habilitado:
                raise SolicitudError(
                    status_code=422,
                    detail="Debes habilitar el servicio para usar mesas",
                )

            if json.reservas_habilitadas and not json.mesas_habilitadas:
                raise SolicitudError(
                    status_code=422, detail="Las reservas requieren mesas habilitadas"
                )

            nuevo_servicio_sucursal = ServiciosSucursales(
                id_sucursal=id_sucursal,
                id_tipo_servicio=json.id_tipo_servicio,
                habilitado=json.habilitado,
                mesas_habilitadas=json.mesas_habilitadas,
                reservas_habilitadas=json.reservas_habilitadas,
            )
            resultado = repo.guardar_nuevo_servicio_sucursal(
                db, nuevo_servicio_sucursal
            )
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
    def listar_servicios_sucursales_service(
        id_sucursal: int,
        id_empresa: int,
        solo_habilitados: bool,
        pagina_actual: int,
        limite: int,
        db: Session,
    ):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)

        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal de esta empresa")

        total, lista_servicios_sucursales = repo.listar_servicios_sucursales(
            db, id_sucursal, solo_habilitados, pagina_actual, limite
        )
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_servicios_sucursales,
        }

    @staticmethod
    def ver_servicio_sucursal_service(
        id_sucursal: int, id_tipo_servicio: int, id_empresa: int, db: Session
    ):
        sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)

        if sucursal is None:
            raise RecursoNoEncontradoError("No se encontro la sucursal de esta empresa")

        look_up = repo.buscar_servicio_sucursal(db, id_sucursal, id_tipo_servicio)

        if look_up is None:
            raise RecursoNoEncontradoError(
                "No se encontro la configuracion de esta sucursal"
            )

        return look_up

    @staticmethod
    def editar_servicio_sucursal_service(
        json: Revisar_Json_Editar_Servicio_Sucursal,
        id_sucursal: int,
        id_tipo_servicio: int,
        id_empresa: int,
        db: Session,
    ):
        try:
            sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)

            if sucursal is None:
                raise RecursoNoEncontradoError(
                    "No se encontro la sucursal de esta empresa"
                )

            look_up = repo.buscar_servicio_sucursal(db, id_sucursal, id_tipo_servicio)

            if look_up is None:
                raise RecursoNoEncontradoError(
                    "No se encontro la configuracion de esta sucursal"
                )

            cambios = json.model_dump(exclude_unset=True)

            if not cambios:
                raise SolicitudError(
                    status_code=422, detail="Debes enviar al menos un campo para editar"
                )

            for campo, valor in cambios.items():
                if valor is None:
                    raise SolicitudError(
                        status_code=422, detail="El campo " + campo + " no acepta null"
                    )
            opcion = repo_opcion.buscar_tipo_servicio_por_id(db, id_tipo_servicio)

            if opcion is None:
                raise RecursoNoEncontradoError("No se encontro la opcion del sistema")
            habilitado = cambios.get("habilitado", look_up.habilitado)
            mesas_habilitadas = cambios.get(
                "mesas_habilitadas", look_up.mesas_habilitadas
            )
            reservas_habilitadas = cambios.get(
                "reservas_habilitadas", look_up.reservas_habilitadas
            )

            if opcion.clave_concepto != "comer_aqui" and (
                mesas_habilitadas or reservas_habilitadas
            ):
                raise SolicitudError(
                    status_code=422, detail="Solo Comer aqui permite mesas y reservas"
                )

            if mesas_habilitadas and not habilitado:
                raise SolicitudError(
                    status_code=422,
                    detail="Debes habilitar el servicio para usar mesas",
                )

            if reservas_habilitadas and not mesas_habilitadas:
                raise SolicitudError(
                    status_code=422, detail="Las reservas requieren mesas habilitadas"
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
    def desactivar_servicio_sucursal_service(
        id_sucursal: int, id_tipo_servicio: int, id_empresa: int, db: Session
    ):
        try:
            sucursal = repo_sucursal.buscar_sucursal_por_id(db, id_sucursal, id_empresa)

            if sucursal is None:
                raise RecursoNoEncontradoError(
                    "No se encontro la sucursal de esta empresa"
                )

            look_up = repo.buscar_servicio_sucursal(db, id_sucursal, id_tipo_servicio)

            if look_up is None:
                raise RecursoNoEncontradoError(
                    "No se encontro la configuracion de esta sucursal"
                )

            look_up.habilitado = False
            look_up.mesas_habilitadas = False
            look_up.reservas_habilitadas = False
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
