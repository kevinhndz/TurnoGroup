from uuid import UUID
from typing import Literal
from fastapi import APIRouter, Depends, Query, Path
from typing import Annotated
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from utils.autorizacion import obtener_contexto
from backend.Pedidos.schema import (
    Revisar_Json_Pedido,
    Revisar_Json_Crear_Pedido,
    Revisar_Json_Cobrar_Pedido,
    Revisar_Json_Cancelar_Pedido,
)
from backend.Pedidos.service import PedidoService as service

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.get("/operaciones/{clave_operacion}")
def consultar_operacion(
    clave_operacion: UUID,
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.consultar_operacion_service(clave_operacion, db, contexto)


@router.get("/mesas")
def disponibilidad_mesas(
    id_pedido: int | None = Query(None, gt=0),
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    if id_pedido:
        service.ver_service(id_pedido, db, contexto)
    return service.mesas_service(db, contexto, id_pedido)


@router.get("/catalogo")
def catalogo(
    contexto=Depends(obtener_contexto), db: Session = Depends(abrir_puerta_bd)
):
    return service.catalogo_service(db, contexto)


@router.post("/cotizar")
def cotizar(
    json: Revisar_Json_Pedido,
    id_pedido: int | None = Query(None, gt=0),
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    if id_pedido is not None:
        service.ver_service(id_pedido, db, contexto)
    return service.calcular_service(json, db, contexto, id_pedido)


@router.post("/", status_code=201)
def crear(
    json: Revisar_Json_Crear_Pedido,
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.crear_service(json, db, contexto)


@router.get("/")
def listar(
    estado: Literal["Abierto", "Cerrado", "Cancelado"] | None = None,
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.listar_service(db, contexto, pagina_actual, limite, estado)


@router.get("/{id}")
def ver(
    id: Annotated[int, Path(gt=0)],
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.ver_service(id, db, contexto)


@router.patch("/{id}")
def editar(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Pedido,
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.editar_service(id, json, db, contexto)


@router.post("/{id}/cobrar")
def cobrar(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Cobrar_Pedido,
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.accion_service(id, "cobrar", json, db, contexto)


@router.post("/{id}/entregar")
def entregar(
    id: Annotated[int, Path(gt=0)],
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.accion_service(id, "entregar", None, db, contexto)


@router.post("/{id}/cancelar")
def cancelar(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Cancelar_Pedido,
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.accion_service(id, "cancelar", json, db, contexto)
