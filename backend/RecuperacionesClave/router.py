from fastapi import APIRouter, BackgroundTasks, Depends, Response
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.RecuperacionesClave.schema import Revisar_Json_Solicitar_Recuperacion, Revisar_Json_Recuperar_Clave
from backend.RecuperacionesClave.service import RecuperacionClaveService as service
from backend.Sesiones.schema import RespuestaMensaje
from backend.Sesiones.router import quitar_cookie
from utils.autorizacion import revisar_solicitud_sesion

router = APIRouter(prefix="/recuperaciones-clave", tags=["Recuperacion de clave"],
                   dependencies=[Depends(revisar_solicitud_sesion)])


@router.post("/solicitar", response_model=RespuestaMensaje, status_code=202)
def solicitar_recuperacion(json: Revisar_Json_Solicitar_Recuperacion, tareas: BackgroundTasks,
                           response: Response, db: Session = Depends(abrir_puerta_bd)):
    response.headers["Cache-Control"] = "no-store"
    return service.solicitar_recuperacion_service(json, tareas, db)


@router.post("/restablecer", response_model=RespuestaMensaje)
def recuperar_clave(json: Revisar_Json_Recuperar_Clave, response: Response,
                    db: Session = Depends(abrir_puerta_bd)):
    resultado = service.recuperar_clave_service(json, db)
    quitar_cookie(response)
    return resultado
