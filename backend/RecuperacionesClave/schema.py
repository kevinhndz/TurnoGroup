from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr


class Revisar_Json_Solicitar_Recuperacion(BaseModel):
    correo: EmailStr

    model_config = ConfigDict(extra="forbid")


class Revisar_Json_Recuperar_Clave(BaseModel):
    codigo: SecretStr = Field(min_length=40, max_length=128)
    nueva_clave: SecretStr = Field(min_length=12, max_length=128)

    model_config = ConfigDict(extra="forbid")
