from datetime import date
from typing import Literal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from utils.autorizacion import obtener_contexto
from backend.Finanzas.service import FinanzasService as service

router = APIRouter(prefix="/finanzas", tags=["Finanzas"])


@router.get("/ventas")
def ventas(
    desde: date,
    hasta: date,
    periodo: Literal["dia", "semana", "mes", "anio"] = "dia",
    solo_sucursal: bool = True,
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.resumen_service(db, contexto, desde, hasta, periodo, solo_sucursal)
