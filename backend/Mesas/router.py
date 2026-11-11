from core.listados import filtros_listado
from utils.autorizacion import obtener_empresa, obtener_sucursal
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.Mesas.schema import (
    RespuestaMesa,
    Revisar_Json_Preparar_Mesas,
    Revisar_Json_Crear_Mesa,
    Revisar_Json_Editar_Mesa,
)
from backend.Mesas.service import MesaService as service
from core.schema import RespuestaPaginada

router = APIRouter(prefix="/mesas", tags=["Mesas"])


@router.post("/", response_model=RespuestaMesa, status_code=201)
def crear_mesa(
    json: Revisar_Json_Crear_Mesa,
    id_empresa: int = Depends(obtener_empresa),
    id_sucursal: int = Depends(obtener_sucursal),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.crear_mesa_service(json, id_empresa, db, id_sucursal)


@router.get("/", response_model=RespuestaPaginada[RespuestaMesa])
def ver_mesas(
    id_sucursal: int = Depends(obtener_sucursal),
    id_empresa: int = Depends(obtener_empresa),
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd), filtros=Depends(filtros_listado)):
    return service.listar_mesas_service(
        id_sucursal, pagina_actual, limite, id_empresa, db, filtros=filtros)


@router.post("/preparar")
def preparar_mesas(
    json: Revisar_Json_Preparar_Mesas,
    id_empresa: int = Depends(obtener_empresa),
    id_sucursal: int = Depends(obtener_sucursal),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.preparar_mesas_service(json, db, id_empresa, id_sucursal)


@router.get("/{id}", response_model=RespuestaMesa)
def ver_mesa(
    id: Annotated[int, Path(gt=0)],
    id_sucursal: int = Depends(obtener_sucursal),
    id_empresa: int = Depends(obtener_empresa),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.ver_mesa_service(id, id_sucursal, id_empresa, db)


@router.patch("/{id}", response_model=RespuestaMesa)
def editar_mesa(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Editar_Mesa,
    id_sucursal: int = Depends(obtener_sucursal),
    id_empresa: int = Depends(obtener_empresa),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.editar_mesa_service(json, id, id_sucursal, id_empresa, db)


@router.post("/{id}/desactivar", response_model=RespuestaMesa)
def desactivar_mesa(
    id: Annotated[int, Path(gt=0)],
    id_sucursal: int = Depends(obtener_sucursal),
    id_empresa: int = Depends(obtener_empresa),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.desactivar_mesa_service(id, id_sucursal, id_empresa, db)
