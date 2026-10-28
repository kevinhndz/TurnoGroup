from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.Empresas.schema import Revisar_Json_Nueva_Empresa, NuevaEmpresaRespuesta
from backend.Empresas.service import EmpresaService as service
from core.schema import RespuestaPaginada


router = APIRouter (
    prefix= "/empresas",
    tags= ["Empresas"]
)

@router.post("/", response_model=NuevaEmpresaRespuesta, status_code=201)
def crear_empresa(json: Revisar_Json_Nueva_Empresa, db: Session = Depends(abrir_puerta_bd)):
    return service.crear_empresa_service(json, db)

@router.get("/", response_model=RespuestaPaginada[NuevaEmpresaRespuesta])
def ver_empresas(
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.listar_empresas_service(pagina_actual, limite, db)
