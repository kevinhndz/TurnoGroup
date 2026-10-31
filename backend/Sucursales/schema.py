from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class Revisar_Json_Crear_Sucursal(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    direccion: str = Field(min_length=5, max_length=255)
    telefono: Optional[str] = Field(default=None, min_length=8, max_length=20)
    es_principal: bool = False

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class Revisar_Json_Editar_Sucursal(BaseModel):
    activo: Optional[bool] = None
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    direccion: Optional[str] = Field(default=None, min_length=5, max_length=255)
    telefono: Optional[str] = Field(default=None, min_length=8, max_length=20)
    es_principal: Optional[bool] = None

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class RespuestaSucursalCreada(Revisar_Json_Crear_Sucursal):
    id_empresa: int
    id: int
    activo: bool

    model_config = ConfigDict(from_attributes=True)


class RespuestaSucursalEditada(RespuestaSucursalCreada):
    pass
