from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Revisar_Json_Crear_Reserva(BaseModel):
    id_mesa: int = Field(gt=0)
    cliente: str = Field(min_length=1, max_length=100)
    telefono: str | None = Field(default=None, max_length=30)
    personas: int = Field(gt=0, le=1000)
    inicio: datetime
    fin: datetime
    nota: str | None = Field(default=None, max_length=500)
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("inicio", "fin")
    @classmethod
    def normalizar_fecha(cls, fecha):
        if fecha.tzinfo is None:
            raise ValueError("Indica una fecha con zona horaria")
        return fecha.astimezone(timezone.utc).replace(tzinfo=None)

    @model_validator(mode="after")
    def validar_horario(self):
        if self.fin <= self.inicio:
            raise ValueError("El fin debe ser posterior al inicio")
        return self
