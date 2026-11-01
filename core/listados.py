from typing import Literal
from fastapi import Query
from sqlalchemy import String, cast, func, or_


def filtros_listado(
    busqueda: str = Query("", max_length=100),
    orden: Literal["recientes", "antiguos", "nombre_asc", "nombre_desc"] = "recientes",
):
    return {"busqueda": busqueda.strip(), "orden": orden}


def filtrar_listado(consulta, modelo, filtros=None, columnas=None):
    if not filtros:
        return consulta
    texto = filtros.get("busqueda", "").strip()
    campos = columnas if columnas is not None else [
        getattr(modelo, nombre) for nombre in ("nombre", "correo", "cliente", "telefono", "direccion", "recurso", "accion")
        if hasattr(modelo, nombre)
    ]
    if texto:
        numero = texto.upper().removeprefix("#").removeprefix("TG-")
        condiciones = [func.lower(campo).contains(texto.lower(), autoescape=True) for campo in campos]
        if hasattr(modelo, "id") and numero.isdigit():
            condiciones.append(cast(modelo.id, String) == numero)
        consulta = consulta.filter(or_(*condiciones))
    orden = filtros.get("orden", "recientes")
    fecha = next((getattr(modelo, nombre) for nombre in ("created_at", "fecha_registro", "fecha_creacion", "inicio", "fecha", "id") if hasattr(modelo, nombre)), modelo.id)
    campo = campos[0] if orden.startswith("nombre") and campos else fecha
    descendente = orden in ("recientes", "nombre_desc")
    return consulta.order_by(None).order_by(campo.desc() if descendente else campo.asc(), modelo.id.desc() if descendente else modelo.id.asc())


def pagina_listado(consulta, modelo, pagina_actual, limite, filtros=None, columnas=None):
    consulta = filtrar_listado(consulta, modelo, filtros, columnas)
    return consulta.count(), consulta.offset((pagina_actual - 1) * limite).limit(limite).all()
