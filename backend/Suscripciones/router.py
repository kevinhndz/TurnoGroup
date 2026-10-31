from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from utils.autorizacion import obtener_empresa
from backend.Suscripciones.schema import Revisar_Json_Plan
from backend.Suscripciones.service import SuscripcionService as service

router = APIRouter(prefix="/suscripciones", tags=["Suscripciones"])


@router.get("/actual")
def consultar_suscripcion(
    id_empresa=Depends(obtener_empresa), db: Session = Depends(abrir_puerta_bd)
):
    return service.consultar_service(db, id_empresa)


@router.patch("/plan")
def cambiar_plan(
    json: Revisar_Json_Plan,
    id_empresa=Depends(obtener_empresa),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.cambiar_plan_service(json, db, id_empresa)
