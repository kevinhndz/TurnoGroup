from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.VinculosLaborales.schema import (
    RespuestaAsignacionSucursal,
    RespuestaVinculoLaboral,
    RespuestaVinculoLaboralDetalle,
    Revisar_Json_Asignar_Sucursal,
    Revisar_Json_Crear_Vinculo_Laboral,
)
from backend.VinculosLaborales.service import VinculoLaboralService as service
from core.schema import RespuestaPaginada


router = APIRouter(
    prefix="/vinculos-laborales",
    tags=["Vinculos Laborales"]
)


@router.post("/", response_model=RespuestaVinculoLaboral, status_code=201)
def crear_vinculo_laboral(
    json: Revisar_Json_Crear_Vinculo_Laboral,
    db: Session = Depends(abrir_puerta_bd)
):
    return service.crear_vinculo_laboral_service(json, db)


@router.get("/", response_model=RespuestaPaginada[RespuestaVinculoLaboral])
def ver_vinculos_laborales(
    id_empresa: int = Query(..., gt=0),
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.listar_vinculos_laborales_service(
        id_empresa, pagina_actual, limite, db
    )


@router.get("/{id}", response_model=RespuestaVinculoLaboralDetalle)
def ver_vinculo_laboral(
    id: Annotated[int, Path(gt=0)],
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.ver_vinculo_laboral_service(id, id_empresa, db)


@router.post(
    "/{id}/sucursales",
    response_model=RespuestaAsignacionSucursal,
    status_code=201
)
def asignar_sucursal(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Asignar_Sucursal,
    db: Session = Depends(abrir_puerta_bd)
):
    return service.asignar_sucursal_service(id, json.id_sucursal, db)


@router.delete(
    "/{id}/sucursales/{id_sucursal}",
    status_code=status.HTTP_204_NO_CONTENT
)
def quitar_asignacion_sucursal(
    id: Annotated[int, Path(gt=0)],
    id_sucursal: Annotated[int, Path(gt=0)],
    db: Session = Depends(abrir_puerta_bd)
):
    service.quitar_asignacion_sucursal_service(id, id_sucursal, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
