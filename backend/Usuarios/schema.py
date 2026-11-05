from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr
from typing import Optional, Literal


class Revisar_Json_Nuevo_Usuario(BaseModel):
    clave: SecretStr = Field(min_length=12, max_length=128)
    correo: EmailStr
    nombre: str = Field(min_length=1, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class Revisar_Json_Registro_Negocio(BaseModel):
    correo: EmailStr
    clave: SecretStr = Field(min_length=12, max_length=128)
    nombre_usuario: str = Field(min_length=1, max_length=100)
    nombre_empresa: str = Field(min_length=4, max_length=45)
    direccion: str = Field(min_length=5, max_length=255)

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
