export class ErrorAPI extends Error {
  constructor(mensaje, estado, errores = []) {
    super(mensaje);
    this.estado = estado;
    this.errores = errores;
  }
}

const cache = new Map();
const pendientes = new Map();
let versionCache = 0;

export function limpiarCache() {
  versionCache += 1;
  cache.clear();
  pendientes.clear();
}

export async function api(ruta, opciones = {}) {
  const method = opciones.method || 'GET';
  if (method !== 'GET' && !ruta.startsWith('/pedidos/cotizar')) limpiarCache();
  const compartir = method === 'GET' && !opciones.signal;
  const guardar = compartir && !ruta.startsWith('/sesiones/actual');
  const clave = `${versionCache}:${ruta}`;
  if (guardar && cache.get(clave)?.hasta > Date.now())
    return structuredClone(cache.get(clave).datos);
  if (compartir && pendientes.has(clave))
    return structuredClone(await pendientes.get(clave));
  const version = versionCache;
  const solicitud = solicitar(ruta, opciones);
  if (compartir) pendientes.set(clave, solicitud);
  try {
    const datos = await solicitud;
    if (guardar && version === versionCache)
      cache.set(clave, {
        datos: structuredClone(datos),
        hasta:
          Date.now() + (/^\/(tipos-servicio|metodos-pago)/.test(ruta) ? 300000 : 15000),
      });
    return structuredClone(datos);
  } finally {
    pendientes.delete(clave);
  }
}

async function solicitar(
  ruta,
  { method = 'GET', body, signal, avisarSesion = true } = {},
) {
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
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new ErrorAPI('No hay conexión. Intenta nuevamente.', 0);
  }
  const datos =
    respuesta.status === 204 ? null : await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    if (respuesta.status === 401 && avisarSesion && typeof window !== 'undefined')
      window.dispatchEvent(new Event('sesion-vencida'));
    const fallo = new ErrorAPI(
      typeof datos?.detail === 'string'
        ? datos.detail
        : datos?.detail?.mensaje || 'No se pudo completar la solicitud.',
      respuesta.status,
      datos?.errores || [],
    );
    fallo.codigo = datos?.detail?.codigo;
    throw fallo;
  }
  return datos;
}

export async function listarTodo(ruta) {
  const separador = ruta.includes('?') ? '&' : '?';
  let pagina = 1;
  let salida = [];
  while (true) {
    const datos = await api(`${ruta}${separador}limite=100&pagina_actual=${pagina}`);
    salida = salida.concat(datos.data);
    if (pagina >= datos.total_paginas) return salida;
    pagina += 1;
  }
}

export function dinero(valor, moneda = 'HNL') {
  const importe = Number(valor || 0);
  try {
    return new Intl.NumberFormat('es-HN', { style: 'currency', currency: moneda }).format(
      importe,
    );
  } catch {
    return `${importe.toLocaleString('es-HN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${moneda}`;
  }
}

export function fechaLocal(valor) {
  if (!valor) return '—';
  return new Date(valor + (/Z$|[+-]\d\d:\d\d$/.test(valor) ? '' : 'Z')).toLocaleString(
    'es-HN',
  );
}
