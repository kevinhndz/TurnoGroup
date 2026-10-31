from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.ServiciosSucursales.schema import (
    RespuestaServicioSucursal,
    Revisar_Json_Crear_Servicio_Sucursal,
    Revisar_Json_Editar_Servicio_Sucursal,
)
from backend.ServiciosSucursales.service import ServicioSucursalService as service
from core.schema import RespuestaPaginada


router = APIRouter(prefix="/servicios-sucursales", tags=["ServiciosSucursales"])


@router.post("/", response_model=RespuestaServicioSucursal, status_code=201)
def crear_servicio_sucursal(
    json: Revisar_Json_Crear_Servicio_Sucursal,
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.crear_servicio_sucursal_service(json, id_empresa, db)


@router.get("/", response_model=RespuestaPaginada[RespuestaServicioSucursal])
def ver_servicios_sucursales(
    id_sucursal: int = Query(..., gt=0),
    id_empresa: int = Query(..., gt=0),
    solo_habilitados: bool = True,
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.listar_servicios_sucursales_service(
        id_sucursal, id_empresa, solo_habilitados, pagina_actual, limite, db
    )


@router.get("/{id_sucursal}/{id_tipo_servicio}", response_model=RespuestaServicioSucursal)
def ver_servicio_sucursal(
    id_sucursal: Annotated[int, Path(gt=0)],
    id_tipo_servicio: Annotated[int, Path(gt=0)],
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.ver_servicio_sucursal_service(id_sucursal, id_tipo_servicio, id_empresa, db)


@router.patch("/{id_sucursal}/{id_tipo_servicio}", response_model=RespuestaServicioSucursal)
def editar_servicio_sucursal(
    id_sucursal: Annotated[int, Path(gt=0)],
    id_tipo_servicio: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Editar_Servicio_Sucursal,
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.editar_servicio_sucursal_service(json, id_sucursal, id_tipo_servicio, id_empresa, db)


@router.post("/{id_sucursal}/{id_tipo_servicio}/desactivar", response_model=RespuestaServicioSucursal)
def desactivar_servicio_sucursal(
    id_sucursal: Annotated[int, Path(gt=0)],
    id_tipo_servicio: Annotated[int, Path(gt=0)],
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.desactivar_servicio_sucursal_service(id_sucursal, id_tipo_servicio, id_empresa, db)
