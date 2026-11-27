from decimal import Decimal, InvalidOperation
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class DatosMenu(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SolicitudMenuIA(DatosMenu):
    texto: str = Field(default="", max_length=12000)
    imagen: str = Field(default="", max_length=4_000_000)

    @model_validator(mode="after")
    def elegir_entrada(self):
        if bool(self.texto) == bool(self.imagen):
            raise ValueError("Envia una lista de texto o una imagen")
        return self


class ProductoExtraido(DatosMenu):
    # Todos los campos son obligatorios en el contrato del proveedor.
    nombre: str = Field(min_length=1, max_length=100)
    precio: str | None
    categoria: str | None = Field(max_length=60)
    descripcion: str | None = Field(max_length=500)
    evidencia: str = Field(max_length=300)
    advertencia: str | None = Field(max_length=300)

    @field_validator("precio")
    @classmethod
    def validar_precio(cls, valor):
        if valor is None:
            return None
        try:
            precio = Decimal(valor)
            if (
                not precio.is_finite()
                or precio < 0
                or precio > Decimal("99999999.99")
                or precio != precio.quantize(Decimal("0.01"))
            ):
                raise ValueError("Precio no valido")
        except (InvalidOperation, ValueError):
            raise ValueError("Precio no valido") from None
        return format(precio, ".2f")


class ExtraccionMenu(DatosMenu):
    productos: list[ProductoExtraido] = Field(max_length=100)
    advertencias: list[str] = Field(max_length=20)


class RevisionMenu(DatosMenu):
    productos: list[ProductoExtraido] = Field(min_length=1, max_length=100)


class ProductoConfirmado(DatosMenu):
    nombre: str = Field(min_length=1, max_length=100)
    precio: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    categoria: str | None = Field(default=None, max_length=60)
    descripcion: str | None = Field(default=None, max_length=500)
    accion: Literal["crear", "usar_existente"] = "crear"
    id_existente: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validar_accion(self):
        if self.accion == "crear" and (self.precio is None or self.id_existente):
            raise ValueError("Completa el precio del producto nuevo")
        if self.accion == "usar_existente" and self.id_existente is None:
            raise ValueError("Selecciona el producto existente")
        return self


class ConfirmacionMenu(DatosMenu):
    productos: list[ProductoConfirmado] = Field(min_length=1, max_length=100)
    asignar_sucursal: bool = True
