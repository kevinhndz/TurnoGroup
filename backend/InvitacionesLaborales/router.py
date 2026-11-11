from fastapi import Response
from backend.Sesiones.schema import RespuestaSesion
from backend.Sesiones.router import poner_cookie
from backend.InvitacionesLaborales.schema import Revisar_Json_Registro_Invitacion
from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks, Path, Query
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from utils.autorizacion import obtener_contexto, obtener_empresa, obtener_sesion
from backend.InvitacionesLaborales.schema import (
    Revisar_Json_Crear_Invitacion_Laboral,
    Revisar_Json_Aceptar_Invitacion_Laboral,
    RespuestaInvitacionLaboral,
)
from backend.InvitacionesLaborales.service import InvitacionLaboralService as service
from backend.VinculosLaborales.schema import RespuestaVinculoLaboral
from core.schema import RespuestaPaginada

router = APIRouter(prefix="/invitaciones-laborales", tags=["Invitaciones laborales"])


@router.post("/", response_model=RespuestaInvitacionLaboral, status_code=201)
def crear_invitacion(
    json: Revisar_Json_Crear_Invitacion_Laboral,
    tareas: BackgroundTasks,
    contexto=Depends(obtener_contexto),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.crear_invitacion_service(json, contexto, tareas, db)


@router.post("/aceptar", response_model=RespuestaVinculoLaboral)
def aceptar_invitacion(
    json: Revisar_Json_Aceptar_Invitacion_Laboral,
    sesion=Depends(obtener_sesion),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.aceptar_invitacion_service(json, sesion[1], db)


@router.get("/", response_model=RespuestaPaginada[RespuestaInvitacionLaboral])
def listar_invitaciones(
    id_empresa: int = Depends(obtener_empresa),
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.listar_invitaciones_service(id_empresa, pagina_actual, limite, db)


@router.get("/{id}", response_model=RespuestaInvitacionLaboral)
def ver_invitacion(
    id: Annotated[int, Path(gt=0)],
    id_empresa: int = Depends(obtener_empresa),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.ver_invitacion_service(id, id_empresa, db)


@router.post("/{id}/revocar", response_model=RespuestaInvitacionLaboral)
def revocar_invitacion(
    id: Annotated[int, Path(gt=0)],
    id_empresa: int = Depends(obtener_empresa),
    db: Session = Depends(abrir_puerta_bd),
):
    return service.revocar_invitacion_service(id, id_empresa, db)


@router.post("/registrar", status_code=201, response_model=RespuestaSesion)
def registrar_invitado(
    json: Revisar_Json_Registro_Invitacion,
    response: Response,
    db: Session = Depends(abrir_puerta_bd),
):
    respuesta, token, vencimiento = service.registrar_invitado_service(json, db)
    poner_cookie(response, token, vencimiento)
    return respuesta
