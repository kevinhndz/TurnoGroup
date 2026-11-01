import os
from pathlib import Path
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
    URL_FRONTEND: str = "http://localhost:3000"
    SMTP_SERVIDOR: str = ""
    SMTP_PUERTO: int = 587
    SMTP_USUARIO: str = ""
    SMTP_CLAVE: str = ""
    SMTP_REMITENTE: str = ""
    SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


raiz = Path(__file__).resolve().parents[1]
cabeza = raiz / ".git" / "HEAD"
rama_pruebas = cabeza.is_file() and cabeza.read_text().strip().endswith(
    "/pruebas-frontend"
)
archivo_entorno = os.environ.get("TURNO_ENV")
if archivo_entorno is None:
    archivo_entorno = ".env.pruebas" if rama_pruebas else ".env"
    if rama_pruebas and not (raiz / archivo_entorno).is_file():
        raise RuntimeError(
            "Falta .env.pruebas. No se permite usar la base de main en la rama de pruebas"
        )
revision = GuardiaSeguridad(_env_file=raiz / archivo_entorno)
if rama_pruebas:
    from sqlalchemy.engine import make_url

    destino = make_url(revision.DATABASE_URL)
    if destino.get_backend_name() != "sqlite" and not (
        destino.host in ("127.0.0.1", "localhost")
        and destino.port == 55432
        and (
            destino.database == "turnogroup_pruebas"
            or (destino.database or "").endswith("_pytest")
        )
    ):
        raise RuntimeError(
            "La rama de pruebas solo puede usar PostgreSQL local de pruebas"
        )


"""

Pydantic con BaseSettings actua como un contrato estricto: si falta un dato o viene mal tipeado por error humano, la app se niega a iniciar 
y te dice exactamente que falta. Garantiza que si el sistema arranco, tenemos 100% de seguridad de que la configuracion es correcta.

Evita que al arrancar hayan problemas porque falto "algo" ese "algo" pasa por revision 

"""
