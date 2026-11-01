from fastapi import APIRouter, Depends, Query
from core.listados import filtros_listado
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from utils.autorizacion import obtener_contexto
from backend.Bitacora.service import BitacoraService as service
from backend.Bitacora.schema import RespuestaBitacora
from core.schema import RespuestaPaginada

router = APIRouter(prefix="/bitacora", tags=["Bitacora"])


@router.get("/", response_model=RespuestaPaginada[RespuestaBitacora])
def listar(
    filtros=Depends(filtros_listado),
    solo_sucursal: bool = True,
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.listar_service(db, contexto, pagina_actual, limite, solo_sucursal, filtros)
