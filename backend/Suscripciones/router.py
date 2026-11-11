from fastapi import APIRouter, Depends, Response, Path
from typing import Annotated
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from utils.autorizacion import obtener_empresa, obtener_contexto
from backend.Suscripciones.schema import Revisar_Json_Desactivar_Cuenta
from backend.Suscripciones.schema import Revisar_Json_Plan, Revisar_Json_Tarjeta_Suscripcion, Revisar_Json_Renovacion
from backend.Suscripciones.service import SuscripcionService as service

router = APIRouter(prefix="/suscripciones", tags=["Suscripciones"])


@router.post("/desactivar-cuenta", status_code=204)
def desactivar_cuenta(json: Revisar_Json_Desactivar_Cuenta, contexto=Depends(obtener_contexto), db: Session = Depends(abrir_puerta_bd)):
    from backend.Sesiones.router import quitar_cookie
    service.desactivar_cuenta_service(json, db, contexto)
    respuesta = Response(status_code=204)
    quitar_cookie(respuesta)
    return respuesta


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


@router.post("/tarjetas", status_code=201)
def agregar_tarjeta(json: Revisar_Json_Tarjeta_Suscripcion, id_empresa=Depends(obtener_empresa), db: Session = Depends(abrir_puerta_bd)):
    return service.agregar_tarjeta_service(json, db, id_empresa)


@router.post("/tarjetas/{id}/principal")
def tarjeta_principal(id: Annotated[int, Path(gt=0)], id_empresa=Depends(obtener_empresa), db: Session = Depends(abrir_puerta_bd)):
    return service.prioridad_service(id, "Principal", db, id_empresa)


@router.post("/tarjetas/{id}/secundaria")
def tarjeta_secundaria(id: Annotated[int, Path(gt=0)], id_empresa=Depends(obtener_empresa), db: Session = Depends(abrir_puerta_bd)):
    return service.prioridad_service(id, "Secundaria", db, id_empresa)


@router.delete("/tarjetas/{id}", status_code=204)
def retirar_tarjeta(id: Annotated[int, Path(gt=0)], id_empresa=Depends(obtener_empresa), db: Session = Depends(abrir_puerta_bd)):
    service.retirar_tarjeta_service(id, db, id_empresa)


@router.patch("/renovacion")
def renovacion(json: Revisar_Json_Renovacion, id_empresa=Depends(obtener_empresa), db: Session = Depends(abrir_puerta_bd)):
    return service.renovacion_service(json, db, id_empresa)


@router.post("/comprobantes/registro", status_code=201)
def comprobante_registro(id_empresa=Depends(obtener_empresa), db: Session = Depends(abrir_puerta_bd)):
    return service.crear_comprobante_registro(db, id_empresa)


@router.get("/comprobantes/excel")
def exportar_excel(id_empresa=Depends(obtener_empresa), db: Session = Depends(abrir_puerta_bd)):
    from backend.Suscripciones.repository import SuscripcionRepository as repo
    from backend.Suscripciones.comprobantes import crear_excel
    return Response(crear_excel(repo.comprobantes(db, id_empresa)), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": 'attachment; filename="comprobantes-prueba.xlsx"'})


@router.get("/comprobantes/{id}/pdf")
def exportar_pdf(id: Annotated[int, Path(gt=0)], id_empresa=Depends(obtener_empresa), db: Session = Depends(abrir_puerta_bd)):
    from backend.Suscripciones.repository import SuscripcionRepository as repo
    from backend.Suscripciones.comprobantes import crear_pdf
    from core.operaciones import exigir
    look_up = repo.buscar_comprobante(db, id_empresa, id)
    exigir(look_up is not None, "No se encontro el comprobante", 404)
    return Response(crear_pdf(look_up), media_type="application/pdf", headers={"Content-Disposition": f'inline; filename="comprobante-prueba-{id}.pdf"'})
