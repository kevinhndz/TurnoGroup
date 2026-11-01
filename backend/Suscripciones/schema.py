from pydantic import BaseModel, ConfigDict, Field, model_validator, SecretStr
from typing import Literal
from core.operaciones import ahora


class Revisar_Json_Plan(BaseModel):
    finanzas_habilitadas: bool
    model_config = ConfigDict(extra="forbid")


class Revisar_Json_Tarjeta_Suscripcion(BaseModel):
    tarjeta_prueba: Literal["visa", "mastercard", "amex"]
    titular: str = Field(min_length=1, max_length=100)
    mes: int = Field(ge=1, le=12)
    anio: int = Field(ge=2026, le=2100)
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @model_validator(mode="after")
    def revisar_vencimiento(self):
        fecha = ahora()
        if (self.anio, self.mes) < (fecha.year, fecha.month):
            raise ValueError("La tarjeta esta vencida")
        return self


class Revisar_Json_Renovacion(BaseModel):
    renovacion_automatica: bool
    model_config = ConfigDict(extra="forbid")


class Revisar_Json_Desactivar_Cuenta(BaseModel):
    clave: SecretStr = Field(min_length=1, max_length=128)
    confirmacion: Literal["DESACTIVAR"]
    model_config = ConfigDict(extra="forbid")
