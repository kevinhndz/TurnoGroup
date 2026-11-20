# Certificado de PostgreSQL

`supabase-ca.crt` es el certificado raiz publico de Supabase Root 2021 CA. Se obtuvo del [enlace oficial de Supabase](https://supabase-downloads.s3-ap-southeast-1.amazonaws.com/prod/ssl/prod-ca-2021.crt); no contiene ninguna clave privada. Hay que revisar su vigencia y reemplazarlo cuando Supabase rote la CA.

Para otro proveedor, configure `DATABASE_SSL_ROOT_CERT` con la ruta de su CA de confianza. Una conexion remota usa `sslmode=verify-full`, verifica el nombre del servidor y exige TLS 1.2 como minimo. No incluya claves privadas en el repositorio.

En Supabase, active **Enforce SSL on incoming connections** en Database Settings. Esta opcion protege tambien el tramo del pooler hacia PostgreSQL y puede reiniciar la base brevemente. Despues, ejecute `python -m scripts.verificar_tls_bd` con el entorno de produccion configurado. El comando falla si no puede validar el certificado o si PostgreSQL informa que el tramo final no usa TLS.
