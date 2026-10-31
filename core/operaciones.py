from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException


def ahora():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def moneda(valor):
    return Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def exigir(condicion, mensaje, estado=422):
    if not condicion:
        raise HTTPException(estado, mensaje)


def alcance(contexto):
    exigir(
        contexto["id_empresa"] and contexto["id_sucursal"],
        "Selecciona una sucursal autorizada",
        403,
    )
    return contexto["id_empresa"], contexto["id_sucursal"]


def paginar(consulta, pagina, limite, convertir):
    total = consulta.count()
    filas = consulta.offset((pagina - 1) * limite).limit(limite).all()
    return {
        "total": total,
        "pagina_actual": pagina,
        "limite": limite,
        "total_paginas": (total + limite - 1) // limite,
        "data": [convertir(item) for item in filas],
    }
