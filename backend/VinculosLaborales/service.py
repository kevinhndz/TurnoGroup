from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.Empresas.repository import EmpresaRepository as repo_empresa
from backend.Sucursales.repository import SucursalRespository as repo_sucursal
from backend.Usuarios.repository import UsuarioRepository as repo_usuario
from backend.VinculosLaborales.repository import VinculoLaboralRepository as repo
from backend.VinculosLaborales.schema import Revisar_Json_Crear_Vinculo_Laboral
from backend.VinculosLaborales.tabla import AsignacionesSucursales, VinculosLaborales
from core.exceptions import RecursoDuplicadoError, RecursoNoEncontradoError


class VinculoLaboralService():

    @staticmethod
    def crear_vinculo_laboral_service(json: Revisar_Json_Crear_Vinculo_Laboral, db: Session):
        from backend.InvitacionesLaborales.repository import InvitacionLaboralRepository
        id_empresa = json.id_empresa
        InvitacionLaboralRepository.bloquear_empresa(db, id_empresa)
        if json.rol != "Gerente":
            raise HTTPException(403, "La plataforma solo asigna el primer gerente")
        gerente = db.query(VinculosLaborales).filter(
            VinculosLaborales.id_empresa == id_empresa, VinculosLaborales.rol == "Gerente",
            VinculosLaborales.activo.is_(True)
        ).first()
        if gerente:
            raise HTTPException(409, "La empresa ya tiene gerente")
        usuario = repo_usuario.buscar_usuario_por_id(db, json.id_usuario)
        if usuario is None:
            raise RecursoNoEncontradoError("No se encontro el usuario")

        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_vinculo_usuario_empresa(db, json.id_usuario, id_empresa)
        if look_up is not None:
            raise RecursoDuplicadoError("El usuario ya tiene un vinculo con esta empresa")

        nuevo_vinculo = VinculosLaborales(
            id_usuario=json.id_usuario,
            id_empresa=id_empresa,
            rol=json.rol
        )
        return repo.guardar_nuevo_vinculo(db, nuevo_vinculo)

    @staticmethod
    def listar_vinculos_laborales_service(id_empresa: int, pagina_actual: int, limite: int, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, id_empresa)
        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        total, lista_vinculos = repo.listar_vinculos_laborales(
            db, id_empresa, pagina_actual, limite
        )
        total_paginas = (total + limite - 1) // limite

        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_vinculos
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
        return {
            "id": look_up.id,
            "id_usuario": look_up.id_usuario,
            "id_empresa": look_up.id_empresa,
            "rol": look_up.rol,
            "activo": look_up.activo,
            "asignaciones_sucursales": asignaciones
        }

    @staticmethod
    def asignar_sucursal_service(id: int, id_sucursal: int, id_empresa: int, db: Session):
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

        asignacion_existente = repo.buscar_asignacion_sucursal(db, look_up.id, id_sucursal)
        if asignacion_existente is not None:
            raise RecursoDuplicadoError("La sucursal ya esta asignada a este vinculo")

        nueva_asignacion = AsignacionesSucursales(
            id_vinculo_laboral=look_up.id,
            id_sucursal=id_sucursal
        )
        return repo.guardar_asignacion_sucursal(db, nueva_asignacion)

    @staticmethod
    def quitar_asignacion_sucursal_service(id: int, id_sucursal: int, id_empresa: int, db: Session):
        look_up = repo.buscar_vinculo_por_id(db, id, id_empresa)

        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el vinculo laboral")

        asignacion = repo.buscar_asignacion_sucursal(db, look_up.id, id_sucursal)
        if asignacion is None:
            raise RecursoNoEncontradoError("No se encontro la asignacion de la sucursal")

        repo.quitar_asignacion_sucursal(db, asignacion)

    @staticmethod
    def listar_asignaciones_sucursales_service(id: int, id_empresa: int, pagina_actual: int, limite: int, db: Session):
        look_up = repo.buscar_vinculo_por_id(db, id, id_empresa)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro el vinculo laboral")
        total, asignaciones = repo.listar_asignaciones_sucursales_paginadas(db, id, pagina_actual, limite)
        return {
            "total": total, "pagina_actual": pagina_actual, "limite": limite,
            "total_paginas": (total + limite - 1) // limite, "data": asignaciones
        }


    @staticmethod
    def editar_vinculo_laboral_service(json, id, id_empresa, db):
        from backend.InvitacionesLaborales.repository import InvitacionLaboralRepository
        InvitacionLaboralRepository.bloquear_empresa(db, id_empresa)
        look_up = repo.buscar_vinculo_por_id(db, id, id_empresa)
        if not look_up:
            raise RecursoNoEncontradoError("No se encontro el vinculo laboral")
        cambios = json.model_dump(exclude_unset=True)
        if not cambios or any(valor is None for valor in cambios.values()):
            raise HTTPException(422, "Indica los campos validos que deseas editar")
        if look_up.activo and look_up.rol == "Gerente" and (
            cambios.get("rol", look_up.rol) != "Gerente" or not cambios.get("activo", look_up.activo)
        ):
            otros = db.query(VinculosLaborales).filter(
                VinculosLaborales.id_empresa == id_empresa, VinculosLaborales.id != id,
                VinculosLaborales.rol == "Gerente", VinculosLaborales.activo.is_(True)
            ).count()
            if not otros:
                raise HTTPException(409, "La empresa debe conservar al menos un gerente")
        for campo, valor in cambios.items():
            setattr(look_up, campo, valor)
        db.commit()
        db.refresh(look_up)
        return look_up
