from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, HTTPException, Response
from utils.autorizacion import obtener_sesion, revisar_solicitud_sesion
from sqlalchemy.orm import Session
from database.almacen import abrir_puerta_bd
from backend.Usuarios.schema import (
    NuevoUsuarioRespuesta,
    Revisar_Json_Rol_Plataforma,
    Revisar_Json_Editar_Usuario,
    Revisar_Json_Nuevo_Usuario,
)
from backend.Usuarios.service import UsuarioService as service
from backend.Usuarios.schema import Revisar_Json_Registro_Negocio
from backend.Sesiones.schema import RespuestaSesion
from core.schema import RespuestaPaginada


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)


@router.post("/", response_model=NuevoUsuarioRespuesta, status_code=201,
             dependencies=[Depends(revisar_solicitud_sesion)])
def crear_usuario(json: Revisar_Json_Nuevo_Usuario, db: Session = Depends(abrir_puerta_bd)):
    return service.crear_usuario_service(json, db)


@router.get("/", response_model=RespuestaPaginada[NuevoUsuarioRespuesta])
def ver_usuarios(
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd)
):
    return service.listar_usuarios_service(pagina_actual, limite, db)


@router.get("/{id}", response_model=NuevoUsuarioRespuesta)
def ver_usuario(id: Annotated[int, Path(gt=0)], db: Session = Depends(abrir_puerta_bd)):
    return service.ver_usuario_service(id, db)


@router.patch("/{id}", response_model=NuevoUsuarioRespuesta)
def editar_usuario(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Editar_Usuario,
    db: Session = Depends(abrir_puerta_bd),
    sesion=Depends(obtener_sesion)
):
    if sesion[1].id != id and sesion[1].rol_plataforma != "Superadministrador":
        raise HTTPException(403, "Solo puedes editar tu propio perfil")
    if "estado" in json.model_fields_set and sesion[1].rol_plataforma != "Superadministrador":
        raise HTTPException(403, "El estado requiere permisos de administracion")
    return service.editar_usuario_service(json, id, db)


@router.post("/{id}/desactivar", response_model=NuevoUsuarioRespuesta)
def desactivar_usuario(
    id: Annotated[int, Path(gt=0)], db: Session = Depends(abrir_puerta_bd),
    sesion=Depends(obtener_sesion)
):
    if sesion[1].id != id and sesion[1].rol_plataforma != "Superadministrador":
        raise HTTPException(403, "Solo puedes desactivar tu propio perfil")
    return service.desactivar_usuario_service(id, db)


@router.patch("/{id}/rol-plataforma", response_model=NuevoUsuarioRespuesta)
def cambiar_rol_plataforma(id: Annotated[int, Path(gt=0)], json: Revisar_Json_Rol_Plataforma,
                           db: Session = Depends(abrir_puerta_bd)):
    return service.cambiar_rol_plataforma_service(json, id, db)


@router.post("/registro-negocio", status_code=201, response_model=RespuestaSesion)
def completar_registro_negocio(json: Revisar_Json_Registro_Negocio,
                               response: Response,
                               db: Session = Depends(abrir_puerta_bd)):
    from backend.Sesiones.router import poner_cookie
    respuesta, token, vencimiento = service.registrar_negocio_service(json, db)
    poner_cookie(response, token, vencimiento)
    return respuesta
