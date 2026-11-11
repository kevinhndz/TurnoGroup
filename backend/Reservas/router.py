from typing import Literal
from core.listados import filtros_listado
from fastapi import APIRouter, Depends, Query, Path
from typing import Annotated
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from utils.autorizacion import obtener_contexto
from backend.Reservas.schema import Revisar_Json_Crear_Reserva
from backend.Reservas.service import ReservaService as service

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.get("/")
def listar(
    filtros=Depends(filtros_listado),
    estado: Literal["Confirmada", "Atendida", "Cancelada"] | None = None,
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.listar_service(db, contexto, pagina_actual, limite, estado, filtros)


@router.get("/{id}")
def ver(
    id: Annotated[int, Path(gt=0)],
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.ver_service(id, db, contexto)


@router.post("/", status_code=201)
def crear(
    json: Revisar_Json_Crear_Reserva,
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.guardar_service(json, db, contexto)


@router.patch("/{id}")
def editar(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Crear_Reserva,
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.guardar_service(json, db, contexto, id)


@router.post("/{id}/cancelar")
def cancelar(
    id: Annotated[int, Path(gt=0)],
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.accion_service(id, "Cancelada", db, contexto)


@router.post("/{id}/atender")
def atender(
    id: Annotated[int, Path(gt=0)],
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.accion_service(id, "Atendida", db, contexto)
