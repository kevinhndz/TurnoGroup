import os
from pathlib import Path
from typing import Literal
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class GuardiaSeguridad(BaseSettings):

    ENTORNO: Literal["desarrollo", "pruebas", "produccion"] = "desarrollo"
    DATABASE_URL: str
    # Puedo indicar otra CA si el proveedor cambia su certificado.
    DATABASE_SSL_ROOT_CERT: str = ""
    ALGORITHM: Literal["HS256"] = "HS256"
    ALTA_PUBLICA_HABILITADA: bool = True
    COOKIE_SEGURA: bool = True
    # Solo Next conoce este valor; asi no confio en cabeceras falsas del cliente.
    BACKEND_PROXY_SECRET: str = ""
    SESION_HORAS: int = Field(default=8, ge=1, le=24)
    LIMITE_LOGIN: int = Field(default=5, ge=1, le=100)
    LIMITE_RECUPERACION: int = Field(default=3, ge=1, le=100)
    LIMITE_INVITACION: int = Field(default=10, ge=1, le=100)
    LIMITE_IMPORTACION: int = Field(default=10, ge=1, le=100)
    VENTANA_RATE_LIMIT_SEGUNDOS: int = Field(default=60, ge=10, le=3600)
    ORIGENES_PERMITIDOS: list[str] = ["http://localhost:3000"]
    URL_FRONTEND: str = "http://localhost:3000"
    SMTP_SERVIDOR: str = ""
    SMTP_PUERTO: int = 587
    SMTP_USUARIO: str = ""
    SMTP_CLAVE: str = ""
    SMTP_REMITENTE: str = ""
    FACTURACION_MODO: Literal["simulado", "paddle"] = "simulado"
    PADDLE_ENTORNO: Literal["sandbox", "production"] = "sandbox"
    PADDLE_API_KEY: str = ""
    PADDLE_CLIENT_TOKEN: str = ""
    PADDLE_WEBHOOK_SECRET: str = ""
    PADDLE_PRECIO_SUCURSAL: str = ""
    PADDLE_PRECIO_FINANZAS: str = ""
    SECRET_KEY: str

    @model_validator(mode="after")
    def revisar_produccion(self):
        if self.ENTORNO != "produccion":
            return self

        from urllib.parse import urlsplit
        from sqlalchemy.engine import make_url

        errores = []
        if not self.COOKIE_SEGURA:
            errores.append("COOKIE_SEGURA debe estar activada")
        for nombre in ("SECRET_KEY", "BACKEND_PROXY_SECRET"):
            if len(getattr(self, nombre)) < 32:
                errores.append(nombre + " debe contener al menos 32 caracteres")
        if self.SECRET_KEY == self.BACKEND_PROXY_SECRET:
            errores.append("Los secretos de aplicacion y proxy deben ser diferentes")
        for origen in [self.URL_FRONTEND, *self.ORIGENES_PERMITIDOS]:
            url = urlsplit(origen)
            if (
                url.scheme != "https"
                or not url.hostname
                or url.hostname in ("localhost", "127.0.0.1", "::1")
                or url.username
                or url.password
                or url.query
                or url.fragment
                or url.path not in ("", "/")
            ):
                errores.append("Los origenes de produccion deben ser dominios HTTPS")
        if self.URL_FRONTEND.rstrip("/") not in self.ORIGENES_PERMITIDOS:
            errores.append("URL_FRONTEND debe estar en ORIGENES_PERMITIDOS")
        if make_url(self.DATABASE_URL).get_backend_name() != "postgresql":
            errores.append("Produccion requiere PostgreSQL")
        for nombre in ("SMTP_SERVIDOR", "SMTP_USUARIO", "SMTP_CLAVE", "SMTP_REMITENTE"):
            if not getattr(self, nombre):
                errores.append(nombre + " es obligatorio en produccion")
        if errores:
            # Los mensajes nunca incluyen valores de secretos.
            raise ValueError("; ".join(errores))
        return self

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
