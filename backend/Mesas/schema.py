from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class Revisar_Json_Crear_Mesa(BaseModel):
    id_sucursal: int = Field(gt=0)
    nombre: str = Field(min_length=1, max_length=60)
    capacidad: Optional[int] = Field(default=None, gt=0)

    model_config = ConfigDict(str_strip_whitespace=True)


class Revisar_Json_Editar_Mesa(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=60)
    capacidad: Optional[int] = Field(default=None, gt=0)

    model_config = ConfigDict(str_strip_whitespace=True)


class RespuestaMesa(BaseModel):
    id: int
    id_sucursal: int
    nombre: str
    capacidad: Optional[int]
    activo: bool

    model_config = ConfigDict(from_attributes=True)
