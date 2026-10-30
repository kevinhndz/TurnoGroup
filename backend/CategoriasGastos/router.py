from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.CategoriasGastos.schema import (
    RespuestaCategoriaGasto,
    Revisar_Json_Crear_Categoria_Gasto,
    Revisar_Json_Editar_Categoria_Gasto,
)
from backend.CategoriasGastos.service import CategoriaGastoService as service
from core.schema import RespuestaPaginada


router = APIRouter(
    prefix="/categorias-gastos",
    tags=["Categorias de gastos"]
)


@router.post("/", response_model=RespuestaCategoriaGasto, status_code=201)
def crear_categoria_gasto(json: Revisar_Json_Crear_Categoria_Gasto, db: Session = Depends(abrir_puerta_bd)):
    return service.crear_categoria_gasto_service(json, db)


@router.get("/", response_model=RespuestaPaginada[RespuestaCategoriaGasto])
def ver_categorias_gastos(
    id_empresa: int = Query(..., gt=0),
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.listar_categorias_gastos_service(id_empresa, pagina_actual, limite, db)


@router.get("/{id}", response_model=RespuestaCategoriaGasto)
def ver_categoria_gasto(
    id: Annotated[int, Path(gt=0)],
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.ver_categoria_gasto_service(id, id_empresa, db)


@router.patch("/{id}", response_model=RespuestaCategoriaGasto)
def editar_categoria_gasto(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Editar_Categoria_Gasto,
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.editar_categoria_gasto_service(json, id, id_empresa, db)


@router.post("/{id}/desactivar", response_model=RespuestaCategoriaGasto)
def desactivar_categoria_gasto(
    id: Annotated[int, Path(gt=0)],
    id_empresa: int = Query(..., gt=0),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.desactivar_categoria_gasto_service(id, id_empresa, db)
