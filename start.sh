#!/bin/bash
if [ -d frontend ]; then
    echo "Compilando..."
    cd frontend
    npm run dev
else
    echo "No encontre la carpeta frontend"
fi