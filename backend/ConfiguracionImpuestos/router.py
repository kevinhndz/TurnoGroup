from core.listados import filtros_listado
from utils.autorizacion import obtener_empresa, obtener_sucursal_catalogo
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.ConfiguracionImpuestos.schema import (
    RespuestaConfiguracionImpuestos,
    Revisar_Json_Crear_Configuracion_Impuestos,
    Revisar_Json_Editar_Configuracion_Impuestos,
)
from backend.ConfiguracionImpuestos.service import ConfiguracionImpuestosService as service
from core.schema import RespuestaPaginada


router = APIRouter(
    prefix="/configuracion-impuestos",
    tags=["Configuracion de impuestos"]
)


@router.post("/", response_model=RespuestaConfiguracionImpuestos, status_code=201)
def crear_configuracion_impuestos(json: Revisar_Json_Crear_Configuracion_Impuestos, db: Session = Depends(abrir_puerta_bd), id_empresa: int = Depends(obtener_empresa)):
    return service.crear_configuracion_impuestos_service(json, db, id_empresa)


@router.get("/", response_model=RespuestaPaginada[RespuestaConfiguracionImpuestos])
def ver_configuraciones_impuestos(
    id_empresa: int = Depends(obtener_empresa),
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd), filtros=Depends(filtros_listado)):
    return service.listar_configuracion_impuestos_service(id_empresa, pagina_actual, limite, db, filtros=filtros)


@router.get("/{id}", response_model=RespuestaConfiguracionImpuestos)
def ver_configuracion_impuestos(
    id: Annotated[int, Path(gt=0)],
    id_empresa: int = Depends(obtener_empresa),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.ver_configuracion_impuestos_service(id, id_empresa, db)


@router.patch("/{id}", response_model=RespuestaConfiguracionImpuestos)
def editar_configuracion_impuestos(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Editar_Configuracion_Impuestos,
    id_empresa: int = Depends(obtener_empresa),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.editar_configuracion_impuestos_service(json, id, id_empresa, db)


@router.post("/{id}/desactivar", response_model=RespuestaConfiguracionImpuestos)
def desactivar_configuracion_impuestos(
    id: Annotated[int, Path(gt=0)],
    id_empresa: int = Depends(obtener_empresa),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.desactivar_configuracion_impuestos_service(id, id_empresa, db)
