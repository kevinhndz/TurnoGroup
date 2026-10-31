from pydantic import BaseModel, ConfigDict


class RespuestaMetodoPago(BaseModel):
    id: int
    clave_concepto: str
    nombre_visible: str
    activo: bool

    model_config = ConfigDict(from_attributes=True)
