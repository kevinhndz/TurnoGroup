export async function api(ruta, { method = 'GET', body, signal } = {}) {
  let respuesta;
  try {
    respuesta = await fetch(`/api/backend${ruta}`, {
      method,
      headers: { 'Content-Type': 'application/json', 'X-Solicitud': 'TurnoGroup' },
      credentials: 'same-origin',
      cache: 'no-store',
      signal,
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
  } catch (fallo) {
    if (fallo.name === 'AbortError') throw fallo;
    throw new Error('No hay conexión. Intenta nuevamente.');
  }
  const datos =
    respuesta.status === 204 ? null : await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    const error = new Error(
      typeof datos?.detail === 'string'
        ? datos.detail
        : 'No se pudo completar la solicitud.',
    );
    error.estado = respuesta.status;
    throw error;
  }
  return datos;
}
