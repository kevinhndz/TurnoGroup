from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.Empresas.schema import Revisar_Json_Nueva_Empresa, Revisar_Json_Editar_Empresa
from core.exceptions import RecursoDuplicadoError, RecursoNoEncontradoError
from backend.Empresas.repository import EmpresaRepository as repo
from backend.Empresas.tabla import Empresas


class EmpresaService():

    @staticmethod
    def crear_empresa_service(json: Revisar_Json_Nueva_Empresa, db: Session, usuario, sesion):
        from backend.InvitacionesLaborales.repository import InvitacionLaboralRepository
        if usuario.rol_plataforma != "Superadministrador" and InvitacionLaboralRepository.buscar_otra_empresa(db, usuario.id):
            raise HTTPException(409, "El usuario ya pertenece a una empresa")
        look_up = repo.buscar_empresa(db, json.nombre)
        if look_up is not None:
            raise RecursoDuplicadoError("Ya existe una empresa con ese nombre")

        nueva_empresa = Empresas(
            nombre=json.nombre,
            tipo_negocio=json.tipo_negocio,
            codigo_pais=json.codigo_pais,
            zona_horaria=json.zona_horaria,
            codigo_moneda=json.codigo_moneda
        )
        from backend.VinculosLaborales.tabla import VinculosLaborales
        db.add(nueva_empresa)
        db.flush()
        from backend.Suscripciones.tabla import Suscripciones
        db.add(Suscripciones(id_empresa=nueva_empresa.id))
        if usuario.rol_plataforma != "Superadministrador":
            vinculo = VinculosLaborales(id_usuario=usuario.id, id_empresa=nueva_empresa.id, rol="Gerente")
            db.add(vinculo)
            db.flush()
            sesion.id_vinculo_laboral = vinculo.id
            sesion.id_sucursal = None
        db.commit()
        db.refresh(nueva_empresa)
        return nueva_empresa

    @staticmethod
    def listar_empresas_service(pagina_actual: int, limite: int, db: Session, id_empresa=None, filtros=None):
        total, lista_empresas = repo.listar_empresas(db, pagina_actual, limite, id_empresa, filtros=filtros)
        total_paginas = (total + limite - 1) // limite
        return {
            "total": total,
            "pagina_actual": pagina_actual,
            "limite": limite,
            "total_paginas": total_paginas,
            "data": lista_empresas
        }

    @staticmethod
    def ver_empresa_service(id: int, db: Session):
        look_up = repo.buscar_empresa_por_id(db, id)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")
        return look_up

    @staticmethod
    def editar_empresa_service(json: Revisar_Json_Editar_Empresa, id: int, db: Session):
        look_up = repo.buscar_empresa_por_id(db, id)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        cambios = json.model_dump(exclude_unset=True)
        if not cambios:
            raise HTTPException(status_code=422, detail="Debes enviar al menos un campo para editar")
        for campo, valor in cambios.items():
            if valor is None:
                raise HTTPException(status_code=422, detail="El campo " + campo + " no acepta null")

        if "nombre" in cambios and cambios["nombre"] != look_up.nombre:
            empresa_existente = repo.buscar_empresa(db, cambios["nombre"])
            if empresa_existente is not None:
                raise RecursoDuplicadoError("Ya existe una empresa con ese nombre")

        for campo, valor in cambios.items():
            setattr(look_up, campo, valor)
        db.commit()
        db.refresh(look_up)
        return look_up

    @staticmethod
    def desactivar_empresa_service(id: int, db: Session):
        look_up = repo.buscar_empresa_por_id(db, id)
        if look_up is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")
        look_up.estado = "Inactiva"
        db.commit()
        db.refresh(look_up)
        return look_up
