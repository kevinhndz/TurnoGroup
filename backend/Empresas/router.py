from utils.autorizacion import obtener_contexto, obtener_sesion
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import Annotated
from database.almacen import abrir_puerta_bd
from backend.Empresas.schema import Revisar_Json_Nueva_Empresa, NuevaEmpresaRespuesta, Revisar_Json_Editar_Empresa
from backend.Empresas.service import EmpresaService as service
from core.schema import RespuestaPaginada


router = APIRouter (
    prefix= "/empresas",
    tags= ["Empresas"]
)

@router.post("/", response_model=NuevaEmpresaRespuesta, status_code=201)
def crear_empresa(json: Revisar_Json_Nueva_Empresa, db: Session = Depends(abrir_puerta_bd), sesion=Depends(obtener_sesion)):
    return service.crear_empresa_service(json, db, sesion[1], sesion[0])

@router.get("/", response_model=RespuestaPaginada[NuevaEmpresaRespuesta])
def ver_empresas(
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd),
    contexto=Depends(obtener_contexto)
):
    return service.listar_empresas_service(pagina_actual, limite, db, contexto["id_empresa"])

@router.get("/{id}", response_model=NuevaEmpresaRespuesta)
def ver_empresa(id: Annotated[int, Path(gt=0)], db: Session = Depends(abrir_puerta_bd)):
    return service.ver_empresa_service(id, db)

@router.patch("/{id}", response_model=NuevaEmpresaRespuesta)
def editar_empresa(id: Annotated[int, Path(gt=0)], json: Revisar_Json_Editar_Empresa, db: Session = Depends(abrir_puerta_bd)):
    return service.editar_empresa_service(json, id, db)


@router.post("/{id}/desactivar", response_model=NuevaEmpresaRespuesta)
def desactivar_empresa(id: Annotated[int, Path(gt=0)], db: Session = Depends(abrir_puerta_bd)):
    return service.desactivar_empresa_service(id, db)
