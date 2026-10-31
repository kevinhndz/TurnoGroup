from fastapi import APIRouter, Depends, Query, Path
from typing import Annotated
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from utils.autorizacion import obtener_contexto
from backend.Cajas.schema import Revisar_Json_Abrir_Caja, Revisar_Json_Cerrar_Caja
from backend.Cajas.service import CajaService as service

router = APIRouter(prefix="/cajas", tags=["Cajas"])


@router.get("/actual")
def actual(contexto=Depends(obtener_contexto), db: Session = Depends(abrir_puerta_bd)):
    return service.actual_service(db, contexto)


@router.get("/")
def listar(
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.listar_service(db, contexto, pagina_actual, limite)


@router.post("/", status_code=201)
def abrir(
    json: Revisar_Json_Abrir_Caja,
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.abrir_service(json, db, contexto)


@router.post("/{id}/cerrar")
def cerrar(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Cerrar_Caja,
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.cerrar_service(id, json, db, contexto)
