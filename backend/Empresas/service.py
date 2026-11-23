from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.Empresas.repository import EmpresaRepository as repo
from backend.Empresas.schema import (
    Revisar_Json_Editar_Empresa,
    Revisar_Json_Nueva_Empresa,
)
from backend.Empresas.tabla import Empresas
from backend.InvitacionesLaborales.repository import InvitacionLaboralRepository
from backend.Suscripciones.tabla import Suscripciones
from backend.VinculosLaborales.tabla import VinculosLaborales
from core.exceptions import (
    RecursoDuplicadoError,
    RecursoNoEncontradoError,
    SolicitudError,
)


class EmpresaService:
    @staticmethod
    def crear_empresa_service(
        json: Revisar_Json_Nueva_Empresa, db: Session, usuario, sesion
    ):
        try:
            if (
                usuario.rol_plataforma != "Superadministrador"
                and InvitacionLaboralRepository.buscar_otra_empresa(db, usuario.id)
            ):
                raise RecursoDuplicadoError("El usuario ya pertenece a una empresa")
            look_up = repo.buscar_empresa(db, json.nombre)

            if look_up is not None:
                raise RecursoDuplicadoError("Ya existe una empresa con ese nombre")

            nueva_empresa = Empresas(
                nombre=json.nombre,
                tipo_negocio=json.tipo_negocio,
                codigo_pais=json.codigo_pais,
                zona_horaria=json.zona_horaria,
                codigo_moneda=json.codigo_moneda,
            )

            repo.agregar(db, nueva_empresa)
            repo.guardar_cambios(db)

            repo.agregar(db, Suscripciones(id_empresa=nueva_empresa.id))

            if usuario.rol_plataforma != "Superadministrador":
                vinculo = VinculosLaborales(
                    id_usuario=usuario.id, id_empresa=nueva_empresa.id, rol="Gerente"
                )
                repo.agregar(db, vinculo)
                repo.guardar_cambios(db)
                sesion.id_vinculo_laboral = vinculo.id
                sesion.id_sucursal = None
            repo.guardar_cambios(db)
            db.commit()
            repo.actualizar(db, nueva_empresa)

            return nueva_empresa
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def listar_empresas_service(
        pagina_actual: int, limite: int, db: Session, id_empresa=None, filtros=None
    ):
        total, lista_empresas = repo.listar_empresas(
            db, pagina_actual, limite, id_empresa, filtros=filtros
        )
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_empresas,
        }

    @staticmethod
    def ver_empresa_service(id: int, db: Session):
        look_up = repo.buscar_empresa_por_id(db, id)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        return look_up

    @staticmethod
    def editar_empresa_service(json: Revisar_Json_Editar_Empresa, id: int, db: Session):
        try:
            look_up = repo.buscar_empresa_por_id(db, id)

            if look_up is None:
                raise RecursoNoEncontradoError("No se encontro la empresa")

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

            if "nombre" in cambios and cambios["nombre"] != look_up.nombre:
                empresa_existente = repo.buscar_empresa(db, cambios["nombre"])

                if empresa_existente is not None:
                    raise RecursoDuplicadoError("Ya existe una empresa con ese nombre")

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
    def desactivar_empresa_service(id: int, db: Session):
        try:
            look_up = repo.buscar_empresa_por_id(db, id)

            if look_up is None:
                raise RecursoNoEncontradoError("No se encontro la empresa")
            look_up.estado = "Inactiva"
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
