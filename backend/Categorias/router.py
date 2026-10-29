from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from typing import Annotated
from database.almacen import abrir_puerta_bd
from backend.Categorias.schema import (
    NuevaCategoriaRespuesta,
    Revisar_Json_Editar_Categoria,
    Revisar_Json_Nueva_Categoria,
)
from backend.Categorias.service import CategoriaService as service
from core.schema import RespuestaPaginada


router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"]
)


@router.post("/", response_model=NuevaCategoriaRespuesta, status_code=201)
def crear_categoria(json: Revisar_Json_Nueva_Categoria, db: Session = Depends(abrir_puerta_bd)):
    return service.crear_categoria_service(json, db)


@router.get("/", response_model=RespuestaPaginada[NuevaCategoriaRespuesta])
def ver_categorias(
    id_empresa: int = Query(..., gt=0),
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.listar_categorias_service(id_empresa, pagina_actual, limite, db)


@router.get("/{id}", response_model=NuevaCategoriaRespuesta)
def ver_categoria(id: Annotated[int, Path(gt=0)], id_empresa: int = Query(..., gt=0), db: Session = Depends(abrir_puerta_bd)):
    return service.ver_categoria_service(id, id_empresa, db)


@router.patch("/{id}", response_model=NuevaCategoriaRespuesta)
def editar_categoria(id: Annotated[int, Path(gt=0)], json: Revisar_Json_Editar_Categoria, id_empresa: int = Query(..., gt=0), db: Session = Depends(abrir_puerta_bd)):
    return service.editar_categoria_service(json, id, id_empresa, db)


@router.post("/{id}/desactivar", response_model=NuevaCategoriaRespuesta)
def desactivar_categoria(id: Annotated[int, Path(gt=0)], id_empresa: int = Query(..., gt=0), db: Session = Depends(abrir_puerta_bd)):
    return service.desactivar_categoria_service(id, id_empresa, db)
