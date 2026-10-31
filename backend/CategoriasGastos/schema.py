from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class Revisar_Json_Crear_Categoria_Gasto(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class Revisar_Json_Editar_Categoria_Gasto(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    activo: Optional[bool] = None

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class RespuestaCategoriaGasto(BaseModel):
    id: int
    id_empresa: int
    nombre: str
    activo: bool

    model_config = ConfigDict(from_attributes=True)
