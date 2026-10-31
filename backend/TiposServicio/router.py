from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.TiposServicio.schema import RespuestaTipoServicio
from backend.TiposServicio.service import TipoServicioService as service
from core.schema import RespuestaPaginada


router = APIRouter(prefix="/tipos-servicio", tags=["TiposServicio"])


@router.get("/", response_model=RespuestaPaginada[RespuestaTipoServicio])
def ver_tipos_servicio(
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.listar_tipos_servicio_service(pagina_actual, limite, db)


@router.get("/{id}", response_model=RespuestaTipoServicio)
def ver_tipo_servicio(id: Annotated[int, Path(gt=0)], db: Session = Depends(abrir_puerta_bd)):
    return service.ver_tipo_servicio_service(id, db)
