export const runtime = 'nodejs';

const permitidas = new Set(['sesiones/iniciar', 'sesiones/actual', 'sesiones/cerrar']);

async function comunicar(request, { params }) {
  const { ruta } = await params;
  const camino = ruta.join('/');

  if (!permitidas.has(camino)) {
    return Response.json({ detail: 'Ruta no disponible' }, { status: 404 });
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
    const url = new URL(`/${camino}`, process.env.BACKEND_URL || 'http://127.0.0.1:8000');
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
