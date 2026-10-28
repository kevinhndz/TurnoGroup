from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class Revisar_Json_Nuevo_Producto(BaseModel):
    id_empresa: int = Field(gt=0)
    id_categoria: Optional[int] = Field(default=None, gt=0)
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio: Decimal = Field(ge=0)

    model_config = ConfigDict(str_strip_whitespace=True)


class NuevoProductoRespuesta(BaseModel):
    id: int
    id_empresa: int
    id_categoria: Optional[int]
    nombre: str
    descripcion: Optional[str]
    precio: Decimal
    ruta_imagen: Optional[str]
    disponible: bool

    model_config = ConfigDict(from_attributes=True)


class Revisar_Json_Editar_Producto(BaseModel):
    id_categoria: Optional[int] = Field(default=None, gt=0)
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio: Optional[Decimal] = Field(default=None, ge=0)

    model_config = ConfigDict(str_strip_whitespace=True)
