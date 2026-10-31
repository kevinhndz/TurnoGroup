from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class GuardiaSeguridad(BaseSettings):

    DATABASE_URL: str
    ALGORITHM: Literal["HS256"] = "HS256"
    ALTA_PUBLICA_HABILITADA: bool = True
    COOKIE_SEGURA: bool = True
    SESION_HORAS: int = Field(default=8, ge=1, le=24)
    ORIGENES_PERMITIDOS: list[str] = ["http://localhost:3000"]
    SMTP_SERVIDOR: str = ""
    SMTP_PUERTO: int = 587
    SMTP_USUARIO: str = ""
    SMTP_CLAVE: str = ""
    SMTP_REMITENTE: str = ""
    SECRET_KEY : str



    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


revision = GuardiaSeguridad()


"""

Pydantic con BaseSettings actua como un contrato estricto: si falta un dato o viene mal tipeado por error humano, la app se niega a iniciar 
y te dice exactamente que falta. Garantiza que si el sistema arranco, tenemos 100% de seguridad de que la configuracion es correcta.

Evita que al arrancar hayan problemas porque falto "algo" ese "algo" pasa por revision 

"""