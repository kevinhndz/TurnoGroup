from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class Revisar_Json_Nueva_Categoria(BaseModel):
    id_empresa: int = Field(gt=0)
    nombre: str = Field(min_length=1, max_length=60)
    orden_presentacion: int = Field(default=1, ge=0)

    model_config = ConfigDict(str_strip_whitespace=True)


class NuevaCategoriaRespuesta(BaseModel):
    id: int
    id_empresa: int
    nombre: str
    orden_presentacion: int
    activo: bool

    model_config = ConfigDict(from_attributes=True)


class Revisar_Json_Editar_Categoria(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=60)
    orden_presentacion: Optional[int] = Field(default=None, ge=0)

    model_config = ConfigDict(str_strip_whitespace=True)
