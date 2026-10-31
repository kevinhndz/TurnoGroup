from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class GuardiaSeguridad(BaseSettings):

    DATABASE_URL: str
    ALGORITHM: Literal["HS256"] = "HS256"
    SECRET_KEY : str



    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


revision = GuardiaSeguridad()


"""

Pydantic con BaseSettings actua como un contrato estricto: si falta un dato o viene mal tipeado por error humano, la app se niega a iniciar 
y te dice exactamente que falta. Garantiza que si el sistema arranco, tenemos 100% de seguridad de que la configuracion es correcta.

Evita que al arrancar hayan problemas porque falto "algo" ese "algo" pasa por revision 

"""