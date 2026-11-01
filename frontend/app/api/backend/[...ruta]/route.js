import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

export const runtime = 'nodejs';

const colecciones = new Set([
  'bitacora',
  'usuarios',
  'pedidos',
  'reservas',
  'cajas',
  'empresas',
  'categorias',
  'productos',
  'sucursales',
  'mesas',
  'configuracion-impuestos',
  'descuentos',
  'vinculos-laborales',
  'invitaciones-laborales',
  'tipos-servicio',
  'metodos-pago',
  'servicios-sucursales',
  'pagos-sucursales',
  'disponibilidad-productos',
]);

async function comunicar(request, { params }) {
  const { ruta } = await params;

  if (!ruta?.length || ruta.some((parte) => !/^[a-z0-9_-]+$/i.test(parte))) {
    return Response.json({ detail: 'Ruta no válida' }, { status: 400 });
  }

  const escritura = !['GET', 'HEAD'].includes(request.method);
  const origen = request.headers.get('origin');

  if (
    escritura &&
    (request.headers.get('X-Solicitud') !== 'TurnoGroup' ||
      (origen &&
        origen !== `${new URL(request.url).protocol}//${request.headers.get('host')}`))
  ) {
    return Response.json({ detail: 'Solicitud no permitida' }, { status: 403 });
  }

  try {
    let pruebas = false;
    try {
      pruebas = readFileSync(resolve(process.cwd(), '../.git/HEAD'), 'utf8')
        .trim()
        .endsWith('/pruebas-frontend');
    } catch {}
    const base =
      process.env.BACKEND_URL ||
      (pruebas ? 'http://127.0.0.1:8010' : 'http://127.0.0.1:8000');
    const url = new URL(base);
    if (
      pruebas &&
      (!['127.0.0.1', 'localhost'].includes(url.hostname) || url.port !== '8010')
    ) {
      return Response.json(
        { detail: 'La rama de pruebas requiere el backend local del puerto 8010' },
        { status: 503 },
      );
    }
    const barra = ruta.length === 1 && colecciones.has(ruta[0]) ? '/' : '';
    url.pathname = `/${ruta.join('/')}${barra}`;
    url.search = new URL(request.url).search;

    const headers = new Headers({ 'X-Solicitud': 'TurnoGroup' });
    const cookie = request.headers
      .get('cookie')
      ?.split(';')
      .find((parte) => parte.trim().startsWith('sesion_turnogroup='));

    if (cookie) headers.set('cookie', cookie.trim());
    headers.set('X-Forwarded-Proto', new URL(request.url).protocol.replace(':', ''));

    let body;
    if (escritura) {
      body = await request.text();
      if (
        body.length >
        (ruta[0] === 'productos' && ruta.at(-1) === 'imagen'
          ? 7_100_000
          : ruta[0] === 'productos' && ruta.at(-1) === 'revisar-archivo'
            ? 1_400_000
            : 1_000_000)
      ) {
        return Response.json(
          { detail: 'La solicitud es demasiado grande' },
          { status: 413 },
        );
      }
      if (body) headers.set('content-type', 'application/json');
    }

    const respuesta = await fetch(url, {
      method: request.method,
      headers,
      body: body || undefined,
      cache: 'no-store',
      redirect: 'manual',
      signal: AbortSignal.timeout(20000),
    });

    const salida = new Headers({ 'Cache-Control': 'no-store' });
    const tipo = respuesta.headers.get('content-type');
    if (tipo) salida.set('content-type', tipo);
    const descarga = respuesta.headers.get('content-disposition');
    if (descarga) salida.set('content-disposition', descarga);
    for (const valor of respuesta.headers.getSetCookie())
      salida.append('set-cookie', valor);

    if (respuesta.status >= 300 && respuesta.status < 400) {
      return Response.json(
        { detail: 'La ruta del servicio no está disponible' },
        { status: 502 },
      );
    }

    return new Response(respuesta.status === 204 ? null : await respuesta.arrayBuffer(), {
      status: respuesta.status,
      headers: salida,
    });
  } catch {
    return Response.json(
      {
        detail:
          'No pudimos conectar con el servicio. Comprueba que el backend esté encendido.',
      },
      { status: 503 },
    );
  }
}

export const GET = comunicar;
export const POST = comunicar;
export const PATCH = comunicar;
export const DELETE = comunicar;
