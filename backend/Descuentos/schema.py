from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field


class Revisar_Json_Crear_Descuento(BaseModel):
    id_empresa: int = Field(gt=0)
    nombre: str = Field(min_length=1, max_length=100)
    tipo_descuento: Literal["Porcentaje", "CantidadFija"]
    valor: Decimal = Field(ge=0, max_digits=12, decimal_places=2)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class Revisar_Json_Editar_Descuento(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    tipo_descuento: Optional[Literal["Porcentaje", "CantidadFija"]] = None
    valor: Optional[Decimal] = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    activo: Optional[bool] = None

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class RespuestaDescuento(BaseModel):
    id: int
    id_empresa: int
    nombre: str
    tipo_descuento: Literal["Porcentaje", "CantidadFija"]
    valor: Decimal
    activo: bool

    model_config = ConfigDict(from_attributes=True)
