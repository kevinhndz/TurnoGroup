from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.Sesiones.schema import (
    Revisar_Json_Iniciar_Sesion,
    RespuestaSesion,
    Revisar_Json_Seleccionar_Contexto,
)
from backend.Sesiones.service import SesionService as service
from core.config import revision
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
    response: Response,
    db: Session = Depends(abrir_puerta_bd),
):
    sesion, usuario, token = service.iniciar_sesion_service(json, db)
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
    from backend.Sesiones.repository import SesionRepository

    vinculos = SesionRepository.listar_vinculos_usuario(db, sesion[1].id)
    from backend.Empresas.tabla import Empresas

    empresas = dict(
        db.query(Empresas.id, Empresas.nombre)
        .filter(Empresas.id.in_([vinculo.id_empresa for vinculo in vinculos]))
        .all()
    )
    return [
        {
            "id": vinculo.id,
            "id_empresa": vinculo.id_empresa,
            "nombre_empresa": empresas.get(vinculo.id_empresa),
            "rol": vinculo.rol,
            "sucursales": [
                {"id": sucursal.id, "nombre": sucursal.nombre, "direccion": sucursal.direccion}
                for sucursal in SesionRepository.listar_sucursales_autorizadas(
                    db, vinculo
                )
            ],
        }
        for vinculo in vinculos
    ]
