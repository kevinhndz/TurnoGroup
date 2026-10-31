from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.PagosSucursales.schema import (
    RespuestaPagoSucursal,
    Revisar_Json_Crear_Pago_Sucursal,
    Revisar_Json_Editar_Pago_Sucursal,
)
from backend.PagosSucursales.service import PagoSucursalService as service
from core.schema import RespuestaPaginada


router = APIRouter(prefix="/pagos-sucursales", tags=["PagosSucursales"])


@router.post("/", response_model=RespuestaPagoSucursal, status_code=201)
def crear_pago_sucursal(
    json: Revisar_Json_Crear_Pago_Sucursal,
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.crear_pago_sucursal_service(json, id_empresa, db)


@router.get("/", response_model=RespuestaPaginada[RespuestaPagoSucursal])
def ver_pagos_sucursales(
    id_sucursal: int = Query(..., gt=0),
    id_empresa: int = Query(..., gt=0),
    solo_habilitados: bool = True,
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.listar_pagos_sucursales_service(
        id_sucursal, id_empresa, solo_habilitados, pagina_actual, limite, db
    )


@router.get("/{id_sucursal}/{id_metodo_pago}", response_model=RespuestaPagoSucursal)
def ver_pago_sucursal(
    id_sucursal: Annotated[int, Path(gt=0)],
    id_metodo_pago: Annotated[int, Path(gt=0)],
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.ver_pago_sucursal_service(id_sucursal, id_metodo_pago, id_empresa, db)


@router.patch("/{id_sucursal}/{id_metodo_pago}", response_model=RespuestaPagoSucursal)
def editar_pago_sucursal(
    id_sucursal: Annotated[int, Path(gt=0)],
    id_metodo_pago: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Editar_Pago_Sucursal,
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.editar_pago_sucursal_service(json, id_sucursal, id_metodo_pago, id_empresa, db)


@router.post("/{id_sucursal}/{id_metodo_pago}/desactivar", response_model=RespuestaPagoSucursal)
def desactivar_pago_sucursal(
    id_sucursal: Annotated[int, Path(gt=0)],
    id_metodo_pago: Annotated[int, Path(gt=0)],
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.desactivar_pago_sucursal_service(id_sucursal, id_metodo_pago, id_empresa, db)
