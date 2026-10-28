from fastapi import Depends
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.Empresas.schema import Revisar_Json_Nueva_Empresa, NuevaEmpresaRespuesta, Revisar_Json_Editar_Empresa
from core.exceptions import RecursoDuplicadoError, RecursoNoEncontradoError
from backend.Empresas.repository import EmpresaRepository as repo
from backend.Empresas.tabla import Empresas


class EmpresaService():

    @staticmethod
    def crear_empresa_service(json: Revisar_Json_Nueva_Empresa, db: Session):
     look_up = repo.buscar_empresa(db, json.nombre)

     if look_up is not None:
        raise RecursoDuplicadoError("Error esta empresa ya se encuenta registrada....")

     nueva_empresa = Empresas(
        nombre=json.nombre,
        tipo_negocio=json.tipo_negocio,
        codigo_pais=json.codigo_pais,
        zona_horaria=json.zona_horaria,
        codigo_moneda=json.codigo_moneda
     )
     return repo.guardar_nueva_empresa(db, nueva_empresa)


    @staticmethod
    def listar_empresas_service(pagina_actual: int, limite: int, db: Session):
      total, lista_empresas = repo.listar_empresas(db, pagina_actual, limite)
      total_paginas = (total + limite - 1) // limite

      return {
        "total": total,
        "pagina_actual": pagina_actual,
        "limite": limite,
        "total_paginas": total_paginas,
        "data": lista_empresas
      }

    @staticmethod
    def ver_empresa_actual_service(db: Session):
      look_up = repo.buscar_empresa_actual(db)

      if look_up is None:
        raise RecursoNoEncontradoError("No hay una empresa de demostracion registrada")

      return look_up

    @staticmethod
    def editar_empresa_actual_service(json: Revisar_Json_Editar_Empresa, db: Session):
      look_up = repo.buscar_empresa_actual(db)

      if look_up is None:
        raise RecursoNoEncontradoError("No hay una empresa de demostracion registrada")

      return EmpresaService.editar_empresa_service(json, look_up.id, db)


    @staticmethod
    def editar_empresa_service(json: Revisar_Json_Editar_Empresa, id: int, db: Session):

      look_up = repo.buscar_empresa_por_id(db, id)

      if look_up is None:
        raise RecursoNoEncontradoError("No se encontro la empresa")

      if json.nombre is not None and json.nombre != look_up.nombre:
        empresa_existente = repo.buscar_empresa(db, json.nombre)
        if empresa_existente is not None:
          raise RecursoDuplicadoError("Ya existe una empresa con ese nombre")

      if json.nombre is not None:
        look_up.nombre = json.nombre
      if json.codigo_moneda is not None:
        look_up.codigo_moneda = json.codigo_moneda
      if json.codigo_pais is not None:
        look_up.codigo_pais = json.codigo_pais
      if json.tipo_negocio is not None:
        look_up.tipo_negocio = json.tipo_negocio
      if json.zona_horaria is not None:
        look_up.zona_horaria = json.zona_horaria

      db.commit()
      db.refresh(look_up)
      return look_up
