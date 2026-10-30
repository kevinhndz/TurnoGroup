from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.Sucursales.schema import (
    Revisar_Json_Crear_Sucursal,
    Revisar_Json_Editar_Sucursal,
    RespuestaSucursalCreada,
    RespuestaSucursalEditada,
)
from backend.Sucursales.service import SucursalService as service
from core.schema import RespuestaPaginada



router = APIRouter(
    prefix= "/sucursales",
    tags = ["Sucursales"]
)


@router.post("/", response_model=RespuestaSucursalCreada, status_code=201)
def crear_sucursal(json: Revisar_Json_Crear_Sucursal, db: Session = Depends(abrir_puerta_bd)):
    return service.crear_sucursal_service(json, db)


@router.get("/", response_model=RespuestaPaginada[RespuestaSucursalCreada])
def ver_sucursales(
    id_empresa: int = Query(..., gt=0),
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.listar_sucursales_service(id_empresa, pagina_actual, limite, db)


@router.get("/{id}", response_model=RespuestaSucursalCreada)
def ver_sucursal(
    id: int,
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.ver_sucursal_service(id, id_empresa, db)


@router.patch("/{id}", response_model=RespuestaSucursalEditada)
def editar_sucursal(
    id: int,
    json: Revisar_Json_Editar_Sucursal,
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.editar_sucursal_service(json, id, id_empresa, db)


@router.post("/{id}/desactivar", response_model=RespuestaSucursalEditada)
def desactivar_sucursal(
    id: int,
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.desactivar_sucursal_service(id, id_empresa, db)
