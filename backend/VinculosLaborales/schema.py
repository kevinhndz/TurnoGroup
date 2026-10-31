from pydantic import BaseModel, ConfigDict, Field
from typing import List, Literal


class Revisar_Json_Crear_Vinculo_Laboral(BaseModel):
    id_usuario: int = Field(gt=0)
    id_empresa: int = Field(gt=0)
    rol: Literal["Gerente", "Administrador", "Mesero", "Cajero"]

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
    nombre_usuario: str | None = None
    correo_usuario: str | None = None
    activo: bool
    id: int
    id_usuario: int
    id_empresa: int
    rol: str

    model_config = ConfigDict(from_attributes=True)


class RespuestaVinculoLaboralDetalle(RespuestaVinculoLaboral):
    asignaciones_sucursales: List[RespuestaAsignacionSucursal] = Field(
        default_factory=list
    )


class Revisar_Json_Editar_Vinculo_Laboral(BaseModel):
    rol: Literal["Gerente", "Administrador", "Mesero", "Cajero"] | None = None
    activo: bool | None = None

    model_config = ConfigDict(extra="forbid")
