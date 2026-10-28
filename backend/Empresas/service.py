from fastapi import Depends
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.Empresas.schema import Revisar_Json_Nueva_Empresa, NuevaEmpresaRespuesta
from core.exceptions import RecursoDuplicadoError
from backend.Empresas.repository import EmpresaRepository as repo
from backend.Empresas.tabla import Empresas


class EmpresaService():

    @staticmethod
    def crear_empresa_service(json: Revisar_Json_Nueva_Empresa, db: Session):
     look_up = repo.buscar_empresa(db,json)

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
   
