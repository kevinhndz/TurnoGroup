from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr


class Revisar_Json_Crear_Invitacion_Laboral(BaseModel):
    correo: EmailStr
    rol: Literal["Gerente", "Administrador", "Mesero"]
    sucursales: list[int] = Field(default_factory=list, max_length=100)

    model_config = ConfigDict(extra="forbid")


class Revisar_Json_Aceptar_Invitacion_Laboral(BaseModel):
    codigo: SecretStr = Field(min_length=40, max_length=128)

    model_config = ConfigDict(extra="forbid")


class RespuestaInvitacionLaboral(BaseModel):
    id: int
    correo: str
    id_empresa: int
    rol: str
    vencimiento: datetime
    fecha_aceptacion: datetime | None
    fecha_revocacion: datetime | None
    sucursales: list[int]


class Revisar_Json_Registro_Invitacion(Revisar_Json_Aceptar_Invitacion_Laboral):
    nombre: str = Field(min_length=1, max_length=100)
    clave: SecretStr = Field(min_length=12, max_length=128)
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
