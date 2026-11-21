# Acceso a datos por Supabase

TurnoGroup usa PostgreSQL desde FastAPI. El frontend no usa Supabase Auth ni llama a REST o GraphQL de Supabase. Su cookie de sesion no autentica a los roles `anon` o `authenticated` de Supabase.

La auditoria de lectura del 20 de noviembre de 2026 encontro 29 tablas en `public` con permisos de lectura y escritura para `anon`, `authenticated` y `service_role`. La migracion `c4a0e4010001` retira los permisos existentes de tablas y secuencias en `public` y los permisos predeterminados del rol que ejecuta Alembic. No se ejecuta automaticamente sobre la base remota al abrir el PR. En el proyecto revisado, `supabase_admin` tambien tiene grants predeterminados y el usuario `postgres` no puede cambiarlos; por eso la opcion de exposicion automatica del Dashboard debe quedar desactivada.

Para cerrar tambien el endpoint administrado, en el proyecto Supabase abra **Integrations > Data API** y desactive **Enable Data API**. Desactive **Automatically expose new tables** si mantiene la API habilitada para otro uso. Revise que ninguna otra aplicacion dependa de ella antes del cambio. Esta opcion del Dashboard no se controla desde este repositorio.

Despues de aplicar la migracion con el usuario de Alembic, ejecute `python -m scripts.verificar_permisos_api` usando el entorno de la base que desea revisar. Debe terminar con codigo cero. Si hay funciones nuevas en `public`, la comprobacion avisara porque PostgreSQL suele permitir `EXECUTE` a `PUBLIC` por defecto; retire ese permiso de cada funcion antes de exponerla. No cree tablas, secuencias ni funciones nuevas para la Data API sin revisar sus grants y RLS.

Con la Data API desactivada, una llamada a `/rest/v1/<tabla>` con la clave publicable no debe devolver filas ni aceptar escrituras. La aplicacion debe seguir consultando la base mediante FastAPI. Esta prueba requiere la URL y clave publicable del proyecto y se realiza despues de cambiar la opcion del Dashboard.
