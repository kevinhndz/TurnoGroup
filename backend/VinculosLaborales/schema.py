from pydantic import BaseModel, ConfigDict, Field
from typing import List


class Revisar_Json_Crear_Vinculo_Laboral(BaseModel):
    id_usuario: int = Field(gt=0)
    id_empresa: int = Field(gt=0)
    rol: str = Field(min_length=2, max_length=40)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class Revisar_Json_Asignar_Sucursal(BaseModel):
    id_sucursal: int = Field(gt=0)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class RespuestaAsignacionSucursal(BaseModel):
    id: int
    id_vinculo_laboral: int
    id_sucursal: int

    model_config = ConfigDict(from_attributes=True)


class RespuestaVinculoLaboral(BaseModel):
    id: int
    id_usuario: int
    id_empresa: int
    rol: str

    model_config = ConfigDict(from_attributes=True)


class RespuestaVinculoLaboralDetalle(RespuestaVinculoLaboral):
    asignaciones_sucursales: List[RespuestaAsignacionSucursal] = Field(default_factory=list)
