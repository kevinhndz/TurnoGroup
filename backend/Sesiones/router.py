from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from backend.Sesiones.repository import SesionRepository
from backend.Sesiones.schema import (
    RespuestaSesion,
    Revisar_Json_Iniciar_Sesion,
    Revisar_Json_Seleccionar_Contexto,
)
from backend.Sesiones.service import SesionService as service
from core.config import revision
from database.almacen import abrir_puerta_bd
from utils.autorizacion import obtener_sesion, revisar_solicitud_sesion

router = APIRouter(
    prefix="/sesiones",
    tags=["Sesiones"],
    dependencies=[Depends(revisar_solicitud_sesion)],
)


def poner_cookie(response, token, vencimiento):
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    segundos = max(0, int((vencimiento - ahora).total_seconds()))
    response.set_cookie(
        "sesion_turnogroup",
        token,
        httponly=True,
        secure=revision.COOKIE_SEGURA,
        samesite="lax",
        max_age=segundos,
        path="/",
    )
    response.headers["Cache-Control"] = "no-store"


def quitar_cookie(response):
    response.delete_cookie(
        "sesion_turnogroup",
        path="/",
        secure=revision.COOKIE_SEGURA,
        httponly=True,
        samesite="lax",
    )
    response.headers["Cache-Control"] = "no-store"


@router.post("/iniciar", response_model=RespuestaSesion)
def iniciar_sesion(
    json: Revisar_Json_Iniciar_Sesion,
    request: Request,
    response: Response,
    db: Session = Depends(abrir_puerta_bd),
):
    sesion, usuario, token = service.iniciar_sesion_service(json, db)
    request.state.sesion_validada = (sesion, usuario)
    poner_cookie(response, token, sesion.vencimiento)

    return service.respuesta_sesion_service(sesion, usuario, db)


@router.get("/actual", response_model=RespuestaSesion)
def consultar_sesion(
    response: Response,
    sesion=Depends(obtener_sesion),
    db: Session = Depends(abrir_puerta_bd),
):
    response.headers["Cache-Control"] = "no-store"

    return service.respuesta_sesion_service(sesion[0], sesion[1], db)


@router.post("/renovar", response_model=RespuestaSesion)
def renovar_sesion(
    response: Response,
    sesion=Depends(obtener_sesion),
    db: Session = Depends(abrir_puerta_bd),
):
    token = service.renovar_sesion_service(sesion[0], db)
    poner_cookie(response, token, sesion[0].vencimiento)

    return service.respuesta_sesion_service(sesion[0], sesion[1], db)


@router.post("/cerrar", status_code=204)
def cerrar_sesion(request: Request, db: Session = Depends(abrir_puerta_bd)):
    service.cerrar_sesion_service(request.cookies.get("sesion_turnogroup"), db)
    response = Response(status_code=204)
    quitar_cookie(response)

    return response


@router.post("/revocar-todas", status_code=204)
def revocar_sesiones(
    sesion=Depends(obtener_sesion), db: Session = Depends(abrir_puerta_bd)
):
    service.revocar_sesiones_service(sesion[1].id, db)
    response = Response(status_code=204)
    quitar_cookie(response)

    return response


@router.patch("/contexto", response_model=RespuestaSesion)
def seleccionar_contexto(
    json: Revisar_Json_Seleccionar_Contexto,
    response: Response,
    sesion=Depends(obtener_sesion),
    db: Session = Depends(abrir_puerta_bd),
):
    token = service.seleccionar_contexto_service(json, sesion[0], sesion[1], db)
    poner_cookie(response, token, sesion[0].vencimiento)

    return service.respuesta_sesion_service(sesion[0], sesion[1], db)


@router.get("/vinculos")
def consultar_mis_vinculos(
    sesion=Depends(obtener_sesion), db: Session = Depends(abrir_puerta_bd)
):
    vinculos = SesionRepository.listar_vinculos_usuario(db, sesion[1].id)

    elementos = []

    for vinculo_actual in vinculos:
        elementos.append(vinculo_actual.id_empresa)
    empresas = dict(SesionRepository.listar_nombres_empresas(db, elementos))
    elementos_2 = []

    for vinculo_actual_2 in vinculos:
        elementos_3 = []

        for sucursal_actual in SesionRepository.listar_sucursales_autorizadas(
            db, vinculo_actual_2
        ):
            elementos_3.append(
                {
                    "id": sucursal_actual.id,
                    "nombre": sucursal_actual.nombre,
                    "direccion": sucursal_actual.direccion,
                }
            )
        elementos_2.append(
            {
                "id": vinculo_actual_2.id,
                "id_empresa": vinculo_actual_2.id_empresa,
                "nombre_empresa": empresas.get(vinculo_actual_2.id_empresa),
                "rol": vinculo_actual_2.rol,
                "sucursales": elementos_3,
            }
        )

    return elementos_2
