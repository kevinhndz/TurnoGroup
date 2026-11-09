export const runtime = 'nodejs';

const permitidas = new Map([
  ['sesiones/iniciar', 'POST'],
  ['sesiones/actual', 'GET'],
  ['sesiones/cerrar', 'POST'],
  ['recuperaciones-clave/solicitar', 'POST'],
  ['recuperaciones-clave/restablecer', 'POST'],
  ['usuarios/registro-negocio', 'POST'],
  ['categorias', 'GET,POST'],
  ['productos', 'GET,POST'],
  ['sucursales', 'GET,POST'],
]);
const colecciones = new Set(['categorias', 'productos', 'sucursales']);
function permisoCatalogo(camino) {
  const partes = camino.split('/');
  if (!['categorias', 'productos'].includes(partes[0]) || !/^\d+$/.test(partes[1] || ''))
    return null;
  if (partes.length === 2) return 'GET,PATCH';
  if (partes.length === 3 && partes[2] === 'desactivar') return 'POST';
  return null;
}

async function comunicar(request, { params }) {
  const { ruta } = await params;
  const camino = ruta.join('/');

  const permitidos = permitidas.get(camino) || permisoCatalogo(camino);
  if (!permitidos) {
    return Response.json({ detail: 'Ruta no disponible' }, { status: 404 });
  }
  if (!permitidos.split(',').includes(request.method)) {
    return Response.json(
      { detail: 'Metodo no permitido' },
      {
        status: 405,
        headers: { Allow: permitidos },
      },
    );
  }

  if (request.method !== 'GET') {
    const origen = request.headers.get('origin');
    if (
      request.headers.get('X-Solicitud') !== 'TurnoGroup' ||
      (origen && origen !== new URL(request.url).origin)
    ) {
      return Response.json({ detail: 'Solicitud no permitida' }, { status: 403 });
    }
  }

  try {
    const sufijo = colecciones.has(camino) ? '/' : '';
    const url = new URL(
      `/${camino}${sufijo}`,
      process.env.BACKEND_URL || 'http://127.0.0.1:8000',
    );
    const headers = new Headers({ 'X-Solicitud': 'TurnoGroup' });
    const cookie = request.headers
      .get('cookie')
      ?.split(';')
      .find((parte) => parte.trim().startsWith('sesion_turnogroup='));
    if (cookie) headers.set('cookie', cookie.trim());
    let body;
    if (request.method !== 'GET') {
      body = await request.text();
      if (body.length > 4096) {
        return Response.json({ detail: 'Solicitud demasiado grande' }, { status: 413 });
      }
      headers.set('content-type', 'application/json');
    }
    const respuesta = await fetch(url, {
      method: request.method,
      headers,
      body: body || undefined,
      cache: 'no-store',
      redirect: 'manual',
      signal: AbortSignal.timeout(15000),
    });
    if (respuesta.status >= 300 && respuesta.status < 400) {
      return Response.json(
        { detail: 'Ruta del servicio no disponible' },
        { status: 502 },
      );
    }
    const salida = new Headers({ 'Cache-Control': 'no-store' });
    salida.set(
      'content-type',
      respuesta.headers.get('content-type') || 'application/json',
    );
    for (const cookie of respuesta.headers.getSetCookie())
      salida.append('set-cookie', cookie);
    return new Response(respuesta.status === 204 ? null : await respuesta.arrayBuffer(), {
      status: respuesta.status,
      headers: salida,
    });
  } catch {
    return Response.json(
      { detail: 'No pudimos conectar con el backend.' },
      { status: 503 },
    );
  }
}

export const GET = comunicar;
export const POST = comunicar;
