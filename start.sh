#!/bin/bash

if [ -d frontend ]; then
    echo "Encontre la carpeta frontend"
    cd frontend
    npm run dev
else
    echo "No encontre la carpeta frontend"
fi
