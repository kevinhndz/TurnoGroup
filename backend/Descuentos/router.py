from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.Descuentos.schema import (
    RespuestaDescuento,
    Revisar_Json_Crear_Descuento,
    Revisar_Json_Editar_Descuento,
)
from backend.Descuentos.service import DescuentoService as service
from core.schema import RespuestaPaginada


router = APIRouter(
    prefix="/descuentos",
    tags=["Descuentos"]
)


@router.post("/", response_model=RespuestaDescuento, status_code=201)
def crear_descuento(json: Revisar_Json_Crear_Descuento, db: Session = Depends(abrir_puerta_bd)):
    return service.crear_descuento_service(json, db)


@router.get("/", response_model=RespuestaPaginada[RespuestaDescuento])
def ver_descuentos(
    id_empresa: int = Query(..., gt=0),
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.listar_descuentos_service(id_empresa, pagina_actual, limite, db)


@router.get("/{id}", response_model=RespuestaDescuento)
def ver_descuento(
    id: Annotated[int, Path(gt=0)],
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.ver_descuento_service(id, id_empresa, db)


@router.patch("/{id}", response_model=RespuestaDescuento)
def editar_descuento(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Editar_Descuento,
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.editar_descuento_service(json, id, id_empresa, db)


@router.post("/{id}/desactivar", response_model=RespuestaDescuento)
def desactivar_descuento(
    id: Annotated[int, Path(gt=0)],
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.desactivar_descuento_service(id, id_empresa, db)
