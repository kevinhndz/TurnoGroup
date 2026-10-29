from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from typing import Annotated
from database.almacen import abrir_puerta_bd
from backend.Productos.schema import (
    NuevoProductoRespuesta,
    Revisar_Json_Editar_Producto,
    Revisar_Json_Nuevo_Producto,
)
from backend.Productos.service import ProductoService as service


router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)


@router.post("/", response_model=NuevoProductoRespuesta, status_code=201)
def crear_producto(json: Revisar_Json_Nuevo_Producto, db: Session = Depends(abrir_puerta_bd)):
    return service.crear_producto_service(json, db)


@router.get("/", response_model=list[NuevoProductoRespuesta])
def ver_productos(id_empresa: int = Query(..., gt=0), db: Session = Depends(abrir_puerta_bd)):
    return service.listar_productos_service(id_empresa, db)


@router.get("/{id}", response_model=NuevoProductoRespuesta)
def ver_producto(id: Annotated[int, Path(gt=0)], id_empresa: int = Query(..., gt=0), db: Session = Depends(abrir_puerta_bd)):
    return service.ver_producto_service(id, id_empresa, db)


@router.patch("/{id}", response_model=NuevoProductoRespuesta)
def editar_producto(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Editar_Producto,
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.editar_producto_service(json, id, id_empresa, db)


@router.post("/{id}/desactivar", response_model=NuevoProductoRespuesta)
def desactivar_producto(id: Annotated[int, Path(gt=0)], id_empresa: int = Query(..., gt=0), db: Session = Depends(abrir_puerta_bd)):
    return service.desactivar_producto_service(id, id_empresa, db)
