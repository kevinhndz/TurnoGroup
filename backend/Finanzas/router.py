from datetime import date
from typing import Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from utils.autorizacion import obtener_contexto
from backend.Finanzas.service import FinanzasService as service

router = APIRouter(prefix="/finanzas", tags=["Finanzas"])


@router.get("/dashboard")
def dashboard(
    periodo: Literal["dia", "semana", "mes", "anio"] = "mes",
    anio: int | None = Query(None, ge=2000, le=2100),
    solo_sucursal: bool = True,
    desde: date | None = None,
    hasta: date | None = None,
    contexto=Depends(obtener_contexto), db: Session = Depends(abrir_puerta_bd),
):
    return service.dashboard_service(db, contexto, periodo, anio, solo_sucursal, desde, hasta)


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
