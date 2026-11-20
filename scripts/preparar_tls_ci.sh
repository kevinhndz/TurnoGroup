#!/usr/bin/env bash
set -euo pipefail

# Preparo un certificado temporal solo para el PostgreSQL de Actions.
: "${CONTENEDOR_POSTGRES_CI:?Falta el contenedor de pruebas}"
: "${GITHUB_ENV:?Este archivo se ejecuta dentro de Actions}"
carpeta_tls=$(mktemp -d "${RUNNER_TEMP:-/tmp}/turnogroup-tls.XXXXXX")
openssl req -x509 -newkey rsa:2048 -nodes -days 1 \
  -subj '/CN=127.0.0.1' -addext 'subjectAltName=IP:127.0.0.1' \
  -keyout "$carpeta_tls/servidor.key" -out "$carpeta_tls/servidor.crt" 2>/dev/null

docker cp "$carpeta_tls/servidor.key" "$CONTENEDOR_POSTGRES_CI:/tmp/turnogroup-ci.key"
docker cp "$carpeta_tls/servidor.crt" "$CONTENEDOR_POSTGRES_CI:/tmp/turnogroup-ci.crt"
docker exec --user root "$CONTENEDOR_POSTGRES_CI" \
  chown postgres:postgres /tmp/turnogroup-ci.key /tmp/turnogroup-ci.crt
docker exec --user root "$CONTENEDOR_POSTGRES_CI" chmod 600 /tmp/turnogroup-ci.key

# Activo TLS sin tocar ninguna base externa ni usar credenciales reales.
docker exec --user postgres "$CONTENEDOR_POSTGRES_CI" \
  psql -U turno_ci -d turno_ci_pytest -v ON_ERROR_STOP=1 \
  -c "ALTER SYSTEM SET ssl_cert_file = '/tmp/turnogroup-ci.crt'" \
  -c "ALTER SYSTEM SET ssl_key_file = '/tmp/turnogroup-ci.key'" \
  -c "ALTER SYSTEM SET ssl = 'on'" \
  -c 'SELECT pg_reload_conf()'
printf 'TEST_DATABASE_SSL_ROOT_CERT=%s/servidor.crt\n' "$carpeta_tls" >> "$GITHUB_ENV"
