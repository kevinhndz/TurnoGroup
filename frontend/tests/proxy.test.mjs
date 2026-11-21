import assert from 'node:assert/strict';
import test from 'node:test';

import { POST } from '../app/api/backend/[...ruta]/route.js';

const parametros = { params: Promise.resolve({ ruta: ['sesiones', 'iniciar'] }) };

function solicitud(cabeceras = {}) {
  return new Request('http://interno/api/backend/sesiones/iniciar', {
    method: 'POST',
    headers: {
      host: 'turnos.example',
      origin: 'https://turnos.example',
      'X-Solicitud': 'TurnoGroup',
      ...cabeceras,
    },
    body: '{}',
  });
}

test('el proxy envia HTTPS y su secreto sin confiar en cabeceras del cliente', async () => {
  process.env.PUBLIC_ORIGIN = 'https://turnos.example';
  process.env.BACKEND_PROXY_SECRET = 'clave-de-prueba';
  process.env.BACKEND_URL = 'http://127.0.0.1:8000';
  const anterior = globalThis.fetch;
  let recibidas;
  globalThis.fetch = async (_url, opciones) => {
    recibidas = opciones.headers;
    return Response.json({ bien: true });
  };
  try {
    const respuesta = await POST(
      solicitud({ 'X-Forwarded-Proto': 'http', 'X-TurnoGroup-Proxy-Secret': 'falso' }),
      parametros,
    );
    assert.equal(respuesta.status, 200);
    assert.equal(recibidas.get('X-Forwarded-Proto'), 'https');
    assert.equal(recibidas.get('X-TurnoGroup-Proxy-Secret'), 'clave-de-prueba');
    assert.equal(recibidas.get('origin'), 'https://turnos.example');
  } finally {
    globalThis.fetch = anterior;
  }
});

test('el proxy rechaza otro dominio u origen', async () => {
  process.env.PUBLIC_ORIGIN = 'https://turnos.example';
  process.env.BACKEND_PROXY_SECRET = 'clave-de-prueba';
  assert.equal((await POST(solicitud({ host: 'otro.example' }), parametros)).status, 403);
  assert.equal(
    (await POST(solicitud({ origin: 'https://otro.example' }), parametros)).status,
    403,
  );
});

test('el proxy exige su secreto para el dominio HTTPS', async () => {
  process.env.PUBLIC_ORIGIN = 'https://turnos.example';
  delete process.env.BACKEND_PROXY_SECRET;
  assert.equal((await POST(solicitud(), parametros)).status, 503);
});
