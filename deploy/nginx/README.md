# HTTPS para TurnoGroup

El archivo `turnogroup.conf.example` es una plantilla para el Nginx externo. Reemplace el dominio y las rutas de certificado, pruebe la configuracion con `nginx -t` y recargue Nginx. El certificado debe ser valido para el dominio publico. Nginx debe ser la unica entrada publica. Los contenedores frontend (puerto 3000) y backend (puerto 8000) deben estar solo en la red privada, sin `ports` publicados a Internet. Si alguien llega por HTTP directo a Next, podria aparentar el dominio publico y hacer que Next firme una solicitud insegura.

En el entorno del frontend configure `PUBLIC_ORIGIN=https://turnos.example`, `BACKEND_URL=http://backend:8000` y un `BACKEND_PROXY_SECRET` aleatorio y largo. Configure el mismo secreto solo en el backend. En el backend configure `COOKIE_SEGURA=true`, `ORIGENES_PERMITIDOS=["https://turnos.example"]` y `URL_FRONTEND=https://turnos.example`. No ponga el secreto en variables `NEXT_PUBLIC_*`, en el navegador ni en Git.

El proxy de Next compara Host y Origin con `PUBLIC_ORIGIN`, reenvia el origen si existe y envia `X-Forwarded-Proto` y su secreto al backend. FastAPI solo acepta el HTTPS reenviado si el secreto coincide. Nginx reemplaza las cabeceras del proxy para que el navegador no pueda imponer sus propios valores.

Compruebe desde el dominio HTTPS que registro e inicio de sesion devuelven una cookie `Secure`, `HttpOnly` y `SameSite=Lax`. Una solicitud directa por HTTP al backend con `X-Forwarded-Proto: https` pero sin el secreto debe recibir 400. Una solicitud con Host u Origin ajeno al dominio debe recibir 403 en Next. Para probar TLS de extremo a extremo se necesita el dominio y certificado reales; este repositorio no configura el servidor Nginx en produccion.
