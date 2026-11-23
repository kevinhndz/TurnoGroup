#!/bin/bash
set -e

cd "$(dirname "$0")"
export TURNO_ENV=.env.pruebas

bash ./iniciar_bd_pruebas.sh

echo "Ejecutando API con la base de pruebas en http://localhost:8000/docs"
exec ./venv/bin/python -m uvicorn main:app --reload --port 8000
