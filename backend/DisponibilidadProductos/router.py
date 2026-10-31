from utils.autorizacion import obtener_empresa, obtener_sucursal
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, Response
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.DisponibilidadProductos.schema import (
    RespuestaDisponibilidadProducto,
    Revisar_Json_Crear_Disponibilidad_Producto,
    Revisar_Json_Editar_Disponibilidad_Producto,
)
from backend.DisponibilidadProductos.service import DisponibilidadProductoService as service
from core.schema import RespuestaPaginada


router = APIRouter(prefix="/disponibilidad-productos", tags=["Disponibilidad de productos"])


@router.post("/", response_model=RespuestaDisponibilidadProducto, status_code=201)
def crear_disponibilidad_producto(
    json: Revisar_Json_Crear_Disponibilidad_Producto,
    id_empresa: int = Depends(obtener_empresa),
    id_sucursal: int = Depends(obtener_sucursal),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.crear_disponibilidad_producto_service(json, id_empresa, db, id_sucursal)


@router.get("/", response_model=RespuestaPaginada[RespuestaDisponibilidadProducto])
def ver_disponibilidad_productos(
    id_sucursal: int = Depends(obtener_sucursal),
    id_empresa: int = Depends(obtener_empresa),
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.listar_disponibilidad_productos_service(id_sucursal, id_empresa, pagina_actual, limite, db)


@router.get("/{id_producto}/{id_sucursal}", response_model=RespuestaDisponibilidadProducto)
def ver_disponibilidad_producto(
    id_producto: Annotated[int, Path(gt=0)],
    id_sucursal: Annotated[int, Path(gt=0)],
    id_empresa: int = Depends(obtener_empresa),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.ver_disponibilidad_producto_service(id_producto, id_sucursal, id_empresa, db)


@router.patch("/{id_producto}/{id_sucursal}", response_model=RespuestaDisponibilidadProducto)
def editar_disponibilidad_producto(
    id_producto: Annotated[int, Path(gt=0)],
    id_sucursal: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Editar_Disponibilidad_Producto,
    id_empresa: int = Depends(obtener_empresa),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.editar_disponibilidad_producto_service(json, id_producto, id_sucursal, id_empresa, db)


@router.delete("/{id_producto}/{id_sucursal}", status_code=204)
def retirar_disponibilidad_producto(
    id_producto: Annotated[int, Path(gt=0)],
    id_sucursal: Annotated[int, Path(gt=0)],
    id_empresa: int = Depends(obtener_empresa),
    db: Session = Depends(abrir_puerta_bd)
):
    service.retirar_disponibilidad_producto_service(id_producto, id_sucursal, id_empresa, db)
    return Response(status_code=204)
