from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class Revisar_Json_Crear_Disponibilidad_Producto(BaseModel):
    id_producto: int = Field(gt=0)
    disponible: bool = True
    precio_especial: Optional[Decimal] = Field(default=None, ge=0, max_digits=12, decimal_places=2)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class Revisar_Json_Editar_Disponibilidad_Producto(BaseModel):
    disponible: Optional[bool] = None
    precio_especial: Optional[Decimal] = Field(default=None, ge=0, max_digits=12, decimal_places=2)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class RespuestaDisponibilidadProducto(BaseModel):
    id_producto: int
    id_sucursal: int
    disponible: bool
    precio_especial: Optional[Decimal]

    model_config = ConfigDict(from_attributes=True)
