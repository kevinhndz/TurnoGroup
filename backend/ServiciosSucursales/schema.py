from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class Revisar_Json_Crear_Servicio_Sucursal(BaseModel):
    id_tipo_servicio: int = Field(gt=0)
    habilitado: bool = False
    mesas_habilitadas: bool = False
    reservas_habilitadas: bool = False

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class Revisar_Json_Editar_Servicio_Sucursal(BaseModel):
    habilitado: Optional[bool] = None
    mesas_habilitadas: Optional[bool] = None
    reservas_habilitadas: Optional[bool] = None

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class RespuestaServicioSucursal(BaseModel):
    id_sucursal: int
    id_tipo_servicio: int
    habilitado: bool
    mesas_habilitadas: bool
    reservas_habilitadas: bool

    model_config = ConfigDict(from_attributes=True)
