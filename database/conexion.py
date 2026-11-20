from pathlib import Path
import ssl

import certifi
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError

RAIZ = Path(__file__).resolve().parents[1]
CA_SUPABASE = RAIZ / "database" / "certs" / "supabase-ca.crt"
HOSTS_LOCALES = {"localhost", "127.0.0.1", "::1"}


def preparar_url_bd(url: str, certificado_raiz: str = "") -> URL:
    try:
        destino = make_url(url)
    except (ArgumentError, ValueError):
        raise ValueError("DATABASE_URL no tiene un formato valido") from None

    if destino.get_backend_name() == "sqlite":
        return destino
    if destino.get_backend_name() != "postgresql":
        raise ValueError("La conexion debe usar PostgreSQL o SQLite")

    # No dejo que otros parametros cambien el servidor que acabo de revisar.
    if {"host", "hostaddr", "port", "service", "servicefile"} & destino.query.keys():
        raise ValueError(
            "Define el servidor y el puerto en DATABASE_URL, no en parametros"
        )
    if not destino.host or any(
        isinstance(valor, tuple) for valor in destino.query.values()
    ):
        raise ValueError("Define un solo servidor y un valor por parametro de conexion")

    host = destino.host.lower()
    modo = destino.query.get("sslmode")
    local = host in HOSTS_LOCALES
    if (
        local
        and not modo
        and not certificado_raiz
        and not destino.query.get("sslrootcert")
    ):
        # Mantengo las pruebas locales sin exigir un certificado de produccion.
        return destino
    if local and modo in ("disable", "allow", "prefer", "require", "verify-ca"):
        return destino
    if modo not in (None, "verify-full"):
        raise ValueError("PostgreSQL remoto requiere sslmode=verify-full")

    # Compruebo tanto la CA como el nombre del servidor, sin bajar a require.
    certificado = certificado_raiz or destino.query.get("sslrootcert")
    if not certificado:
        es_supabase = host.endswith((".supabase.com", ".supabase.co"))
        certificado = str(CA_SUPABASE) if es_supabase else certifi.where()
    archivo = Path(certificado).expanduser()
    if not archivo.is_absolute():
        archivo = RAIZ / archivo
    try:
        ssl.create_default_context(cafile=str(archivo))
    except (OSError, ssl.SSLError):
        raise ValueError(
            "El certificado raiz de PostgreSQL no existe o no es valido"
        ) from None

    minimo = destino.query.get("ssl_min_protocol_version", "TLSv1.2")
    if minimo not in ("TLSv1.2", "TLSv1.3"):
        raise ValueError("PostgreSQL requiere TLS 1.2 o superior")
    return destino.update_query_dict(
        {
            "sslmode": "verify-full",
            "sslrootcert": str(archivo),
            "ssl_min_protocol_version": minimo,
            "gssencmode": "disable",
        }
    )
