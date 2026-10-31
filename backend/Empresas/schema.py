from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class Revisar_Json_Nueva_Empresa(BaseModel):
    nombre: str = Field(min_length=4, max_length=45)
    tipo_negocio: str = Field(min_length=1, max_length=35)
    codigo_pais: str = Field(min_length=2, max_length=5)
    zona_horaria: str = Field(min_length=4, max_length=45)
    codigo_moneda: str = Field(min_length=2, max_length=5)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class NuevaEmpresaRespuesta(Revisar_Json_Nueva_Empresa):
    id: int
    estado: str
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)


class Revisar_Json_Editar_Empresa(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=4, max_length=45)
    tipo_negocio: Optional[str] = Field(default=None, min_length=1, max_length=35)
    codigo_pais: Optional[str] = Field(default=None, min_length=2, max_length=5)
    zona_horaria: Optional[str] = Field(default=None, min_length=4, max_length=45)
    codigo_moneda: Optional[str] = Field(default=None, min_length=2, max_length=5)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
