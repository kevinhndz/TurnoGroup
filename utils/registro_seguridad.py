"""Registro propio con rotacion diaria; nunca registra datos de formularios."""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from core.config import revision


class ArchivoAuditoria(TimedRotatingFileHandler):
    def _open(self):
        descriptor = os.open(
            self.baseFilename, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600
        )
        return os.fdopen(descriptor, "a", encoding="utf-8")


def configurar_auditoria():
    registro = logging.getLogger("turnogroup.seguridad")
    registro.setLevel(logging.INFO)
    registro.propagate = False
    if any(
        handler.get_name() == "auditoria_turnogroup" for handler in registro.handlers
    ):
        return registro
    if revision.AUDITORIA_ARCHIVO:
        archivo = Path(revision.AUDITORIA_ARCHIVO)
        archivo.parent.mkdir(parents=True, exist_ok=True)
        handler = ArchivoAuditoria(
            archivo,
            when="midnight",
            utc=True,
            backupCount=revision.AUDITORIA_DIAS,
            encoding="utf-8",
        )
    else:
        handler = logging.StreamHandler()
    handler.set_name("auditoria_turnogroup")
    handler.setFormatter(logging.Formatter("%(asctime)sZ %(levelname)s %(message)s"))
    from time import gmtime

    handler.formatter.converter = gmtime
    registro.addHandler(handler)
    return registro
