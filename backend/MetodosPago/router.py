from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.MetodosPago.schema import RespuestaMetodoPago
from backend.MetodosPago.service import MetodoPagoService as service
from core.schema import RespuestaPaginada


router = APIRouter(prefix="/metodos-pago", tags=["MetodosPago"])


@router.get("/", response_model=RespuestaPaginada[RespuestaMetodoPago])
def ver_metodos_pago(
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.listar_metodos_pago_service(pagina_actual, limite, db)


@router.get("/{id}", response_model=RespuestaMetodoPago)
def ver_metodo_pago(id: Annotated[int, Path(gt=0)], db: Session = Depends(abrir_puerta_bd)):
    return service.ver_metodo_pago_service(id, db)
