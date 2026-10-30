from sqlalchemy.orm import Session
from backend.Sucursales.repository import SucursalRespository as repo
from backend.Sucursales.schema import Revisar_Json_Crear_Sucursal
from backend.Sucursales.tabla import Sucursales
from backend.Empresas.repository import EmpresaRepository as repo_empresa
from core.exceptions import RecursoNoEncontradoError, RecursoDuplicadoError


class SucursalService():

    @staticmethod
    def crear_sucursal_service(json: Revisar_Json_Crear_Sucursal, db: Session):
        empresa = repo_empresa.buscar_empresa_por_id(db, json.id_empresa)

        if empresa is None:
            raise RecursoNoEncontradoError("No se encontro la empresa")

        look_up = repo.buscar_sucursal(db, json.id_empresa, json.nombre)

        if look_up is not None:
            raise RecursoDuplicadoError("Ya existe esta sucursal")

        if json.es_principal is True:
            sucursal_principal = repo.buscar_sucursal_principal(db, json.id_empresa)
            if sucursal_principal is not None:
                raise RecursoDuplicadoError("La empresa ya tiene una sucursal principal")

        nueva_sucursal = Sucursales(
            id_empresa=json.id_empresa,
            nombre=json.nombre,
            direccion=json.direccion,
            telefono=json.telefono,
            es_principal=json.es_principal
        )

        return repo.guardar_nueva_sucursal(db, nueva_sucursal)
