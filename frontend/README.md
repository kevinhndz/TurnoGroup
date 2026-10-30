# Landing page de Turno Group

Pagina de presentacion hecha con Next.js, React y JavaScript. Los estilos usan CSS y los componentes estan separados y formateados con Prettier.

## Abrir la pagina

Necesitas Node.js 20.9 o superior. Desde la carpeta del proyecto:

```bash
cd frontend
npm ci
npm run dev
```

Abre http://localhost:3000.

## Comandos

```bash
npm run build
npm start
npm run format
npm run format:check
```

`build` prepara la version de produccion y `start` la sirve. `format` ordena el codigo y `format:check` revisa su formato.

## Organizacion

- `app/page.js`: orden de las secciones.
- `app/layout.js`: idioma y metadatos.
- `app/globals.css`: estilos y adaptacion a celulares.
- `components/`: portada, menu, funciones, precios, calculadora y pie de pagina.
- `public/`: fotografia y fuentes locales.

## Alcance

Esta entrega contiene solamente la landing page, basada en la pantalla Gestion Presencial de Restaurantes de Turno Group.

La calculadora muestra el costo mensual despues de la prueba: 100 USD por sucursal y 30 USD por empresa si se incluye finanzas. No realiza cobros ni cambia suscripciones.

El registro, acceso, contacto y enlaces legales abren ventanas informativas porque sus flujos se implementaran despues. No se crean cuentas, no se envian datos ni se conecta al backend en esta entrega.

Al publicar, configura `NEXT_PUBLIC_SITE_URL` con la URL completa del dominio antes de ejecutar `npm run build`. En desarrollo los metadatos usan http://localhost:3000.
