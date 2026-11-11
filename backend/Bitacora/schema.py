from datetime import datetime
from pydantic import BaseModel


class RespuestaBitacora(BaseModel):
    id: int
    sucursal: str | None = None
    persona: str
    recurso: str
    id_registro: int
    cliente: str | None = None
    accion: str
    fecha: datetime
