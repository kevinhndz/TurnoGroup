from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr
from typing import Optional


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
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)


class Revisar_Json_Editar_Usuario(BaseModel):
    estado: Optional[bool] = None
    correo: Optional[EmailStr] = None
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
