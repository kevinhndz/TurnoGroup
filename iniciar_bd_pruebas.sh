#!/bin/bash
set -e
raiz="$HOME/.local/share/turnogroup-postgres"
if [ ! -x "$raiz/binarios/usr/lib/postgresql/18/bin/pg_ctl" ]; then
    echo "Primero ejecuta: venv/bin/python preparar_pruebas.py"
    exit 1
fi
export LD_LIBRARY_PATH="$raiz/binarios/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
if ! "$raiz/binarios/usr/lib/postgresql/18/bin/pg_ctl" -D "$raiz/datos" status >/dev/null 2>&1; then
    "$raiz/binarios/usr/lib/postgresql/18/bin/pg_ctl" -D "$raiz/datos" -l "$raiz/postgres.log" -o '-p 55432 -h 127.0.0.1 -k /tmp' -w start
fi
