#!/bin/bash
set -e

cd "$(dirname "$0")/frontend"

echo "Ejecutando frontend en http://localhost:3000"
exec npm run dev -- --port 3000
