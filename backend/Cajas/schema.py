from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class Revisar_Json_Abrir_Caja(BaseModel):
    monto_inicial: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    model_config = ConfigDict(extra="forbid")


class Revisar_Json_Cerrar_Caja(BaseModel):
    efectivo_contado: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    nota: str | None = Field(default=None, max_length=500)
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
