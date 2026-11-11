from decimal import Decimal
from uuid import UUID
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Revisar_Json_Detalle_Pedido(BaseModel):
    id_producto: int = Field(gt=0)
    cantidad: int = Field(ge=1, le=99)
    nota: str | None = Field(default=None, max_length=300)
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Revisar_Json_Pedido(BaseModel):
    id_tipo_servicio: int = Field(gt=0)
    id_metodo_pago: int = Field(gt=0)
    id_mesa: int | None = Field(default=None, gt=0)
    id_descuento: int | None = Field(default=None, gt=0)
    cliente: str = Field(min_length=1, max_length=100)
    telefono: str = Field(min_length=1, max_length=30)
    direccion: str | None = Field(default=None, max_length=500)
    nota: str | None = Field(default=None, max_length=1000)
    detalles: list[Revisar_Json_Detalle_Pedido] = Field(min_length=1, max_length=100)
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Revisar_Json_Crear_Pedido(Revisar_Json_Pedido):
    clave_operacion: UUID
    cobrado: bool = False
    total_esperado: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )


class Revisar_Json_Cobrar_Pedido(BaseModel):
    id_metodo_pago: int = Field(gt=0)
    model_config = ConfigDict(extra="forbid")


class Revisar_Json_Cancelar_Pedido(BaseModel):
    motivo: str = Field(min_length=3, max_length=500)
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
