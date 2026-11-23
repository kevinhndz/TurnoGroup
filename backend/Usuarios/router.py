from core.listados import filtros_listado
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
    Revisar_Json_Registro_Negocio,
)
from backend.Usuarios.service import UsuarioService as service
from backend.Usuarios.codigos_mfa import CodigosRecuperacionMfa
from backend.Sesiones.schema import RespuestaSesion
from core.schema import RespuestaPaginada

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post(
    "/",
    response_model=NuevoUsuarioRespuesta,
    status_code=201,
    dependencies=[Depends(revisar_solicitud_sesion)],
)
def crear_usuario(
    json: Revisar_Json_Nuevo_Usuario, db: Session = Depends(abrir_puerta_bd)
):
    return service.crear_usuario_service(json, db)


@router.get("/", response_model=RespuestaPaginada[NuevoUsuarioRespuesta])
def ver_usuarios(
    pagina_actual: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    db: Session = Depends(abrir_puerta_bd),
    filtros=Depends(filtros_listado),
):
    return service.listar_usuarios_service(pagina_actual, limite, db, filtros=filtros)


@router.get("/{id}", response_model=NuevoUsuarioRespuesta)
def ver_usuario(id: Annotated[int, Path(gt=0)], db: Session = Depends(abrir_puerta_bd)):
    return service.ver_usuario_service(id, db)


@router.patch("/{id}", response_model=NuevoUsuarioRespuesta)
def editar_usuario(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Editar_Usuario,
    db: Session = Depends(abrir_puerta_bd),
    sesion=Depends(obtener_sesion),
):
    if sesion[1].id != id and sesion[1].rol_plataforma != "Superadministrador":
        raise HTTPException(403, "Solo puedes editar tu propio perfil")
    if (
        "estado" in json.model_fields_set
        and sesion[1].rol_plataforma != "Superadministrador"
    ):
        raise HTTPException(403, "El estado requiere permisos de administracion")
    return service.editar_usuario_service(json, id, db)


@router.post("/{id}/desactivar", response_model=NuevoUsuarioRespuesta)
def desactivar_usuario(
    id: Annotated[int, Path(gt=0)],
    db: Session = Depends(abrir_puerta_bd),
    sesion=Depends(obtener_sesion),
):
    if sesion[1].id != id and sesion[1].rol_plataforma != "Superadministrador":
        raise HTTPException(403, "Solo puedes desactivar tu propio perfil")
    return service.desactivar_usuario_service(id, db)


@router.patch("/{id}/rol-plataforma", response_model=NuevoUsuarioRespuesta)
def cambiar_rol_plataforma(
    id: Annotated[int, Path(gt=0)],
    json: Revisar_Json_Rol_Plataforma,
    db: Session = Depends(abrir_puerta_bd),
):
    return service.cambiar_rol_plataforma_service(json, id, db)


@router.post("/registro-negocio", status_code=201, response_model=RespuestaSesion)
def completar_registro_negocio(
    json: Revisar_Json_Registro_Negocio,
    response: Response,
    db: Session = Depends(abrir_puerta_bd),
):
    from backend.Sesiones.router import poner_cookie

    respuesta, token, vencimiento = service.registrar_negocio_service(json, db)
    # Guardo el token solo en la cookie para que JavaScript no pueda leerlo.
    poner_cookie(response, token, vencimiento)
    return respuesta


from fastapi import BackgroundTasks
from backend.Usuarios.schema import SolicitarCambioCorreo, ConfirmarCambioCorreo
from backend.Usuarios.seguridad import SeguridadUsuarioService
from backend.Sesiones.router import quitar_cookie


@router.post("/{id}/correo/solicitar", status_code=202)
def solicitar_cambio_correo(
    id: int,
    json: SolicitarCambioCorreo,
    tareas: BackgroundTasks,
    sesion=Depends(obtener_sesion),
    db: Session = Depends(abrir_puerta_bd),
):
    if sesion[1].id != id:
        raise HTTPException(403, "Solo puedes cambiar tu propio correo")
    return SeguridadUsuarioService.solicitar(json, id, db, tareas)


@router.post("/{id}/correo/confirmar")
def confirmar_cambio_correo(
    id: int,
    json: ConfirmarCambioCorreo,
    tareas: BackgroundTasks,
    response: Response,
    sesion=Depends(obtener_sesion),
    db: Session = Depends(abrir_puerta_bd),
):
    if sesion[1].id != id:
        raise HTTPException(403, "Solo puedes cambiar tu propio correo")
    resultado = SeguridadUsuarioService.confirmar(json, id, db, tareas)
    quitar_cookie(response)
    return resultado


from backend.Usuarios.schema import (
    SolicitarVerificacionCorreo,
    ConfirmarVerificacionCorreo,
)
from backend.Usuarios.verificacion import VerificacionCorreoService


@router.post("/verificacion/solicitar", status_code=202)
def solicitar_verificacion(
    json: SolicitarVerificacionCorreo,
    tareas: BackgroundTasks,
    db: Session = Depends(abrir_puerta_bd),
):
    return VerificacionCorreoService.solicitar(json, db, tareas)


@router.post("/verificacion/confirmar")
def confirmar_verificacion(
    json: ConfirmarVerificacionCorreo, db: Session = Depends(abrir_puerta_bd)
):
    return VerificacionCorreoService.confirmar(json, db)
