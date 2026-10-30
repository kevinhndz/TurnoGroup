from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.Mesas.schema import (
    RespuestaMesa,
    Revisar_Json_Crear_Mesa,
    Revisar_Json_Editar_Mesa,
)
from backend.Mesas.service import MesaService as service
from core.schema import RespuestaPaginada


router = APIRouter(
    prefix="/mesas",
    tags=["Mesas"]
)


@router.post("/", response_model=RespuestaMesa, status_code=201)
def crear_mesa(json: Revisar_Json_Crear_Mesa, db: Session = Depends(abrir_puerta_bd)):
    return service.crear_mesa_service(json, db)


@router.get("/", response_model=RespuestaPaginada[RespuestaMesa])
def ver_mesas(
    id_sucursal: int = Query(..., gt=0),
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.listar_mesas_service(id_sucursal, pagina_actual, limite, db)


@router.get("/{id}", response_model=RespuestaMesa)
def ver_mesa(
    id: Annotated[int, Path(gt=0)],
    id_sucursal: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.ver_mesa_service(id, id_sucursal, db)


@router.patch("/{id}", response_model=RespuestaMesa)
def editar_mesa(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Editar_Mesa,
    id_sucursal: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.editar_mesa_service(json, id, id_sucursal, db)


@router.post("/{id}/desactivar", response_model=RespuestaMesa)
def desactivar_mesa(
    id: Annotated[int, Path(gt=0)],
    id_sucursal: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.desactivar_mesa_service(id, id_sucursal, db)
