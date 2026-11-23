from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.Empresas.repository import EmpresaRepository as repo_empresa
from backend.InvitacionesLaborales.repository import InvitacionLaboralRepository
from backend.Sucursales.repository import SucursalRespository as repo_sucursal
from backend.Usuarios.repository import UsuarioRepository as repo_usuario
from backend.VinculosLaborales.repository import VinculoLaboralRepository as repo
from backend.VinculosLaborales.schema import Revisar_Json_Crear_Vinculo_Laboral
from backend.VinculosLaborales.tabla import AsignacionesSucursales, VinculosLaborales
from core.exceptions import (
    RecursoDuplicadoError,
    RecursoNoEncontradoError,
    SolicitudError,
)


class VinculoLaboralService:
    @staticmethod
    def crear_vinculo_laboral_service(
        json: Revisar_Json_Crear_Vinculo_Laboral, db: Session
    ):
        try:
            id_empresa = json.id_empresa
            InvitacionLaboralRepository.bloquear_empresa(db, id_empresa)

            if json.rol != "Gerente":
                raise SolicitudError(403, "La plataforma solo asigna el primer gerente")
            gerente = repo.buscar_gerente_activo(db, id_empresa)

            if gerente:
                raise SolicitudError(409, "La empresa ya tiene gerente")
            usuario = repo_usuario.buscar_usuario_por_id(db, json.id_usuario)

            if usuario is None:
                raise RecursoNoEncontradoError("No se encontro el usuario")

            if InvitacionLaboralRepository.buscar_otra_empresa(
                db, usuario.id, id_empresa
            ):
                raise SolicitudError(409, "El usuario ya pertenece a otra empresa")

            empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

            if empresa is None:
                raise RecursoNoEncontradoError("No se encontro la empresa")

            look_up = repo.buscar_vinculo_usuario_empresa(
                db, json.id_usuario, id_empresa
            )

            if look_up is not None:
                raise RecursoDuplicadoError(
                    "El usuario ya tiene un vinculo con esta empresa"
                )

            nuevo_vinculo = VinculosLaborales(
                id_usuario=json.id_usuario, id_empresa=id_empresa, rol=json.rol
            )
            resultado = repo.guardar_nuevo_vinculo(db, nuevo_vinculo)
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
    def listar_vinculos_laborales_service(
        id_empresa: int, pagina_actual: int, limite: int, db: Session, filtros=None
    ):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        total, lista_vinculos = repo.listar_vinculos_laborales(
            db, id_empresa, pagina_actual, limite, filtros=filtros
        )
        total_paginas = (total + limite - 1) // limite

        usuarios = {}
        elementos = []

        for item_actual in lista_vinculos:
            elementos.append(item_actual.id_usuario)

        for usuario_actual in repo.listar_usuarios_de_vinculos(db, elementos):
            usuarios[usuario_actual.id] = usuario_actual
        respuesta = []

        for item_actual_2 in lista_vinculos:
            campos = {}

            for campo_actual in ["id", "id_usuario", "id_empresa", "rol", "activo"]:
                campos[campo_actual] = getattr(item_actual_2, campo_actual)
            respuesta.append(
                {
                    **campos,
                    "nombre_usuario": usuarios[item_actual_2.id_usuario].nombre,
                    "correo_usuario": usuarios[item_actual_2.id_usuario].correo,
                }
            )

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": respuesta,
        }

    @staticmethod
    def ver_vinculo_laboral_service(id: int, id_empresa: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_vinculo_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el vinculo laboral")

        asignaciones = repo.listar_asignaciones_sucursales(db, look_up.id)
        usuario = repo_usuario.buscar_usuario_por_id(db, look_up.id_usuario)

        return {
            "nombre_usuario": usuario.nombre,
            "correo_usuario": usuario.correo,
            "id": look_up.id,
            "id_usuario": look_up.id_usuario,
            "id_empresa": look_up.id_empresa,
            "rol": look_up.rol,
            "activo": look_up.activo,
            "asignaciones_sucursales": asignaciones,
        }

    @staticmethod
    def asignar_sucursal_service(
        id: int, id_sucursal: int, id_empresa: int, db: Session
    ):
        try:
            InvitacionLaboralRepository.bloquear_empresa(db, id_empresa)
            look_up = repo.buscar_vinculo_por_id(db, id, id_empresa)

            if look_up is None:
                raise RecursoNoEncontradoError("No se encontro el vinculo laboral")

            sucursal = repo_sucursal.buscar_sucursal_por_id(
                db, id_sucursal, look_up.id_empresa
            )

            if sucursal is None:
                raise RecursoNoEncontradoError(
                    "La sucursal no existe o no pertenece a la empresa del vinculo"
                )

            asignacion_existente = repo.buscar_asignacion_sucursal(
                db, look_up.id, id_sucursal
            )

            if asignacion_existente is not None:
                raise RecursoDuplicadoError(
                    "La sucursal ya esta asignada a este vinculo"
                )

            if look_up.rol != "Gerente" and repo.listar_asignaciones_sucursales(
                db, look_up.id
            ):
                raise SolicitudError(
                    409,
                    "Este rol solo puede tener una sucursal. Retira la anterior antes de asignar otra",
                )

            nueva_asignacion = AsignacionesSucursales(
                id_vinculo_laboral=look_up.id, id_sucursal=id_sucursal
            )
            resultado = repo.guardar_asignacion_sucursal(db, nueva_asignacion)
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
    def quitar_asignacion_sucursal_service(
        id: int, id_sucursal: int, id_empresa: int, db: Session
    ):
        try:
            look_up = repo.buscar_vinculo_por_id(db, id, id_empresa)

            if look_up is None:
                raise RecursoNoEncontradoError("No se encontro el vinculo laboral")

            asignacion = repo.buscar_asignacion_sucursal(db, look_up.id, id_sucursal)

            if asignacion is None:
                raise RecursoNoEncontradoError(
                    "No se encontro la asignacion de la sucursal"
                )

            repo.quitar_asignacion_sucursal(db, asignacion)
            repo.guardar_cambios(db)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def listar_asignaciones_sucursales_service(
        id: int, id_empresa: int, pagina_actual: int, limite: int, db: Session
    ):
        look_up = repo.buscar_vinculo_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el vinculo laboral")
        total, asignaciones = repo.listar_asignaciones_sucursales_paginadas(
            db, id, pagina_actual, limite
        )

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": (total + limite - 1) // limite,
            "data": asignaciones,
        }

    @staticmethod
    def editar_vinculo_laboral_service(json, id, id_empresa, db):
        try:
            InvitacionLaboralRepository.bloquear_empresa(db, id_empresa)
            look_up = repo.buscar_vinculo_por_id(db, id, id_empresa)

            if not look_up:
                raise RecursoNoEncontradoError("No se encontro el vinculo laboral")
            cambios = json.model_dump(exclude_unset=True)

            if (
                cambios.get("rol", look_up.rol) != "Gerente"
                and len(repo.listar_asignaciones_sucursales(db, look_up.id)) > 1
            ):
                raise SolicitudError(
                    409, "Deja una sola sucursal antes de asignar este rol"
                )
            condicion_verificada = not cambios

            if not condicion_verificada:
                cumple_condicion = False

                for valor_actual in cambios.values():
                    if valor_actual is None:
                        cumple_condicion = True
                        break
                condicion_verificada = cumple_condicion

            if condicion_verificada:
                raise SolicitudError(422, "Indica los campos validos que deseas editar")

            if (
                look_up.activo
                and look_up.rol == "Gerente"
                and (
                    cambios.get("rol", look_up.rol) != "Gerente"
                    or not cambios.get("activo", look_up.activo)
                )
            ):
                otros = repo.contar_otros_gerentes(db, id_empresa, id)

                if not otros:
                    raise SolicitudError(
                        409, "La empresa debe conservar al menos un gerente"
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
