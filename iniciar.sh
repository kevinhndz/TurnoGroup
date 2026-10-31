#!/bin/bash

# Existe un archivo llamado main.py aqui donde estoy?
if [ -f main.py ]; then
    source venv/bin/activate
    if [ "$(git branch --show-current)" = "pruebas-frontend" ]; then
        bash ./iniciar_bd_pruebas.sh || exit 1
        echo "Ejecutando backend de pruebas en el puerto 8010..."
        uvicorn main:app --reload --port 8010
    else
        echo "Ejecutando Uvicorn..."
        uvicorn main:app --reload
    fi
else
    echo "No encontre el archivo main.py"
fi
