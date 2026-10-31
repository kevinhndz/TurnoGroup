from pathlib import Path
import os
import secrets
import subprocess
import tempfile

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

raiz = Path(__file__).resolve().parent
rama = subprocess.check_output(
    ["git", "branch", "--show-current"], cwd=raiz, text=True
).strip()
if rama != "pruebas-frontend":
    raise SystemExit("Ejecuta este archivo solamente en la rama pruebas-frontend")

carpeta = Path.home() / ".local/share/turnogroup-postgres"
binarios = carpeta / "binarios"
programas = binarios / "usr/lib/postgresql/18/bin"
carpeta.mkdir(parents=True, exist_ok=True)
if not (programas / "pg_ctl").exists():
    with tempfile.TemporaryDirectory() as temporal:
        subprocess.run(
            ["apt-get", "download", "postgresql-18", "postgresql-client-18", "libpq5"],
            cwd=temporal,
            check=True,
        )
        for paquete in Path(temporal).glob("*.deb"):
            subprocess.run(["dpkg-deb", "-x", str(paquete), str(binarios)], check=True)

entorno = os.environ.copy()
entorno["LD_LIBRARY_PATH"] = str(binarios / "usr/lib/x86_64-linux-gnu")
configuracion = raiz / ".env.pruebas"
if not configuracion.exists():
    clave = secrets.token_urlsafe(32)
    url = f"postgresql+psycopg://turno:{clave}@127.0.0.1:55432/turnogroup_pruebas"
    configuracion.write_text(
        f"DATABASE_URL={url}\nSECRET_KEY={secrets.token_urlsafe(48)}\nCOOKIE_SEGURA=false\nALTA_PUBLICA_HABILITADA=true\n"
    )
    configuracion.chmod(0o600)
else:
    from dotenv import dotenv_values

    url = dotenv_values(configuracion)["DATABASE_URL"]
destino = make_url(url)
if (
    destino.host != "127.0.0.1"
    or destino.port != 55432
    or destino.database != "turnogroup_pruebas"
):
    raise SystemExit(".env.pruebas debe apuntar al PostgreSQL local de pruebas")

if not (carpeta / "datos/PG_VERSION").exists():
    with tempfile.NamedTemporaryFile(mode="w") as archivo:
        archivo.write(destino.password)
        archivo.flush()
        subprocess.run(
            [
                str(programas / "initdb"),
                "-D",
                str(carpeta / "datos"),
                "-U",
                "turno",
                "--auth-host=scram-sha-256",
                "--auth-local=trust",
                f"--pwfile={archivo.name}",
            ],
            env=entorno,
            check=True,
        )
subprocess.run(["bash", str(raiz / "iniciar_bd_pruebas.sh")], check=True)
motor = create_engine(destino.set(database="postgres"), isolation_level="AUTOCOMMIT")
with motor.connect() as conexion:
    for nombre in ("turnogroup_pruebas", "turnogroup_pytest"):
        if not conexion.execute(
            text("SELECT 1 FROM pg_database WHERE datname=:nombre"), {"nombre": nombre}
        ).scalar():
            conexion.execute(text(f"CREATE DATABASE {nombre}"))
motor.dispose()
entorno["TURNO_ENV"] = ".env.pruebas"
entorno["DATABASE_URL"] = url
subprocess.run(
    [str(raiz / "venv/bin/alembic"), "upgrade", "head"],
    cwd=raiz,
    env=entorno,
    check=True,
)
print(
    "Base local preparada. Inicia el backend con ./iniciar.sh y el frontend con ./start.sh"
)
