from fastapi import FastAPI , APIRouter, Depends
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.Empresas.schema import Revisar_Json_Nueva_Empresa, NuevaEmpresaRespuesta
from backend.Empresas.service import EmpresaService as service


router = APIRouter (
    prefix= "/empresas",
    tags= ["Empresas"]
)

@router.post("/", response_model=NuevaEmpresaRespuesta, status_code=201)
def crear_empresa(json: Revisar_Json_Nueva_Empresa, db: Session = Depends(abrir_puerta_bd)):
    return service.crear_empresa_service(json, db)
