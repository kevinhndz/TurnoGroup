from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class Revisar_Json_Crear_Sucursal(BaseModel):
    id_empresa: int = Field(gt=0)
    nombre: str = Field(min_length=2, max_length=100)
    direccion: str = Field(min_length=5, max_length=255)
    telefono: Optional[str] = Field(default=None, min_length=8, max_length=20)
    es_principal: bool = False

    model_config = ConfigDict(str_strip_whitespace=True)


class Revisar_Json_Editar_Sucursal(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    direccion: Optional[str] = Field(default=None, min_length=5, max_length=255)
    telefono: Optional[str] = Field(default=None, min_length=8, max_length=20)
    es_principal: Optional[bool] = None

    model_config = ConfigDict(str_strip_whitespace=True)


class RespuestaSucursalCreada(Revisar_Json_Crear_Sucursal):
    id: int
    activo: bool

    model_config = ConfigDict(from_attributes=True)


class RespuestaSucursalEditada(BaseModel):
    id: int
    id_empresa: int
    nombre: str
    direccion: str
    telefono: Optional[str]
    es_principal: bool
    activo: bool

    model_config = ConfigDict(from_attributes=True)
     
