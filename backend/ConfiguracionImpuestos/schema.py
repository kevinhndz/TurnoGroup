from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class Revisar_Json_Crear_Configuracion_Impuestos(BaseModel):
    id_empresa: int = Field(gt=0)
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=80)
    porcentaje: Decimal = Field(ge=0, le=100, max_digits=6, decimal_places=3)
    precios_incluyen_impuesto: bool

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class Revisar_Json_Editar_Configuracion_Impuestos(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=80)
    porcentaje: Optional[Decimal] = Field(default=None, ge=0, le=100, max_digits=6, decimal_places=3)
    precios_incluyen_impuesto: Optional[bool] = None
    activo: Optional[bool] = None

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class RespuestaConfiguracionImpuestos(BaseModel):
    id: int
    id_empresa: int
    nombre: Optional[str]
    porcentaje: Decimal
    precios_incluyen_impuesto: bool
    activo: bool

    model_config = ConfigDict(from_attributes=True)
