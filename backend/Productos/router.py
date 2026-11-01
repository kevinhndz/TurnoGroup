from core.listados import filtros_listado
from utils.autorizacion import obtener_empresa, obtener_sucursal_catalogo
from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import FileResponse
from utils.autorizacion import obtener_sucursal
from sqlalchemy.orm import Session
from typing import Annotated
from database.almacen import abrir_puerta_bd
from backend.Productos.schema import (
    NuevoProductoRespuesta,
    Revisar_Json_Importar_Productos,
    Revisar_Json_Archivo_Productos,
    Revisar_Json_Imagen_Producto,
    Revisar_Json_Editar_Producto,
    Revisar_Json_Nuevo_Producto,
)
from backend.Productos.service import ProductoService as service
from core.schema import RespuestaPaginada

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.post("/", response_model=NuevoProductoRespuesta, status_code=201)
def crear_producto(
    json: Revisar_Json_Nuevo_Producto,
    db: Session = Depends(abrir_puerta_bd),
    id_empresa: int = Depends(obtener_empresa),
):
    return service.crear_producto_service(json, db, id_empresa)


@router.get("/", response_model=RespuestaPaginada[NuevoProductoRespuesta])
def ver_productos(
    id_empresa: int = Depends(obtener_empresa),
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    id_sucursal: int | None = Depends(obtener_sucursal_catalogo),
    db: Session = Depends(abrir_puerta_bd), filtros=Depends(filtros_listado)):
    return service.listar_productos_service(
        id_empresa, pagina_actual, limite, db, id_sucursal, filtros=filtros)


@router.post("/revisar-archivo")
def revisar_archivo_productos(json: Revisar_Json_Archivo_Productos):
    return service.revisar_archivo_service(json)


@router.post("/importar", status_code=201)
def importar_productos(
    json: Revisar_Json_Importar_Productos,
    db: Session = Depends(abrir_puerta_bd),
    id_empresa: int = Depends(obtener_empresa),
    id_sucursal: int = Depends(obtener_sucursal),
):
    return service.importar_productos_service(json, db, id_empresa, id_sucursal)


@router.post("/{id}/imagen", response_model=NuevoProductoRespuesta)
def guardar_imagen_producto(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Imagen_Producto,
    db: Session = Depends(abrir_puerta_bd),
    id_empresa: int = Depends(obtener_empresa),
):
    return service.guardar_imagen_service(json, id, id_empresa, db)


@router.get("/{id}/imagen")
def consultar_imagen_producto(
    id: Annotated[int, Path(gt=0)],
    db: Session = Depends(abrir_puerta_bd),
    id_empresa: int = Depends(obtener_empresa),
    id_sucursal: int | None = Depends(obtener_sucursal_catalogo),
):
    archivo = service.consultar_imagen_service(id, id_empresa, db, id_sucursal)
    return FileResponse(
        archivo,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.get("/{id}", response_model=NuevoProductoRespuesta)
def ver_producto(
    id: Annotated[int, Path(gt=0)],
    id_empresa: int = Depends(obtener_empresa),
    id_sucursal: int | None = Depends(obtener_sucursal_catalogo),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.ver_producto_service(id, id_empresa, db, id_sucursal)


@router.patch("/{id}", response_model=NuevoProductoRespuesta)
def editar_producto(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Editar_Producto,
    id_empresa: int = Depends(obtener_empresa),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.editar_producto_service(json, id, id_empresa, db)


@router.post("/{id}/desactivar", response_model=NuevoProductoRespuesta)
def desactivar_producto(
    id: Annotated[int, Path(gt=0)],
    id_empresa: int = Depends(obtener_empresa),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.desactivar_producto_service(id, id_empresa, db)
