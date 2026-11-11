from pathlib import Path
import os
import subprocess
from dotenv import dotenv_values
from sqlalchemy.engine import make_url

raiz = Path(__file__).resolve().parent
configuracion = raiz / ".env.pruebas"
if not configuracion.is_file():
    raise SystemExit("Primero ejecuta: venv/bin/python preparar_pruebas.py")
url = make_url(dotenv_values(configuracion)["DATABASE_URL"])
if url.host != "127.0.0.1" or url.port != 55432 or url.database != "turnogroup_pruebas":
    raise SystemExit("La configuracion debe usar la base local de pruebas")
subprocess.run(["bash", str(raiz / "iniciar_bd_pruebas.sh")], check=True)
entorno = os.environ.copy()
entorno["DATABASE_URL"] = url.set(database="turnogroup_pytest").render_as_string(
    hide_password=False
)
entorno["TURNO_ENV"] = ".env.pruebas"
subprocess.run(
    [str(raiz / "venv/bin/alembic"), "upgrade", "head"],
    cwd=raiz,
    env=entorno,
    check=True,
)
entorno["TEST_DATABASE_URL"] = entorno["DATABASE_URL"]
raise SystemExit(
    subprocess.run(
        [str(raiz / "venv/bin/pytest"), "-q"], cwd=raiz, env=entorno
    ).returncode
)
