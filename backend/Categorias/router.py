from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
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
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.listar_categorias_service(pagina_actual, limite, db)


@router.get("/{id}", response_model=NuevaCategoriaRespuesta)
def ver_categoria(id: int, db: Session = Depends(abrir_puerta_bd)):
    return service.ver_categoria_service(id, db)


@router.patch("/{id}", response_model=NuevaCategoriaRespuesta)
def editar_categoria(id: int, json: Revisar_Json_Editar_Categoria, db: Session = Depends(abrir_puerta_bd)):
    return service.editar_categoria_service(json, id, db)


@router.post("/{id}/desactivar", response_model=NuevaCategoriaRespuesta)
def desactivar_categoria(id: int, db: Session = Depends(abrir_puerta_bd)):
    return service.desactivar_categoria_service(id, db)
