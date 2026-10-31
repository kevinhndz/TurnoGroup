from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class Revisar_Json_Crear_Pago_Sucursal(BaseModel):
    id_sucursal: int = Field(gt=0)
    id_metodo_pago: int = Field(gt=0)
    habilitado: bool = False


class Revisar_Json_Editar_Pago_Sucursal(BaseModel):
    habilitado: Optional[bool] = None


class RespuestaPagoSucursal(BaseModel):
    id_sucursal: int
    id_metodo_pago: int
    habilitado: bool

    model_config = ConfigDict(from_attributes=True)
