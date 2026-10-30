from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.Sucursales.schema import Revisar_Json_Crear_Sucursal, RespuestaSucursalCreada
from backend.Sucursales.service import SucursalService as service



router = APIRouter(
    prefix= "/sucursales",
    tags = ["Sucursales"]
)


@router.post("/", response_model=RespuestaSucursalCreada, status_code=201)
def crear_sucursal(json: Revisar_Json_Crear_Sucursal, db: Session = Depends(abrir_puerta_bd)):
    return service.crear_sucursal_service(json, db)
