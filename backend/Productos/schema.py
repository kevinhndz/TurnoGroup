from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class Revisar_Json_Nuevo_Producto(BaseModel):
    id_categoria: Optional[int] = Field(default=None, gt=0)
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio: Decimal = Field(ge=0, max_digits=10, decimal_places=2)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


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
    disponible: Optional[bool] = None
    id_categoria: Optional[int] = Field(default=None, gt=0)
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio: Optional[Decimal] = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class Revisar_Json_Imagen_Producto(BaseModel):
    contenido: str = Field(min_length=1, max_length=7_000_000)
    model_config = ConfigDict(extra="forbid")


class Revisar_Json_Importar_Productos(BaseModel):
    productos: list[Revisar_Json_Nuevo_Producto] = Field(min_length=1, max_length=1000)
    asignar_sucursal: bool = True
    model_config = ConfigDict(extra="forbid")
