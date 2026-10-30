#!/bin/bash

# Existe un archivo llamado main.py aqui donde estoy?
if [ -f main.py ]; then
    echo "Ejecutando Uvicorn..."
    source venv/bin/activate
    uvicorn main:app --reload
else
    echo "No encontre el archivo main.py"
fi