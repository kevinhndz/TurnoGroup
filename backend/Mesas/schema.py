from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class Revisar_Json_Crear_Mesa(BaseModel):
    nombre: str = Field(min_length=1, max_length=60)
    capacidad: Optional[int] = Field(default=None, gt=0)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class Revisar_Json_Editar_Mesa(BaseModel):
    activo: Optional[bool] = None
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=60)
    capacidad: Optional[int] = Field(default=None, gt=0)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class RespuestaMesa(BaseModel):
    id: int
    id_sucursal: int
    nombre: str
    capacidad: Optional[int]
    activo: bool

    model_config = ConfigDict(from_attributes=True)
