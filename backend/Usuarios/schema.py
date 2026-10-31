from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr
from typing import Optional, Literal
from backend.Empresas.schema import Revisar_Json_Nueva_Empresa
from backend.Sucursales.schema import Revisar_Json_Crear_Sucursal
from backend.Categorias.schema import Revisar_Json_Nueva_Categoria
from backend.Productos.schema import Revisar_Json_Nuevo_Producto
from backend.Descuentos.schema import Revisar_Json_Crear_Descuento
from backend.ConfiguracionImpuestos.schema import Revisar_Json_Crear_Configuracion_Impuestos



class Revisar_Json_Nuevo_Usuario(BaseModel):
    clave: SecretStr = Field(min_length=12, max_length=128)
    correo: EmailStr
    nombre: str = Field(min_length=1, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class NuevoUsuarioRespuesta(BaseModel):
    id: int
    correo: EmailStr
    nombre: str
    estado: bool
    rol_plataforma: str
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)


class Revisar_Json_Editar_Usuario(BaseModel):
    estado: Optional[bool] = None
    correo: Optional[EmailStr] = None
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class Revisar_Json_Rol_Plataforma(BaseModel):
    rol_plataforma: Literal["Usuario", "Superadministrador"]
    model_config = ConfigDict(extra="forbid")




class ServicioRegistro(BaseModel):
    habilitado: bool = False
    mesas_habilitadas: bool = False
    reservas_habilitadas: bool = False
    model_config = ConfigDict(extra="forbid")


class SucursalRegistro(Revisar_Json_Crear_Sucursal):
    id_local: int = Field(gt=0)
    servicios: dict[Literal["comer_aqui", "para_llevar", "domicilio"], ServicioRegistro]
    pagos: list[Literal["efectivo", "transferencia", "tarjeta"]] = Field(min_length=1, max_length=3)


class CategoriaRegistro(Revisar_Json_Nueva_Categoria):
    id_local: int = Field(gt=0)


class ProductoRegistro(Revisar_Json_Nuevo_Producto):
    sucursales: list[int] = Field(default_factory=list, max_length=100)


class Revisar_Json_Registro_Negocio(BaseModel):
    finanzas_habilitadas: bool = False
    cuenta: Revisar_Json_Nuevo_Usuario
    negocio: Revisar_Json_Nueva_Empresa
    sucursales: list[SucursalRegistro] = Field(min_length=1, max_length=100)
    categorias: list[CategoriaRegistro] = Field(default_factory=list, max_length=500)
    productos: list[ProductoRegistro] = Field(default_factory=list, max_length=1000)
    descuentos: list[Revisar_Json_Crear_Descuento] = Field(default_factory=list, max_length=100)
    impuesto: Revisar_Json_Crear_Configuracion_Impuestos | None = None
    model_config = ConfigDict(extra="forbid")
