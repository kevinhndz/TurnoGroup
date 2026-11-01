from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr
from backend.Usuarios.schema import NuevoUsuarioRespuesta


class Revisar_Json_Iniciar_Sesion(BaseModel):
    reactivar: bool = False
    correo: EmailStr
    clave: SecretStr = Field(min_length=1, max_length=128)

    model_config = ConfigDict(extra="forbid")


class RespuestaSesion(BaseModel):
    usuario: NuevoUsuarioRespuesta
    vencimiento: datetime
    id_empresa: int | None = None
    id_sucursal: int | None = None
    rol_empresa: str | None = None
    mesas_habilitadas: bool = False
    reservas_habilitadas: bool = False
    finanzas_habilitadas: bool = False


class RespuestaMensaje(BaseModel):
    detail: str


class Revisar_Json_Seleccionar_Contexto(BaseModel):
    id_vinculo_laboral: int = Field(gt=0)
    id_sucursal: int | None = Field(default=None, gt=0)

    model_config = ConfigDict(extra="forbid")
