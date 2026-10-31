from fastapi import Header, Depends
from utils.token import verificar_token
from core.exceptions import AccesoProhibidoError


def el_vigilante(token: str = Header(...)) -> dict:
    return verificar_token(token)


def permiso_admin(json: dict = Depends(el_vigilante)) -> dict:
    if json.get("rol") != "Administrador":
        raise AccesoProhibidoError("No estas autorizado")
    else:
        return json


def permiso_usuario(json: dict = Depends(el_vigilante)) -> dict:
    if json.get("rol") not in ["Mesero", "Cajero", "Administrador"]:
        raise AccesoProhibidoError("No estas autorizado")
    else:
        return json
